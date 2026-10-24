# Validation record — 24 October 2026

- Python 3.12.14; direct dependency versions are in requirements.txt and requirements-dev.txt.
- `python -m pytest -q --tb=short`: **16 passed**. Fixtures are explicitly synthetic software tests, not research samples.
- `python -m ruff check .`: passed, including the notebook.
- Python source compilation and `git diff --check`: passed.
- Executed every cell of dataset_audit.ipynb against the real local inputs using nbclient. The executed notebook is a local deliverable; the public version has cleared outputs.
- 20 original WAVs fully decoded; 44,100 Hz mono; 60.951723 seconds total. Original and processed files remain separate. All 20 processed WAVs decoded at 16,000 Hz mono with duration deviation below one output sample.
- Metadata schema includes all required columns. Original source IDs, relative paths and hashes are retained locally. No duplicate recording IDs or raw-file SHA256 values. OCSC: 303 unique participant IDs and zero missing ages.
- ZIP member integrity: each of the 20 extracted members matched the archive's uncompressed size and CRC32; local SHA256 recorded. Full-archive MD5 was not verified.
- Missing per-child age and unresolved quality flags correctly yield zero eligible audio recordings. Cohort mean, school grade and age-band midpoints were never substituted.
- Three aggregate PNGs were exported. Age and source/duration plots were visually inspected for readable labels and distinct child-versus-recording counts.

Initial checks encountered Windows sandbox temporary-folder restrictions and a slow/interrupted download. Tests passed after running with the required filesystem access. Acquisition resumed from CRC-verified cached members. This is why download success is based on final per-member verification, not the first attempt.

The first GitHub CI run exposed a test-collection import-path difference between `pytest` and `python -m pytest`. The repository now explicitly configures its root on pytest's import path so both entry points resolve the source package.

Audio decoding is not manual transcription verification, diarization or a near-duplicate audit. Those remain outstanding. No trained model, clinical performance or cross-source generalization was evaluated.
