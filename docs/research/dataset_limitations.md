# Limitations, permissions and evaluation contract

## Scope

Chronological-age estimation is not language-development-age measurement. An age prediction gap does not establish DLD risk or diagnose a disorder. The prototype has no clinical validation. Language background, task, equipment, schooling and developmental variability can all affect speech.

## Permissions and storage

The public repository excludes audio, transcripts, individual participant metadata, demographic workbooks and credentials, consistent with SECURITY.md. Download local copies from original providers under their terms. Raw and processed WAVs stay in a non-synced local data folder. Do not upload them to hosted notebooks, ASR services, public Streamlit deployments or GitHub without verifying permission.

Zenodo sample attribution: Kennedy, J., Lemaignan, S., Montassier, C., Lavalade, P., Irfan, B., Papadopoulos, F., Senft, E., and Belpaeme, T. (2016), *Children speech recording (English, spontaneous speech + pre-defined sentences)*, v1, DOI [10.5281/zenodo.200495](https://doi.org/10.5281/zenodo.200495), CC BY 4.0. Related paper: *Child Speech Recognition in Human-Robot Interaction: Evaluations and Recommendations* (HRI 2017). Original WAVs are retained unchanged; optional mono/resampling derivatives have a separate transformation log. No denoising or amplitude normalization is performed.

OCSC attribution: Wagner et al. (2025), *The Ohio Child Speech Corpus*, Speech Communication 170, 103206; corpus DOI [10.21415/60TV-D669](https://doi.org/10.21415/60TV-D669). Follow [TalkBank access levels](https://talkbank.org/0share/access.html), [ground rules](https://talkbank.org/0share/rules.html) and [ethics](https://talkbank.org/0share/ethics.html). Registration and any additional corpus requirements still apply. The code does not circumvent login or accept terms for the user.

CHILDES-Aligned attribution: Zheng et al. (2026), *CHILDES-Aligned: A Curated Children's Speech Dataset via Multi-Model Timestamp Ensembling*, [arXiv:2607.03670](https://arxiv.org/abs/2607.03670); cite each included original corpus as well. Its explicit licence is CC BY-NC-SA 4.0. Access and identity verification remain outstanding.

Other candidates retain their own licences; a combined manifest does not create permission to redistribute their contents. Public code is subject to the repository's existing licence status, not automatically the data licence.

## Data quality

- Zenodo's sample selection is deterministic convenience sampling, not a representative population sample. Participant folder numbers are archive identities, not ages. All microphone and segmented/whole-file variants of a participant share one split group. Only one microphone and fixed-task recordings were selected here.
- Filename text represents an elicitation prompt. It is not verified speech and must not produce linguistic model features as if it were a manual transcript. Original audio can contain examiner speech, overlap or mispronunciation; decoding alone does not establish speech purity. Manual listening/annotation remains necessary.
- No missing age or clinical label is filled. An absent diagnosis does not mean typically developing. The Zenodo group mean 4.9 is never assigned to individuals.
- OCSC age-group counts describe the downloaded roster, not recording availability. Its exact-age decimal values are preserved without rounding; age_months is derived as age_years × 12. Original numeric values and precision notes remain in the local roster.
- CHAT conversion uses years + months/12 + days/365.2425, preserves the original string, rejects invalid notation, and does not infer missing birth dates. Day terms are approximate decimal-year conversion.
- Byte-identical duplicates are detected by SHA256. Near-duplicates, different encodings and overlapping segments require additional temporal/provenance checks and are not ruled out by hashes.

## Speaker-wise evaluation

Create a frozen child roster first. Namespace stable original child IDs by original corpus; use that ID as split_group. Establish cross-corpus aliases and family/session relationships where relevant before splitting. Every recording, session, clip and microphone variant from the same child belongs to one partition. Never split clips randomly.

Use grouped train/validation/test partitions with age coverage where sample size permits. Fit imputation, scaling, feature selection and model selection on training children only; tune using child-grouped validation. Balance training children only. The mean-age predictor must use the training target distribution and match the chosen child-versus-recording weighting. Report both recording-level metrics and child-level aggregated errors so prolific speakers do not dominate. Bootstrap children, not clips, for uncertainty. No automatic split or performance report is produced for the current zero-eligible-recording sample.

Compare acoustic-only, linguistic-only and combined models on the same eligible held-out cohort. If transcript availability differs, report the intersection cohort separately; never interpret different-cohort MAEs as modality gains. Keep source/task/language for auditing, not as shortcuts that expose the target. Check age by source and task, and use source-held-out tests only once multiple compatible sources exist.

## Feature research for handoff

Acoustic candidates: duration, voiced fraction, pause statistics, F0 distribution with reliability bounds, spectral summaries and MFCC aggregates. The current short repeated sentences are suitable for testing I/O, not validating developmental claims. Pitch failures, examiner speech and background noise must be flagged before modelling.

Linguistic candidates, only with verified child transcripts: word count, lexical diversity with length control, mean words per utterance and task-specific grammatical measures. Document CHAT cleaning decisions and retain raw text locally. Prompt complexity, task duration, transcript conventions and ASR errors can dominate these values. No linguistic features were falsely derived from the Zenodo prompt filenames.
