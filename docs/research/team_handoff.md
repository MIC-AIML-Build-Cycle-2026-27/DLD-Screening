# Dataset handoff

Phase 2 continuation: see [OCSC processing](ocsc_processing.md) and [current aggregate audit](ocsc/audit_summary.json). The Review 1 results below are retained as a historical snapshot.

**Usable now: audio-processing demonstration and verified Ohio participant metadata. Not yet usable: supervised age-model training/evaluation.**

## Local files and joins

Set `MIC_DLD_DATA_ROOT` to a non-synced local folder. File paths in the recording manifest are relative to that folder, not the repository. Each teammate should obtain permitted media from the provider or an approved internal mechanism.

| Recipient | Inputs | Contract |
|---|---|---|
| Varsha | `unified_metadata.csv`, `raw/`, optional `processed/`, `transformations.json`, `validation_report.json` | 20 original 44.1-kHz mono files; optional 16-kHz mono float-WAV derivatives. Join `acoustic_features.csv` on unique `recording_id`. Retain quality flags; do not treat short clips as a training cohort. |
| Arnavi | `transcript_available`, `transcript_path`, `task`, `prompt_text` | All 20 verbatim transcripts are missing. `prompt_text` is an intended sentence only. Implement joins and missing-data handling now; extract linguistic features after verified transcripts arrive. |
| Shrinikhaythan / Sachithan | `ocsc_children.csv`, empty `eligible_metadata.csv`, comparison and limitations | Ohio has 303 age-labelled children but no acquired audio. No age baseline can yet be evaluated. Preserve child grouping and report MAE/RMSE only after eligibility checks pass. |

`unified_metadata.csv` includes the requested common columns plus age precision, original IDs, sample rate/channels/duration, licence, SHA256 and quality flags. Missing CSV cells are missing values, not zeros. `recording_id` identifies the source archive member; `child_id` and `split_group` namespace the archive's participant number. `original_recording_id` preserves archive provenance. Public commits include no participant rows.

## Reproduce locally (Python 3.12)

From the repository root, create a virtual environment and install `requirements.txt`. The run used Windows/Python 3.12.14. Use an absolute path outside cloud-synced folders for DATA_ROOT. The following shell-neutral commands assume that your environment's `python` is active:

```text
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
python -m src.data.acquire_demo --data-root DATA_ROOT
python -m src.data.build_demo_metadata --data-root DATA_ROOT
python -m src.data.validate_metadata DATA_ROOT/unified_metadata.csv --data-root DATA_ROOT --report DATA_ROOT/validation_report.json
```

The downloader requests only archive byte ranges, checks member size/CRC and records SHA256; it stops if the archive size/range response changes. It retries interrupted transfers and validates cached files. Do not claim the archive-wide MD5 has been checked.

Download the public [Ohio workbook](https://talkbank.org/childes/access/Eng-NA/0docs/OCSC-demo.xlsx) to DATA_ROOT, retaining the original file. Then:

```text
python -m src.data.prepare_dataset DATA_ROOT/ocsc_demo.xlsx DATA_ROOT/ocsc_children.csv
python -m src.data.audit_dataset --data-root DATA_ROOT --output docs/research/figures
python -m pytest -q
python -m ruff check .
```

Set environment variable `MIC_DLD_DATA_ROOT` before executing `notebooks/dataset_audit.ipynb` in a kernel with these dependencies. Run all cells; the notebook calls the same audit implementation and outputs aggregate figures. Do not display individual rows in public notebooks. `--require-eligible` on the validator deliberately returns nonzero for the current demo.

Optional audio conversion is `convert_audio(source, destination, sample_rate=16000)` in `src/data/prepare_dataset.py`. It preserves originals, averages channels if needed, uses polyphase resampling and writes floating-point WAV. Record the returned original/output hashes and method in a transformation log. Do not replace the raw-path metadata silently with a resampled path; use a separate feature-processing manifest.

## Immediate access handoff

Register/sign in to TalkBank and obtain a small OCSC sample with CHAT files and matching media. Verify IDs against the workbook, inspect child-only time spans for a common non-reading task, and select 10–20 recordings across independent children and ages. Confirm the full cohort is large enough before allocating held-out children. Keep each recording's task/source and raw age evidence.

Review 1 target from the supplied brief: dataset handoff 25–26 October, integration 28 October, demo freeze 30 October, review 31 October–3 November 2026. The three original project documents were not supplied, so confirm these against the updated plan when available.
