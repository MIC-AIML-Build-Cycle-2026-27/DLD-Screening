"""Fetch 20 small Zenodo WAV members with HTTP ranges and ZIP CRC checks.

Dataset: Kennedy et al. (2017), https://doi.org/10.5281/zenodo.200495,
CC BY 4.0. No individual ages are released. This is an audio pipeline demo.
"""
import argparse
import csv
import hashlib
import io
import json
import struct
import urllib.request
import urllib.error
import zipfile
import zlib
from pathlib import Path

URL = 'https://zenodo.org/records/200495/files/english_children.zip?download=1'
SIZE = 607539935


def byte_range(start, end):
    for attempt in range(3):
        try:
            request = urllib.request.Request(URL, headers={'Range': f'bytes={start}-{end}'})
            with urllib.request.urlopen(request, timeout=90) as response:
                if response.status != 206 or response.headers.get('Content-Range') != f'bytes {start}-{end}/{SIZE}':
                    raise ValueError('Server ignored range or archive version changed')
                chunks, remaining = [], end - start + 1
                while remaining:
                    chunk = response.read(min(65536, remaining))
                    if not chunk:
                        raise OSError('Incomplete range response')
                    chunks.append(chunk)
                    remaining -= len(chunk)
            return b''.join(chunks)
        except (OSError, urllib.error.URLError):
            if attempt == 2:
                raise


def inventory():
    tail = byte_range(SIZE - 100000, SIZE - 1)
    pos = tail.rfind(b'PK\x05\x06')
    if pos < 0:
        raise ValueError('Missing ZIP end record')
    fields = struct.unpack('<4s4H2LH', tail[pos:pos + 22])
    length, offset = fields[5:7]
    directory = byte_range(offset, offset + length - 1)
    end = struct.pack('<4s4H2LH', b'PK\x05\x06', 0, 0, fields[3], fields[4], length, 0, 0)
    with zipfile.ZipFile(io.BytesIO(directory + end)) as archive:
        return archive.infolist()


def extract(info):
    header = byte_range(info.header_offset, info.header_offset + 29)
    fields = struct.unpack('<4s5H3L2H', header)
    if fields[0] != b'PK\x03\x04' or fields[2] & 1:
        raise ValueError('Invalid or encrypted member')
    start = info.header_offset + 30 + fields[-2] + fields[-1]
    data = byte_range(start, start + info.compress_size - 1)
    if info.compress_type == zipfile.ZIP_DEFLATED:
        data = zlib.decompress(data, -15)
    elif info.compress_type != zipfile.ZIP_STORED:
        raise ValueError('Unsupported compression')
    if len(data) != info.file_size or zlib.crc32(data) != info.CRC:
        raise ValueError('Member failed size/CRC verification')
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-root', required=True, type=Path,
                        help='Local non-synced folder outside the public repository')
    args = parser.parse_args()
    root = args.data_root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    infos = inventory()
    candidates = sorted((i for i in infos if '/english_words_sentences/' in i.filename
                         and '/studio_mic/sentences/' in i.filename
                         and i.filename.endswith('.wav')), key=lambda i: i.filename)
    groups = {}
    for info in candidates:
        groups.setdefault(info.filename.split('/')[2].split('_')[0], []).append(info)
    if len(groups) < 10:
        raise ValueError('Unexpected archive structure')
    rows = []
    for child in sorted(groups)[:10]:
        if len(groups[child]) < 2:
            raise ValueError('Insufficient sentence files')
        for info in groups[child][:2]:
            recording = 'zenodo200495:' + hashlib.sha256(info.filename.encode()).hexdigest()[:16]
            relative = Path('raw') / (recording.replace(':', '_') + '.wav')
            target = root / relative
            target.parent.mkdir(exist_ok=True)
            if target.exists():
                data = target.read_bytes()
                if len(data) != info.file_size or zlib.crc32(data) != info.CRC:
                    raise ValueError('Cached member checksum mismatch')
            else:
                data = extract(info)
                target.write_bytes(data)
            rows.append({'child_id': 'zenodo200495:' + child, 'recording_id': recording,
                         'original_child_id': child, 'original_recording_id': info.filename,
                         'audio_path': relative.as_posix(),
                         'sha256': hashlib.sha256(data).hexdigest(), 'zip_crc32': info.CRC,
                         'prompt_text': Path(info.filename).stem.replace('_', ' ')})
            print('Verified member', len(rows), flush=True)
    with (root / 'download_manifest.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0])
        writer.writeheader()
        writer.writerows(rows)
    (root / 'acquisition.json').write_text(json.dumps({
        'url': URL, 'archive_size': SIZE, 'wav_members': sum(i.filename.endswith('.wav') for i in infos),
        'non_wav_files': [i.filename for i in infos if not i.is_dir() and not i.filename.endswith('.wav')],
        'downloaded_members': len(rows), 'participant_folders': len(groups),
        'selection': 'First ten sorted participant folders; first two sorted studio sentence files each',
        'verification': 'ZIP member CRC32 and size; local SHA256. Full archive MD5 NOT verified.'
    }, indent=2), encoding='utf-8')
    print('Local data root:', root)


if __name__ == '__main__':
    main()
