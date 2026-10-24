# Review 1 — dataset contribution

**Prepared 24 October 2026 for Suhani and Sachithan.**

Investigated eight candidates: OCSC, CHILDES-Aligned, Zenodo 200495, MyST, ASER, Pratham ReadNet, ENNI and Samrómur Children. Recommended OCSC as the primary source because of its participant-age table and shared tasks; a single identity-audited CHILDES-Aligned source corpus is the conditional backup.

| Actual result | Verified count |
|---|---:|
| Ohio participants with unique IDs and decimal ages | 303 |
| Ohio acquired recordings | 0 — login required |
| Ohio missing ages / duplicate participant IDs | 0 / 0 |
| Zenodo acquired, decoded recordings | 20 |
| Zenodo independent participant folders | 10 |
| Total sample audio | 60.952 seconds |
| Original audio | 44.1 kHz, mono |
| Missing individual ages / verbatim transcripts in demo | 20 / 20 |
| Duplicate recording IDs / byte-identical files | 0 / 0 |
| Recordings eligible for age regression | **0** |

Ohio age groups: 4: 26 children; 5: 54; 6: 60; 7: 63; 8: 57; 9: 43. Ages span 4.103–9.936 years. A seed-42 metadata subset provides 26 children per group 4–8 (130 total), but is not a training dataset or a frozen evaluation split.

Delivered reproducible acquisition, metadata preparation, decode/checksum validation, optional 16-kHz conversion, an executed EDA notebook, aggregate plots, comparison CSV/Markdown and teammate input contracts. Original WAVs remain local; public contribution excludes audio and participant rows. Automated tests cover age parsing, missing labels, duplicated content, path containment, corrupt audio, split-group mismatches and preservation of originals.

Varsha can test acoustic extraction now. Arnavi can implement transcript joins/missingness, but this sample has no verified verbatim transcripts. Shrinikhaythan and Sachithan can prepare grouped evaluation interfaces; they cannot defensibly report age-model performance yet.

**Highest-priority next step:** authenticated OCSC download followed by verification of workbook → child → CHAT → media joins and child-only task boundaries. Do not substitute mean ages, grades or device IDs to make an apparently complete training table.

No clinical DLD screening claim follows from this work. The three named project documents were not attached; responsibilities and dates use the supplied brief provisionally. Repository publication status is recorded separately in the handoff accompanying this contribution.
