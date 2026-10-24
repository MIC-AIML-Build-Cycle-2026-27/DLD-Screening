"""Synthetic unit fixtures are software tests, never research evidence."""
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import soundfile as sf

from src.data.prepare_dataset import FIELDS, chat_age, convert_audio, prepare_ocsc
from src.data.validate_metadata import local_path, validate


@pytest.mark.parametrize('value,expected', [('4;06', 4.5), ('2;00.29', 2 + 29 / 365.2425), ('0;06.00', .5)])
def test_chat_age(value, expected):
    assert chat_age(value) == pytest.approx(expected)


@pytest.mark.parametrize('value', ['4.6', '4;12', '4;03.32', '-1;02', 'unknown'])
def test_invalid_age(value):
    with pytest.raises(ValueError):
        chat_age(value)


def test_missing_age():
    assert chat_age(None) is None
    assert chat_age('') is None


def valid_fixture(root):
    sf.write(root / 'sample.wav', np.sin(np.arange(1600) / 10) * .2, 16000)
    row = dict.fromkeys(FIELDS)
    row.update(child_id='fixture:1', split_group='fixture:1', recording_id='fixture:r1',
               age_years=5., age_months=60., language='English', task='test', source='synthetic',
               license='test fixture', audio_path='sample.wav', transcript_available=False)
    return pd.DataFrame([row])


def test_missing_age_not_eligible(tmp_path):
    frame = valid_fixture(tmp_path)
    assert validate(frame, tmp_path)['eligible_recordings'] == 1
    frame.loc[0, 'age_years'] = None
    assert validate(frame, tmp_path)['eligible_recordings'] == 0


def test_duplicates_quarantine_both(tmp_path):
    frame = valid_fixture(tmp_path)
    second = frame.copy()
    second['recording_id'] = 'fixture:r2'
    report = validate(pd.concat([frame, second], ignore_index=True), tmp_path)
    assert report['eligible_recordings'] == 0
    assert all('duplicate_file' in row['problems'] for row in report['records'])


def test_group_and_path_integrity(tmp_path):
    frame = valid_fixture(tmp_path)
    frame.loc[0, 'split_group'] = 'wrong-child'
    assert validate(frame, tmp_path)['eligible_recordings'] == 0
    with pytest.raises(ValueError):
        local_path(tmp_path, '../escape.wav')
    with pytest.raises(ValueError):
        local_path(tmp_path, str(Path(tmp_path / 'sample.wav').resolve()))


def test_corrupt_audio(tmp_path):
    frame = valid_fixture(tmp_path)
    (tmp_path / 'sample.wav').write_text('not WAV')
    assert validate(frame, tmp_path)['eligible_recordings'] == 0


def test_conversion_preserves_original(tmp_path):
    frame = valid_fixture(tmp_path)
    source = tmp_path / frame.loc[0, 'audio_path']
    original = source.read_bytes()
    destination = tmp_path / 'converted.wav'
    convert_audio(source, destination, sample_rate=8000)
    assert source.read_bytes() == original
    info = sf.info(destination)
    assert info.samplerate == 8000 and info.frames == 800 and info.channels == 1
    with pytest.raises(ValueError):
        convert_audio(source, source)


def test_ocsc_rejects_duplicate_children(tmp_path):
    workbook = tmp_path / 'test.xlsx'
    pd.DataFrame({'ID': [4001, 4001], 'Exact Age': [4.2, 4.3], 'Age group': [4, 4]}).to_excel(
        workbook, sheet_name='Demographic Data', index=False)
    with pytest.raises(ValueError):
        prepare_ocsc(workbook, tmp_path / 'output.csv')


def test_archive_crc_rejects_tampering(monkeypatch):
    import struct
    from types import SimpleNamespace
    from src.data import acquire_demo
    header = struct.pack('<4s5H3L2H', b'PK\x03\x04', 20, 0, 0, 0, 0, 0, 3, 3, 0, 0)
    monkeypatch.setattr(acquire_demo, 'byte_range', lambda start, end: header if start == 0 else b'bad')
    info = SimpleNamespace(header_offset=0, compress_size=3, compress_type=0, file_size=3, CRC=0)
    with pytest.raises(ValueError, match='CRC'):
        acquire_demo.extract(info)
