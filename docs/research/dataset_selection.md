# Review 1 dataset decision — 24 October 2026

**Primary: Ohio Child Speech Corpus (OCSC), conditional on authenticated audio/transcript access and verified participant joins. Backup: one identity-audited English source corpus within CHILDES-Aligned, also conditional on access. Neither is an acquired age-regression dataset yet.**

The completed feasibility sample is Zenodo 200495: 20 decoded recordings from 10 participant folders, 60.952 seconds, 44.1 kHz mono. All 20 lack individual ages and verbatim transcripts. There are **zero acquired recordings eligible for age-model evaluation**. No model was trained and no MAE/RMSE was invented.

## What was verified

- Eight candidates were compared across 27 fields in [CSV](../../data/metadata/dataset_comparison.csv) and [Markdown](dataset_comparison.md).
- OCSC's public [demographics workbook](https://talkbank.org/childes/access/Eng-NA/0docs/OCSC-demo.xlsx) has 303 unique IDs, no missing ages, and decimal ages 4.103–9.936. Its Coding Notes explicitly define Exact Age as decimal age. Decimal display precision does not prove measurement accuracy. Audio/CHAT links returned login HTML, not downloadable files.
- [CHILDES-Aligned](https://talkbank.org/childes/access/Derived/CHILDES-Aligned.html) independently confirms the previously quoted 501,880 clips, 413.3 hours and 49 corpora as publisher figures. These were not independently recounted. The advertised metadata-only ZIP contains CSV/JSONL and corpus documentation; the linked TalkBank archive requires access. Hugging Face exposes a file inventory with 97 General Parquet shards, but attempted file retrieval returned HTTP 401. Metadata fields and identity completeness remain untested.
- [Zenodo 200495](https://zenodo.org/records/200495) API specifies CC BY 4.0. The central directory contains 671 WAV members and no non-WAV metadata files. Twenty selected members passed uncompressed size and CRC32 checks; each has a local SHA256. The full archive MD5 was **not** verified: the slow full download was stopped in favour of byte-range extraction.
- [Pratham ReadNet](https://huggingface.co/datasets/PrathamOrgAI/ReadNet): the actual HI_Letters CSV has 8,783 rows and only `recordingserverurl` and `Transcribed Text`. No explicit individual-age or child-ID columns occur in that file. The wider collection's 200,000+ children must not be claimed as the released subset's independent sample size.

## Why Ohio

Its participant-age table and shared elicitation protocol make it more defensible than pooling heterogeneous corpora. Start with one common non-reading task after checking child speech boundaries and completion coverage. Reading tasks depend on literacy and participation; whole-session audio includes adult/robot speech and cannot be treated as child-only acoustics. Verify every join between workbook ID, CHAT participant, session and media filename before using any label.

Child identity must persist across sessions. `CHI` is a speaker role, not a globally unique person. A recording ID is not a child ID. For CHILDES-Aligned, create an explicit reviewed original-corpus-to-child crosswalk; corpus + session only is insufficient for longitudinal children. Quarantine unresolved identities. A chosen corpus must have enough independent children spanning ages, not merely many clips of a few children.

## Combination experiments

| Option | Decision and actual result |
|---|---|
| A: one corpus | Prefer OCSC; 303 metadata children, 0 acquired recordings. No fitted experiment yet. |
| B: age-balanced | Created a reproducible **metadata-only** list: seed 42, 26 randomly sampled children per completed-year group 4–8, 130 total. Original eligible roster has 260 children in that range. Recording counts for every group are currently zero. Do not use this preselected list as the final test design. Split the full cohort first, then balance training children only; retain natural held-out distribution. |
| C: multiple corpora | Rejected for Review 1. Ohio metadata and Zenodo audio represent different children and cannot be joined. ReadNet/ASER have language/task and age-label mismatches. CHILDES-Aligned may overlap original corpora, requiring provenance/child deduplication. |

Balancing reduces data and changes the target distribution. Retain the unbalanced baseline; compare child-level age coverage, task completion and relevant collection conditions before drawing conclusions. Do not use transcript length or label availability to cherry-pick test children.

## Scientific and project inconsistencies

1. The three named project documents were absent from this chat and checkout. Their contents and differences cannot be assessed. Dates and responsibilities follow the supplied brief provisionally. The foundation README still describes screening broadly; immediate work is chronological-age regression, not DLD diagnosis.
2. The brief describes Shrinikhaythan first as comparison/evaluation/SHAP and later as the modelling handoff recipient; Sachithan is ML/evaluation lead. Deliver the same data contract to both and let the updated work plan settle implementation ownership.
3. TalkBank's [general rules](https://talkbank.org/0share/rules.html) specify CC BY-NC-SA 3.0, whereas CHILDES-Aligned explicitly specifies 4.0. Preserve corpus-specific terms; do not relabel every TalkBank corpus as 4.0.
4. [ENNI's corpus page](https://talkbank.org/childes/access/Clinical-Eng/ENNI.html) says media are unavailable while exposing a media link; [DrivenData](https://drivendata.co/kidsasr) reports using ENNI audio. Resolve current access before selecting it.
5. DrivenData's ReadNet refers to a US early-literacy project; Pratham ReadNet is a distinct Indian dataset. Do not combine their licences, subjects or counts.

## Reproducible evidence levels

Publisher statements, downloaded-file inspection and measured local results are distinguished in the comparison. Unknowns are UNVERIFIED. Inclusion requires permitted audio, traceable chronological age, defensible child grouping and adequate independent children. A feasibility spike validates these requirements before scaling; this spike found a genuine access/label gap rather than a trainable dataset.
