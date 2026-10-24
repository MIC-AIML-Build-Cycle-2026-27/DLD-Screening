from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import soundfile as sf

from src.data.ocsc_pipeline import parse_chat, run, scan, select


def fixture(root, rid='4001', age='4;01.27', media=None, name='Synthetic'):
    path = root / 'OCSC-dataset' / rid[0] / (rid + '.cha')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f'@ID:\teng|OCSC|CHI|{age}|male|||Target_Child||{name}|\n'
                    f'@Media:\t{media or rid}, audio\n@G:\tAlphabet\n'
                    '*CHI:\ttest . \x1510_100\x15\n', encoding='utf-8')
    return path


def audio(root, rid='4001'):
    path = root / 'audio' / (rid + '.wav')
    path.parent.mkdir(exist_ok=True)
    sf.write(path, np.sin(np.arange(1600) / 10) * .2, 16000)
    return path


def test_extract_age_media_and_privacy(tmp_path):
    row = parse_chat(fixture(tmp_path), tmp_path, b'fixture')
    assert row['age_original'] == '4;01.27'
    assert row['age_years'] == pytest.approx(4 + 1/12 + 27/365.2425)
    assert row['media_valid'] and row['child_utterances'] == 1
    assert row['timed_child_utterances'] == 1
    assert row['child_id'] == ''
    assert 'Synthetic' not in str(row)


@pytest.mark.parametrize('age', ['', '4;12.00', 'unknown', '4;01.99'])
def test_invalid_ages(tmp_path, age):
    row = parse_chat(fixture(tmp_path, age=age), tmp_path, b'fixture')
    assert not row['age_valid']


def test_missing_and_ambiguous_child(tmp_path):
    path = fixture(tmp_path)
    path.write_text('@Media:\t4001, audio\n', encoding='utf-8')
    assert not parse_chat(path, tmp_path, b'fixture')['age_valid']
    path = fixture(tmp_path)
    path.write_text(path.read_text() * 2)
    row = parse_chat(path, tmp_path, b'fixture')
    assert not row['age_valid'] and not row['media_valid']


def test_media_mismatch_and_missing_audio(tmp_path):
    fixture(tmp_path, media='different')
    frame, count = scan(tmp_path, b'fixture')
    assert count == 0 and not frame.iloc[0].pair_verified
    assert not frame.iloc[0].media_valid
    assert select(frame).empty


def test_full_audio_match_and_corruption(tmp_path):
    fixture(tmp_path)
    path = audio(tmp_path)
    frame, count = scan(tmp_path, b'fixture')
    assert count == 1 and frame.iloc[0].pair_verified
    assert frame.iloc[0].duration_seconds == pytest.approx(.1)
    path.write_bytes(b'broken wav')
    frame, _ = scan(tmp_path, b'fixture')
    assert frame.iloc[0].audio_available and not frame.iloc[0].pair_verified


def test_duplicate_recordings_and_audio(tmp_path):
    original = fixture(tmp_path)
    copy = original.parent / 'nested' / original.name
    copy.parent.mkdir()
    copy.write_bytes(original.read_bytes())
    audio(tmp_path)
    frame, _ = scan(tmp_path, b'fixture')
    assert frame.duplicate_recording.all() and not frame.pair_verified.any()


def test_name_is_only_hint_and_selection_avoids_repeat(tmp_path):
    fixture(tmp_path)
    fixture(tmp_path, rid='4002')
    frame, _ = scan(tmp_path, b'fixture')
    assert frame.child_id.eq('').all()
    assert frame.possible_repeat_identity.all()
    assert len(select(frame)) == 1


def test_explicit_identity_map_groups_recordings(tmp_path):
    fixture(tmp_path)
    fixture(tmp_path, rid='4002', name='Different synthetic name')
    mapping = tmp_path / 'private.csv'
    pd.DataFrame([{'recording_id': r, 'participant_id': 'approved-fixture-id',
                   'evidence': 'synthetic test provenance'} for r in ['4001', '4002']]).to_csv(mapping, index=False)
    frame, _ = scan(tmp_path, b'fixture', mapping)
    assert frame.child_id.nunique() == 1 and frame.child_id.ne('').all()
    assert len(select(frame)) == 1
    assert 'approved-fixture-id' not in frame.to_csv(index=False)


def test_conflicting_identity_map_rejected(tmp_path):
    fixture(tmp_path)
    path = tmp_path / 'private.csv'
    pd.DataFrame({'recording_id': ['4001', '4001'], 'participant_id': ['a', 'b'],
                  'evidence': ['test', 'test']}).to_csv(path, index=False)
    with pytest.raises(ValueError):
        scan(tmp_path, b'fixture', path)


def test_refuse_public_output(tmp_path):
    from src.data import ocsc_pipeline
    with pytest.raises(ValueError, match='outside'):
        run(tmp_path, Path(ocsc_pipeline.__file__).resolve().parents[2] / 'data/unsafe')


def test_duplicate_content_and_multiple_paths(tmp_path):
    fixture(tmp_path)
    fixture(tmp_path, rid='4002', name='Second synthetic')
    path = audio(tmp_path)
    (path.parent / '4002.wav').write_bytes(path.read_bytes())
    frame, _ = scan(tmp_path, b'fixture')
    assert frame.duplicate_audio.all() and not frame.pair_verified.any()
    nested = path.parent / 'nested'
    nested.mkdir()
    (nested / path.name).write_bytes(path.read_bytes())
    frame, _ = scan(tmp_path, b'fixture')
    assert frame.iloc[0].audio_status == 'ambiguous_multiple_audio_files'


def test_workbook_conflict_is_quarantined(tmp_path):
    fixture(tmp_path)
    audio(tmp_path)
    folder = tmp_path / 'research_evidence'
    folder.mkdir()
    pd.DataFrame({'ID': ['4001'], 'Exact Age': [5.0]}).to_excel(
        folder / 'ocsc_demo.xlsx', sheet_name='Demographic Data', index=False)
    frame, _ = scan(tmp_path, b'fixture')
    assert frame.iloc[0].age_valid
    assert not frame.iloc[0].pair_verified and select(frame).empty
