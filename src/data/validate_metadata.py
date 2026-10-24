"""Fail closed for age-model eligibility; validate local media without uploading."""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import soundfile as sf

from src.data.prepare_dataset import FIELDS, sha256


def local_path(root, value):
    if pd.isna(value) or not str(value).strip():
        raise ValueError('Missing path')
    path = Path(str(value))
    if path.is_absolute():
        raise ValueError('Paths must be relative to data root')
    target = (root / path).resolve()
    if not target.is_relative_to(root.resolve()):
        raise ValueError('Path escapes data root')
    return target


def validate(frame, root):
    missing = sorted(set(FIELDS) - set(frame))
    if missing:
        raise ValueError(f'Missing schema columns: {missing}')
    measurements = []
    hashes = {}
    duplicate_ids = frame.recording_id.duplicated(keep=False)
    for index, row in frame.iterrows():
        problems = []
        record = {'row': int(index), 'recording_id': row.recording_id}
        if pd.isna(row.recording_id) or not str(row.recording_id).strip() or duplicate_ids.loc[index]:
            problems.append('missing_or_duplicate_recording_id')
        for field in ('child_id', 'split_group', 'source', 'task', 'language', 'license'):
            if pd.isna(row[field]) or not str(row[field]).strip():
                problems.append('missing_' + field)
        if pd.notna(row.child_id) and row.child_id != row.split_group:
            problems.append('split_group_mismatch')
        age = pd.to_numeric(row.age_years, errors='coerce')
        if pd.isna(age) or not np.isfinite(age) or not 0 < age < 18:
            problems.append('missing_or_invalid_age')
        if pd.notna(row.age_months) and pd.notna(age) and not np.isclose(float(row.age_months), age * 12):
            problems.append('age_conversion_mismatch')
        try:
            audio = local_path(root, row.audio_path)
            data, rate = sf.read(audio, always_2d=True)
            if not len(data) or not np.isfinite(data).all():
                raise ValueError('empty_or_nonfinite_audio')
            digest = sha256(audio)
            record.update(duration_seconds=len(data) / rate, sample_rate=rate,
                          channels=data.shape[1], sha256=digest,
                          silent=bool(np.max(np.abs(data)) == 0),
                          clipping_fraction=float(np.mean(np.abs(data) >= .999)))
            if record['silent']:
                problems.append('silent_audio')
            if digest in hashes:
                problems.append('duplicate_file')
            hashes.setdefault(digest, []).append(index)
            for field in ('sample_rate', 'channels', 'duration_seconds'):
                if pd.notna(row[field]) and not np.isclose(float(row[field]), record[field], atol=.001):
                    problems.append('incorrect_' + field)
            if pd.notna(row.sha256) and row.sha256 != digest:
                problems.append('checksum_mismatch')
        except (OSError, ValueError, RuntimeError) as exc:
            problems.append('audio_error:' + str(exc))
        if str(row.transcript_available).lower() in ('true', '1'):
            try:
                if not local_path(root, row.transcript_path).is_file():
                    problems.append('missing_transcript_file')
            except ValueError as exc:
                problems.append('transcript_error:' + str(exc))
        if pd.notna(row.quality_flag) and str(row.quality_flag).strip() not in ('', 'verified'):
            problems.append('unresolved_quality_flag')
        record['problems'] = problems
        record['eligible_for_age_model'] = not problems
        measurements.append(record)
    # Quarantine every copy, including the first occurrence of duplicate content.
    for indices in hashes.values():
        if len(indices) > 1:
            for item in measurements:
                if item['row'] in indices:
                    item['eligible_for_age_model'] = False
                    if 'duplicate_file' not in item['problems']:
                        item['problems'].append('duplicate_file')
    return {'recordings': len(frame), 'children_with_ids': int(frame.child_id.nunique()),
            'eligible_recordings': sum(m['eligible_for_age_model'] for m in measurements),
            'missing_values': frame.isna().sum().to_dict(), 'records': measurements}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('metadata', type=Path)
    parser.add_argument('--data-root', required=True, type=Path)
    parser.add_argument('--report', required=True, type=Path)
    parser.add_argument('--require-eligible', action='store_true')
    args = parser.parse_args()
    report = validate(pd.read_csv(args.metadata), args.data_root)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print({k: report[k] for k in ('recordings', 'children_with_ids', 'eligible_recordings')})
    if args.require_eligible and (not report['recordings'] or report['eligible_recordings'] != report['recordings']):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
