"""Prepare local-only metadata. Never infer a child identity from a session ID."""
import argparse
import hashlib
import json
import re
from pathlib import Path

import pandas as pd

FIELDS = ['child_id', 'recording_id', 'age_years', 'language', 'task', 'source',
          'audio_path', 'transcript_path', 'corpus', 'original_child_id',
          'original_recording_id', 'age_months', 'age_original', 'age_precision',
          'duration_seconds', 'sample_rate', 'channels', 'transcript_available',
          'clinical_label', 'license', 'split_group', 'quality_flag', 'sha256']


def chat_age(value):
    """CHAT years;months[.days] -> decimal years; days use 365.2425/year.

    Missing stays missing. This approximation preserves original precision;
    it does not reconstruct birth dates or treat 4;06 as 4.06 years.
    """
    if value is None or pd.isna(value) or str(value).strip() == '':
        return None
    match = re.fullmatch(r'(\d+);(\d{1,2})(?:\.(\d{1,2}))?', str(value).strip())
    if not match:
        raise ValueError(f'Invalid CHAT age: {value}')
    years, months, days = match.groups()
    if not 0 <= int(months) <= 11 or (days is not None and not 0 <= int(days) <= 31):
        raise ValueError('Invalid CHAT month/day')
    return int(years) + int(months) / 12 + int(days or 0) / 365.2425


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def prepare_ocsc(workbook, output):
    """One row per participant, NOT a recording manifest. Drop unrelated demographics."""
    original = pd.read_excel(workbook, sheet_name='Demographic Data', dtype={'ID': str})
    required = {'ID', 'Exact Age', 'Age group'}
    if not required <= set(original):
        raise ValueError(f'Missing workbook fields: {required - set(original)}')
    ids = original['ID'].str.strip()
    age = pd.to_numeric(original['Exact Age'], errors='raise')
    if ids.isna().any() or ids.eq('').any() or ids.duplicated().any():
        raise ValueError('Missing or duplicate participant IDs')
    if age.isna().any() or not age.between(0, 18).all():
        raise ValueError('Missing or implausible age')
    result = pd.DataFrame({'child_id': 'OCSC:' + ids, 'original_child_id': ids,
                           'age_years': age, 'age_months': age * 12,
                           'age_original': original['Exact Age'],
                           'age_precision': 'publisher decimal years; measurement precision unverified',
                           'age_group': original['Age group'], 'source': 'OCSC',
                           'split_group': 'OCSC:' + ids})
    if not (result.age_years.astype(int) == result.age_group).all():
        raise ValueError('Age group disagrees with decimal age')
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output, index=False)
    return result


def convert_audio(source, destination, sample_rate=16000):
    """Optional mono conversion; retain original. No denoising or normalization."""
    import math
    import numpy as np
    import soundfile as sf
    from scipy.signal import resample_poly

    if Path(source).resolve() == Path(destination).resolve():
        raise ValueError('Refusing to overwrite original audio')
    signal, rate = sf.read(source, always_2d=True)
    if not len(signal) or not np.isfinite(signal).all():
        raise ValueError('Empty or non-finite audio')
    mono = signal.mean(axis=1)
    divisor = math.gcd(rate, sample_rate)
    if rate != sample_rate:
        mono = resample_poly(mono, sample_rate // divisor, rate // divisor)
    Path(destination).parent.mkdir(parents=True, exist_ok=True)
    sf.write(destination, mono, sample_rate, subtype='FLOAT')
    return {'original_sha256': sha256(source), 'output_sha256': sha256(destination),
            'original_rate': rate, 'output_rate': sample_rate,
            'original_channels': signal.shape[1], 'method': 'channel mean; polyphase resampling; float WAV'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('workbook', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    result = prepare_ocsc(args.workbook, args.output)
    print(json.dumps({'participants': len(result), 'age_min': result.age_years.min(),
                      'age_max': result.age_years.max()}))


if __name__ == '__main__':
    main()
