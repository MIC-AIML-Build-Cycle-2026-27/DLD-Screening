"""Local-only CHAT inventory, conservative identity checks and targeted selection."""
import argparse
from collections import Counter
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import secrets

import numpy as np
import pandas as pd
import soundfile as sf

from src.data.prepare_dataset import FIELDS, chat_age, sha256

MEDIA_FOLDER = 'https://media.talkbank.org/childes/Eng-NA/OCSC'


def token(value, key):
    return hmac.new(key, value.encode('utf-8'), hashlib.sha256).hexdigest()[:24]


def parse_chat(path, root, key):
    """Extract only needed fields; never serialize child names or complete ID tiers."""
    row = dict.fromkeys(FIELDS, '')
    row.update(recording_id=path.stem, original_recording_id=path.stem,
               transcript_path=path.relative_to(root).as_posix(), source='OCSC',
               corpus='OCSC', transcript_available=True, age_group=path.parent.name,
               identity_status='unresolved', child_id='', split_group='',
               license='TalkBank conditions; user must confirm permitted use',
               audio_available=False, audio_verified=False, pair_verified=False,
               media_valid=False, age_valid=False, identity_hint='',
               target_id_sanitized='', child_utterances=0, timed_child_utterances=0)
    problems = []
    try:
        text = path.read_text(encoding='utf-8-sig')
    except (OSError, UnicodeError):
        row['validation_status'] = 'transcript_unreadable'
        return row
    # CHAT continuation lines belong to the previous tier.
    text = re.sub(r'\r?\n[ \t]+', ' ', text)
    ids = [s.strip().split('|') for s in re.findall(r'^@ID:\s*(.*)$', text, re.M)]
    children = [x for x in ids if len(x) >= 8 and
                (x[2] == 'CHI' or x[7] == 'Target_Child')]
    if len(children) != 1:
        problems.append('missing_or_ambiguous_child_id')
    else:
        child = children[0]
        row['language'] = child[0]
        row['age_original'] = child[3]
        row['target_id_sanitized'] = '|'.join(child[:4]) + '|[remaining fields omitted]'
        try:
            age = chat_age(child[3])
            if age is None or not 0 < age < 18:
                raise ValueError('Missing/implausible age')
            row.update(age_years=age, age_months=age * 12, age_valid=True,
                       age_precision='CHAT days' if '.' in child[3] else 'CHAT months')
            if str(int(age)) != row['age_group']:
                problems.append('age_folder_mismatch')
        except ValueError:
            problems.append('missing_or_invalid_age')
        # A matching name is only a possible repeat, never proof of identity.
        if len(child) > 9 and child[9].strip():
            row['identity_hint'] = token(child[9].strip().casefold(), key)
        utterances = re.findall(r'^\*' + re.escape(child[2]) + r':(.*)$', text, re.M)
        row['child_utterances'] = len(utterances)
        row['timed_child_utterances'] = sum(
            bool(re.search(r'\x15\d+_\d+\x15', line)) for line in utterances)
    media = re.findall(r'^@Media:\s*(.*)$', text, re.M)
    row['media_id'] = ''
    if len(media) == 1:
        parts = [x.strip() for x in media[0].split(',')]
        if len(parts) >= 2 and re.fullmatch(r'[A-Za-z0-9_-]+', parts[0]) and parts[1] == 'audio':
            row['media_id'] = parts[0]
            row['media_valid'] = parts[0] == path.stem
    if not row['media_valid']:
        problems.append('missing_ambiguous_or_mismatched_media')
    tasks = re.findall(r'^@(?:G|BG):\s*(.*)$', text, re.M)
    # Only corpus-documented task labels are retained; other free text stays private.
    allowed = {'Alphabet', 'Numbers', 'Wug', 'ExpPictures', 'Reading', 'HowTo',
               'Howto', 'DescriptivePictures', 'EndTasks'}
    row['task'] = ';'.join(sorted(set(tasks) & allowed))
    row['validation_status'] = ';'.join(problems) or 'metadata_valid'
    return row


def verify_audio(path):
    """Decode all frames in bounded memory, not just the WAV header."""
    frames = 0
    peak = 0.0
    with sf.SoundFile(path) as stream:
        rate, channels, expected = stream.samplerate, stream.channels, stream.frames
        for block in stream.blocks(blocksize=65536, always_2d=True):
            if not np.isfinite(block).all():
                raise ValueError('nonfinite_audio')
            frames += len(block)
            peak = max(peak, float(np.max(np.abs(block))))
    if not frames or frames != expected or peak == 0:
        raise ValueError('empty_truncated_or_silent_audio')
    return dict(duration_seconds=frames / rate, sample_rate=rate, channels=channels,
                sha256=sha256(path), audio_verified=True)


def scan(root, key, participant_map=None):
    paths = sorted((root / 'OCSC-dataset').rglob('*.cha'))
    if not paths:
        raise ValueError('No CHAT transcripts found under OCSC-dataset')
    rows = [parse_chat(p, root, key) for p in paths]
    workbook = root / 'research_evidence' / 'ocsc_demo.xlsx'
    roster = {}
    if workbook.exists():
        table = pd.read_excel(workbook, sheet_name='Demographic Data', dtype={'ID': str})
        if table.ID.duplicated().any():
            raise ValueError('Duplicate IDs in demographics workbook')
        roster = table.set_index('ID')['Exact Age'].to_dict()
    for row in rows:
        reference = roster.get(row['recording_id'])
        row['workbook_age_years'] = reference if reference is not None else ''
        row['workbook_age_status'] = 'not_compared'
        if reference is not None and row['age_valid']:
            # A numeric-ID cross-check is not proof of participant identity.
            conflict = not np.isfinite(reference) or abs(reference - row['age_years']) > .02
            row['workbook_age_status'] = 'conflict_over_0.02_years' if conflict else 'within_0.02_years'
            if conflict:
                row['validation_status'] += ';workbook_age_conflict'
    counts = Counter(r['recording_id'] for r in rows)
    hints = Counter(r['identity_hint'] for r in rows if r['identity_hint'])
    mapping = {}
    if participant_map is not None:
        table = pd.read_csv(participant_map, dtype=str).fillna('')
        if not {'recording_id', 'participant_id', 'evidence'} <= set(table):
            raise ValueError('Participant map requires recording_id, participant_id, evidence')
        if table.recording_id.duplicated().any() or table.eq('').any().any():
            raise ValueError('Participant map has duplicate or missing entries')
        mapping = table.set_index('recording_id').to_dict('index')
    audio = {}
    for path in sorted((root / 'audio').rglob('*')):
        if path.is_file() and path.suffix.lower() == '.wav':
            audio.setdefault(path.stem, []).append(path)
    for row in rows:
        rid = row['recording_id']
        row['duplicate_recording'] = counts[rid] > 1
        row['possible_repeat_identity'] = bool(row['identity_hint'] and hints[row['identity_hint']] > 1)
        if rid in mapping:
            row['child_id'] = 'OCSC:' + token(mapping[rid]['participant_id'], key)
            row['split_group'] = row['child_id']
            row['identity_status'] = 'verified_from_user_supplied_evidence_map'
        row['audio_filename'] = row.get('media_id', '') + '.wav' if row.get('media_id') else ''
        matches = audio.get(row.get('media_id', ''), [])
        row['audio_available'] = bool(matches)
        row['audio_status'] = 'missing'
        if len(matches) > 1:
            row['audio_status'] = 'ambiguous_multiple_audio_files'
        elif len(matches) == 1:
            row['audio_path'] = matches[0].relative_to(root).as_posix()
            try:
                row.update(verify_audio(matches[0]))
                row['audio_status'] = 'decoded_all_frames'
            except (OSError, ValueError, RuntimeError):
                row['audio_status'] = 'decode_failed'
        row['pair_verified'] = bool(row['audio_verified'] and row['media_valid'] and
                                    row['age_valid'] and not row['duplicate_recording'] and
                                    row['validation_status'] == 'metadata_valid')
        row['quality_flag'] = 'identity_or_child_only_segmentation_pending'
    # Byte-identical media under different recording names is also quarantined.
    hashes = Counter(r['sha256'] for r in rows if r['sha256'])
    for row in rows:
        row['duplicate_audio'] = bool(row['sha256'] and hashes[row['sha256']] > 1)
        if row['duplicate_audio']:
            row['pair_verified'] = False
            row['audio_status'] = 'duplicate_audio_content'
    return pd.DataFrame(rows), sum(len(v) for v in audio.values())


def select(frame, per_group=3):
    candidates = frame.loc[frame.age_valid & frame.media_valid &
                           ~frame.duplicate_recording & ~frame.duplicate_audio &
                           frame.validation_status.eq('metadata_valid')].copy()
    candidates['age_years'] = pd.to_numeric(candidates.age_years)
    candidates = candidates.loc[candidates.age_years.between(4, 9, inclusive='left')]
    selected, seen = [], set()
    for age in range(4, 9):
        group = candidates.loc[candidates.age_group.eq(str(age))].sort_values(
            ['audio_verified', 'audio_available', 'recording_id'], ascending=[False, False, True])
        n = 0
        for index, row in group.iterrows():
            # Avoid known repeats and matching name hints, without asserting independence.
            identity = row.child_id or row.identity_hint
            if identity and identity in seen:
                continue
            selected.append(index)
            if identity:
                seen.add(identity)
            n += 1
            if n == per_group:
                break
    result = frame.loc[selected].copy()
    result['selection_reason'] = 'age coverage; prefer available audio; independence pending'
    result['media_folder_url'] = MEDIA_FOLDER
    result['download_status'] = np.where(result.audio_available, 'already_local', 'manual_download_pending')
    return result


def run(root, output, participant_map=None):
    root = root.resolve()
    output = output.resolve()
    repo = Path(__file__).resolve().parents[2]
    if output.is_relative_to(repo):
        raise ValueError('Participant outputs must be outside the public repository')
    output.mkdir(parents=True, exist_ok=True)
    keypath = output / '.identity.key'
    if not keypath.exists():
        keypath.write_bytes(secrets.token_bytes(32))
    frame, wavs = scan(root, keypath.read_bytes(), participant_map)
    chosen = select(frame)
    frame.to_csv(output / 'transcript_inventory.csv', index=False)
    chosen.to_csv(output / 'download_manifest.csv', index=False)
    frame.to_csv(output / 'unified_metadata.csv', index=False)
    ages = pd.to_numeric(frame.age_years, errors='coerce').dropna()
    summary = dict(transcripts_scanned=len(frame), valid_age_labels=int(frame.age_valid.sum()),
                   invalid_or_missing_ages=int((~frame.age_valid).sum()),
                   age_folder_mismatches=int(frame.validation_status.str.contains('age_folder_mismatch').sum()),
                   workbook_age_conflicts=int(frame.workbook_age_status.eq('conflict_over_0.02_years').sum()),
                   valid_media_references=int(frame.media_valid.sum()),
                   independently_identified_children=int(frame.loc[frame.child_id.ne(''), 'child_id'].nunique()),
                   identity_unresolved_recordings=int(frame.child_id.eq('').sum()),
                   possible_repeat_identity_recordings=int(frame.possible_repeat_identity.sum()),
                   duplicate_recording_rows=int(frame.duplicate_recording.sum()),
                   duplicate_audio_rows=int(frame.duplicate_audio.sum()),
                   wav_files_available=wavs, verified_pairs=int(frame.pair_verified.sum()),
                   missing_audio=int((~frame.audio_available).sum()),
                   selected_recordings=len(chosen),
                   selected_per_age_group=chosen.age_group.value_counts().sort_index().to_dict(),
                   transcripts_per_age_group=frame.age_group.value_counts().sort_index().to_dict(),
                   age_min=float(ages.min()) if len(ages) else None,
                   age_max=float(ages.max()) if len(ages) else None,
                   child_only_segments_created=0, eligible_for_age_model=0,
                   limitations=['Recording IDs and matching names do not prove independent children.',
                                'No verified participant map supplied unless explicitly configured.',
                                'Full-session WAV includes other speakers; segmentation remains planned.',
                                'Transcript media matching is metadata evidence, not voice identification.',
                                'TalkBank access and permitted-use conditions apply; no bulk download.'])
    (output / 'audit_summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    pd.DataFrame({'transcripts': frame.age_group.value_counts(),
                  'selected': chosen.age_group.value_counts()}).fillna(0).sort_index().to_csv(
                      output / 'age_groups.csv', index_label='age_group')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    bins = np.arange(np.floor(ages.min()), np.ceil(ages.max()) + .5, .5) if len(ages) else 10
    axes[0].hist(ages, bins=bins, color='#2563a6', edgecolor='white')
    axes[0].set(title='Transcript age labels', xlabel='Age in decimal years', ylabel='Transcripts')
    if not chosen.empty:
        chosen.age_group.value_counts().sort_index().plot.bar(ax=axes[1], rot=0, color='#167c80')
    axes[1].set(title='Targeted selection; identity pending', xlabel='Age group', ylabel='Recordings')
    fig.tight_layout()
    fig.savefig(output / 'age_distribution.png', dpi=160)
    plt.close(fig)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-root', type=Path, default=os.environ.get('MIC_DLD_DATA_ROOT'))
    parser.add_argument('--output', type=Path)
    parser.add_argument('--participant-map', type=Path)
    args = parser.parse_args()
    if args.data_root is None:
        parser.error('Provide --data-root or MIC_DLD_DATA_ROOT')
    output = args.output or args.data_root / 'processed' / 'ocsc'
    print(json.dumps(run(args.data_root, output, args.participant_map), indent=2))


if __name__ == '__main__':
    main()
