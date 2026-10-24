"""Decode acquired demo WAVs and build standardized, explicitly age-ineligible rows."""
import argparse
from pathlib import Path

import pandas as pd
import soundfile as sf

from src.data.prepare_dataset import FIELDS
from src.data.validate_metadata import local_path


def build(root):
    manifest = pd.read_csv(root / 'download_manifest.csv', dtype={'original_child_id': str})
    rows = []
    for _, item in manifest.iterrows():
        signal, rate = sf.read(local_path(root, item.audio_path), always_2d=True)
        row = dict.fromkeys(FIELDS)
        row.update(item.to_dict())
        row.update(age_years=None, age_months=None, age_original=None,
                   age_precision='individual age unavailable', source='Zenodo200495',
                   corpus='Plymouth-English-2016', language='English',
                   task='sentence_repetition', transcript_path=None,
                   transcript_available=False, duration_seconds=len(signal) / rate,
                   sample_rate=rate, channels=signal.shape[1], license='CC-BY-4.0',
                   split_group=item.child_id, quality_flag='missing_individual_age;prompt_not_transcript')
        rows.append(row)
    result = pd.DataFrame(rows)
    result.to_csv(root / 'unified_metadata.csv', index=False)
    result.iloc[:0].to_csv(root / 'eligible_metadata.csv', index=False)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-root', required=True, type=Path)
    args = parser.parse_args()
    frame = build(args.data_root)
    print({'recordings': len(frame), 'children': frame.child_id.nunique(),
           'duration_seconds': frame.duration_seconds.sum()})
