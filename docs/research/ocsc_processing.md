# OCSC local transcript and audio processing

Phase 2 extends the existing `chat_age`, standardized `FIELDS` and SHA256 helpers. Previous Review 1 research and Zenodo outputs are historical snapshots and are not regenerated.

## Reproduce after moving the workspace

Run from the `DLD-Screening` repository in PowerShell:

```powershell
$env:MIC_DLD_DATA_ROOT = (Resolve-Path '..').Path
& '..\.venv\Scripts\python.exe' -m src.data.ocsc_pipeline --data-root $env:MIC_DLD_DATA_ROOT
& '..\.venv\Scripts\python.exe' -m pytest -q
& '..\.venv\Scripts\python.exe' -m ruff check .
```

The data root contains `OCSC-dataset/` and `audio/`. Outputs default to `processed/ocsc/`. All manifest paths are relative to that root. Use `--output` for a different private directory; repository-local output is rejected. Keep the environment variable scoped to this project: the old Zenodo demo uses a separate data root.

The private outputs are `transcript_inventory.csv`, `unified_metadata.csv`, `download_manifest.csv`, `audit_summary.json`, `age_groups.csv`, `age_distribution.png` and `.identity.key`. Preserve the key between runs for stable pseudonyms; never publish it. Existing raw data is read only. Derived OCSC reports are refreshed on rerun. Full ID tiers and transcript text are never exported. The sanitized target-ID field retains only language, corpus, speaker code and original age.

## Identity and eligibility

A recording filename, age, sex or matching name does not establish independent children. By default `child_id` and `split_group` are blank and identity is unresolved. A keyed hash of the private name field identifies possible repeat-name groups solely for conservative selection, not for train/test splitting. Name collisions and spelling variation remain possible. HMAC pseudonyms are not anonymization; all participant rows remain private.

After establishing a documented recording-to-participant mapping from publisher metadata, provide a private CSV with `recording_id,participant_id,evidence` through `--participant-map`. The tool rejects missing fields and duplicate recording mappings, hashes participant IDs and groups repeated recordings together. Evidence is a user assertion that requires review; the program cannot independently verify it. No participant map has yet been established for the local corpus. The existing demographics workbook can inform that review, but coincident numeric IDs alone have not been promoted to verified identity.

A verified pair means valid age, matching transcript/media identifiers, nonduplicate recording and a fully decoded non-silent WAV. It does not prove voice identity, licensing approval or child-only speech. All current rows retain an unresolved quality flag, so the existing `validate_metadata` module excludes them from age-model eligibility. No clinical labels are inferred from corpus descriptions.

## Selection and manual acquisition

The manifest selects up to three recordings in each completed-year group 4–8, preferring already verified/local media, then recording ID order. Known participant repeats or matching private name hints are skipped. Independence is still provisional. Missing or invalid ages, mismatched media, duplicate recordings and duplicate audio are excluded.

Use the [official corpus page](https://talkbank.org/childes/access/Eng-NA/OCSC.html) and its [media folder](https://media.talkbank.org/childes/Eng-NA/OCSC). Sign in if requested, navigate the age folder and locate the exact `audio_filename` from the private manifest. Save selected WAV files under `audio/`. Direct per-file URLs have not been verified and are deliberately not invented. The media endpoint could not be inspected through the browser tool in this run, so no automated downloads were attempted. Confirm TalkBank's current permitted-use conditions before downloading or sharing. Cite Wagner et al. (2025), The Ohio Child Speech Corpus, Speech Communication 170, 103206, as requested by the corpus page. No open redistribution license is assumed.

## Planned child-only segmentation

The parser counts target-child tiers and tiers carrying CHAT media bullets (`\x15start_end\x15`). Segmentation is not implemented or claimed. Future extraction must retain the target-child speaker code, track `@G`/`@BG` task boundaries, validate start/end milliseconds against decoded audio duration, exclude overlap with investigators/robot speech and manually check a sample of boundaries. Select a common non-reading task before comparing ages. Preserve raw files and log source hashes, segment offsets and transformations. Assign train/test groups at verified child level before segmenting or fitting preprocessing.

The separate OCSC audit contains aggregate counts only when copied into `docs/research/ocsc/`. No raw audio, transcripts, names, private maps or participant rows belong in Git.

## Workbook cross-check

When `research_evidence/ocsc_demo.xlsx` is present, numeric recording IDs are compared with the existing demographic roster. Differences above 0.02 decimal years (about 7.3 days) are conservatively flagged and excluded from selection; this is a review threshold, not proof that either source is correct. Original CHAT ages remain unchanged. Syntactically valid labels are reported separately from folder or workbook inconsistencies. Numeric ID concordance is not promoted to verified participant identity.
