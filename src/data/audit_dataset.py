"""Aggregate-only EDA; distinguish child roster from decoded recording manifest."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.data.validate_metadata import validate


def audit(root, output):
    output.mkdir(parents=True, exist_ok=True)
    children = pd.read_csv(root / 'ocsc_children.csv')
    recordings = pd.read_csv(root / 'unified_metadata.csv')
    checks = validate(recordings, root)
    counts = children.groupby('age_group').child_id.nunique()
    preferred = children.loc[children.age_years.between(4, 9, inclusive='left')]
    target = int(preferred.groupby('age_group').size().min())
    balanced = pd.concat([group.sample(n=target, random_state=42)
                          for _, group in preferred.groupby('age_group')])
    balanced.to_csv(root / 'ocsc_balanced_children.csv', index=False)
    summary = {
        'ocsc': {'children': int(children.child_id.nunique()), 'rows': len(children),
                 'age_min': children.age_years.min(), 'age_max': children.age_years.max(),
                 'age_mean': children.age_years.mean(), 'age_groups': counts.to_dict(),
                 'missing_age': int(children.age_years.isna().sum()),
                 'duplicate_child_ids': int(children.child_id.duplicated().sum()),
                 'downloaded_recordings': 0,
                 'balanced_4_to_under9_children_per_age': target,
                 'balanced_4_to_under9_total': len(balanced)},
        'audio_demo': {'recordings': len(recordings), 'children': int(recordings.child_id.nunique()),
                       'missing_age': int(recordings.age_years.isna().sum()),
                       'missing_transcript': int(recordings.transcript_path.isna().sum()),
                       'missing_clinical_label': int(recordings.clinical_label.isna().sum()),
                       'duplicate_recording_ids': int(recordings.recording_id.duplicated().sum()),
                       'duplicate_audio_hashes': int(recordings.sha256.duplicated().sum()),
                       'duration_seconds': float(recordings.duration_seconds.sum()),
                       'duration_min': float(recordings.duration_seconds.min()),
                       'duration_max': float(recordings.duration_seconds.max()),
                       'sample_rates': sorted(recordings.sample_rate.unique().tolist()),
                       'channels': sorted(recordings.channels.unique().tolist()),
                       'eligible_recordings': checks['eligible_recordings'],
                       'languages': recordings.language.value_counts().to_dict(),
                       'tasks': recordings.task.value_counts().to_dict()},
        'limitations': ['OCSC is a participant roster, not an audio dataset acquired here.',
                       'Zenodo has no individual ages; do not train age regression on it.',
                       'No combined source-age association can be estimated from these disjoint inputs.',
                       'Balanced list is a metadata-only proposal, not an executable age experiment.']}
    (output / 'audit_summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    recordings.isna().sum().rename('missing').to_csv(output / 'missing_values.csv')
    recordings.duration_seconds.describe().to_csv(output / 'duration_summary.csv')
    pd.Series({'duplicate_recording_ids': summary['audio_demo']['duplicate_recording_ids'],
               'duplicate_audio_hashes': summary['audio_demo']['duplicate_audio_hashes'],
               'duplicate_ocsc_child_ids': summary['ocsc']['duplicate_child_ids']}).to_csv(output / 'duplicate_report.csv')
    plt.rcParams.update({'font.size': 11, 'axes.spines.top': False, 'axes.spines.right': False})
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    axes[0].hist(children.age_years, bins=np.arange(4, 10.01, .5), color='#2563a6', edgecolor='white')
    axes[0].set(xlabel='Chronological age (decimal years)', ylabel='Independent children', title='OCSC: metadata only')
    counts.plot.bar(ax=axes[1], color='#167c80', rot=0)
    axes[1].set(xlabel='Completed-year age group', ylabel='Independent children', title='Children per age group')
    for i, n in enumerate(counts):
        axes[1].text(i, n, str(n), ha='center', va='bottom')
    axes[1].set_ylim(0, counts.max() * 1.15)
    fig.suptitle(f'{len(children)} verified participant records; audio access still pending')
    fig.tight_layout()
    fig.savefig(output / 'age_distribution.png', dpi=160)
    plt.close(fig)
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    recordings.source.value_counts().plot.bar(ax=axes[0], color='#2563a6', rot=0)
    axes[0].set(title='Decoded recordings by source', ylabel='Recordings')
    recordings.language.value_counts().plot.bar(ax=axes[1], color='#167c80', rot=0)
    axes[1].set(title='Language', ylabel='Recordings')
    axes[2].hist(recordings.duration_seconds, bins=8, color='#cb8233', edgecolor='white')
    axes[2].set(title='Duration of original WAVs', xlabel='Seconds', ylabel='Recordings')
    fig.suptitle(f'Audio demo: {len(recordings)} recordings / {recordings.child_id.nunique()} children; '
                 f'{recordings.age_years.isna().sum()} ages missing')
    fig.tight_layout()
    fig.savefig(output / 'source_distribution.png', dpi=160)
    plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    age_groups = recordings.age_years.apply(lambda x: 'Age unavailable' if pd.isna(x) else str(int(x)))
    age_groups.value_counts().plot.bar(ax=axes[0], color='#cb8233', rot=0)
    axes[0].set(title='Recordings by age group', ylabel='Recordings')
    recordings.task.value_counts().plot.bar(ax=axes[1], color='#167c80', rot=0)
    axes[1].set(title='Task distribution', ylabel='Recordings')
    fig.tight_layout()
    fig.savefig(output / 'recording_age_task.png', dpi=160)
    plt.close(fig)
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-root', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.data_root, args.output), indent=2))
