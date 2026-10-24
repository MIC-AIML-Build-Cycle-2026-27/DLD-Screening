# Child-speech dataset comparison

Evidence checked 24 October 2026. Publisher counts are not locally verified usable counts. UNVERIFIED means no evidence sufficient to confirm the field. See dataset_selection.md for decisions and actual results.

## Ohio Child Speech Corpus (OCSC)

| Field | Finding |
|---|---|
| publisher | Ohio State University and collaborators |
| official_url | https://talkbank.org/childes/access/Eng-NA/OCSC.html |
| download_url | https://talkbank.org/data/childes/Eng-NA/OCSC?f=zip ; https://media.talkbank.org/childes/Eng-NA/OCSC |
| license | TalkBank default CC BY-NC-SA 3.0; specific override unverified |
| commercial_use | Not permitted under default licence |
| redistribution | Respect TalkBank registration/confidentiality restrictions; no participant data in public repo |
| children | 303 publisher and workbook rows |
| recordings | UNVERIFIED |
| duration_hours | UNVERIFIED |
| age_range | 4–9 years |
| exact_age | YES: public workbook Exact Age |
| age_precision | Decimal years; underlying measurement precision UNVERIFIED |
| language | English; not all participants monolingual |
| task | Alphabet; Numbers; Wug; picture description; reading; Howto |
| audio | Publisher available; live download returned login HTML |
| audio_format | UNVERIFIED |
| transcripts | CHAT download advertised; login required |
| alignment | Task gems documented; timestamp accuracy UNVERIFIED |
| child_identifiers | Workbook ID unique; join to audio still UNVERIFIED |
| clinical_labels | Parent-reported history; not a DLD diagnosis |
| recording_conditions | Science museum; lapel microphone; robot conditions vary |
| missing_metadata | Recording paths/durations and audio joins not acquired |
| source_task_bias | Reading ability changes task participation; demographic and robot-condition imbalance |
| review1 | PRIMARY, conditional on access and child/audio/task join |
| future_dld | Useful age baseline; not clinical validation |
| evidence_status | Publisher + downloaded 303-row workbook verified; audio blocked by registration |

## CHILDES-Aligned

| Field | Finding |
|---|---|
| publisher | Haolong Zheng and Mark Hasegawa-Johnson, University of Illinois |
| official_url | https://talkbank.org/childes/access/Derived/CHILDES-Aligned.html |
| download_url | https://media.talkbank.org/childes/0extra/CHILDES_Aligned.zip ; https://huggingface.co/datasets/MagicLuke/CHILDES-Aligned |
| license | CC BY-NC-SA 4.0 stated on corpus page |
| commercial_use | No |
| redistribution | Attribution/noncommercial/share-alike plus TalkBank rules |
| children | UNVERIFIED |
| recordings | 501880 General clips; 5533 sessions; 49 corpora (publisher) |
| duration_hours | 413.3 General; 282.6 ASR (publisher) |
| age_range | 0;6–14;3 (publisher) |
| exact_age | child_age documented; completeness UNVERIFIED |
| age_precision | CHAT years;months.days |
| language | English |
| task | Mixed source-corpus tasks |
| audio | 16-kHz clips advertised; HF file fetch returned 401 |
| audio_format | 16 kHz mono WAV |
| transcripts | CSV/JSONL text; General raw CHAT, ASR normalized |
| alignment | Utterance boundaries recovered by multi-model consensus; not guaranteed exact |
| child_identifiers | recording_id is documented; globally stable child ID UNVERIFIED |
| clinical_labels | child_group documented; semantics depend on original corpus |
| recording_conditions | Heterogeneous |
| missing_metadata | Child mapping; task mapping; age missingness; actual metadata schema not downloaded |
| source_task_bias | Strong risk of source-age confounding and longitudinal leakage |
| review1 | BACKUP: one original corpus only, after identity mapping and access |
| future_dld | Potential linguistic research; trace original labels |
| evidence_status | Headline claims independently confirmed on official page, NOT independently recounted; file tree 97 General shards verified |

## Children speech recording (Zenodo 200495)

| Field | Finding |
|---|---|
| publisher | Kennedy, Lemaignan et al.; Plymouth University HRI lab |
| official_url | https://zenodo.org/records/200495 |
| download_url | https://zenodo.org/records/200495/files/english_children.zip?download=1 |
| license | CC BY 4.0 (Zenodo API) |
| commercial_use | Allowed by licence with attribution |
| redistribution | Allowed by licence with attribution; team public repo excludes recordings |
| children | 11 publisher; numbered participant folders |
| recordings | 671 WAV archive members, including microphone/segmentation variants |
| duration_hours | UNVERIFIED |
| age_range | Only mean 4.9 reported |
| exact_age | NO individual age metadata found: archive contains WAV files only |
| age_precision | Cohort mean only; never use as per-child target |
| language | English; native and non-native speakers |
| task | Frog story retelling; repeated sentences; number naming |
| audio | Open; ranged member extraction supported |
| audio_format | Lossless WAV; sample-specific properties measured locally |
| transcripts | Filename prompts only for fixed tasks; no verified verbatim transcripts |
| alignment | Free-speech segmentation advertised; fixed-task prompts are not transcripts |
| child_identifiers | Numbered 01–11 folders, preserved across microphone/task variants |
| clinical_labels | Not provided; do not infer typically developing |
| recording_conditions | Studio/portable/robot microphones; missing combinations |
| missing_metadata | Individual age, diagnosis, verbatim fixed-task transcript |
| source_task_bias | Very small sample; microphone variants duplicate performances |
| review1 | AUDIO DEMO ONLY; ineligible for supervised age regression |
| future_dld | Preprocessing robustness only; no clinical labels |
| evidence_status | API licence and ZIP central-directory structure verified; sample validation reported separately |

## MyST Children’s Conversational Speech

| Field | Finding |
|---|---|
| publisher | Boulder Learning Inc.; LDC |
| official_url | https://catalog.ldc.upenn.edu/LDC2021S05 |
| download_url | LDC licensed web download; catalogue login |
| license | MyST Children’s Conversational Speech Agreement |
| commercial_use | Separate commercial licence via Boulder Learning |
| redistribution | UNVERIFIED agreement details; do not redistribute |
| children | 1371 students (publisher) |
| recordings | 227567 utterances; 10496 sessions (publisher) |
| duration_hours | Approximately 470 (publisher) |
| age_range | Grades 3–5; not an exact age range |
| exact_age | UNVERIFIED; grade must not be converted to age |
| age_precision | UNVERIFIED |
| language | English |
| task | Virtual science-tutor dialogue |
| audio | Licensed download; public sample exists |
| audio_format | 16 kHz, mono, 16-bit FLAC |
| transcripts | 102433 utterances, approximately 45% (publisher) |
| alignment | Per-utterance text; word timestamps UNVERIFIED |
| child_identifiers | Student grouping expected but released schema UNVERIFIED |
| clinical_labels | UNVERIFIED |
| recording_conditions | Microphone dialogue with virtual tutor |
| missing_metadata | Individual chronological age and ID schema not verified |
| source_task_bias | Science curriculum/grade and partial transcription |
| review1 | Exclude until licence and age fields verified; older target population |
| future_dld | Conversational features, not diagnostic labels |
| evidence_status | LDC catalogue inspected; complete licensed files not acquired |

## ASER Dataset

| Field | Finding |
|---|---|
| publisher | Pratham Education Foundation |
| official_url | https://github.com/PrathamOrg/ASER-Dataset |
| download_url | https://github.com/PrathamOrg/ASER-Dataset/tree/master/Data |
| license | CC BY-NC-SA 4.0 |
| commercial_use | No |
| redistribution | Attribution/noncommercial/share-alike |
| children | UNVERIFIED |
| recordings | 5301 samples (publisher; not assumed independent children) |
| duration_hours | UNVERIFIED |
| age_range | 6–14 publisher |
| exact_age | README example exposes ageGroup, e.g. 7–10 years |
| age_precision | Age bands, not exact ages |
| language | Hindi, Marathi, English tasks |
| task | Reading-level assessment |
| audio | Audio/JSON samples advertised in Data |
| audio_format | Example recordingName .mp3; rates UNVERIFIED |
| transcripts | que_text is target prompt, not verified spoken transcript |
| alignment | Question/recordingName mapping; temporal alignment UNVERIFIED |
| child_identifiers | deviceID identifies collection device, not child; stable child ID UNVERIFIED |
| clinical_labels | Reading-proficiency labels only |
| recording_conditions | Android mobile app |
| missing_metadata | Exact age, stable child ID, audio properties |
| source_task_bias | Language, schooling, literacy and device confounds |
| review1 | Exclude from exact-age evaluation |
| future_dld | Future reading research; reading proficiency is not language development |
| evidence_status | Official README/JSON example inspected; raw sample content not acquired |

## Pratham ReadNet

| Field | Finding |
|---|---|
| publisher | Pratham Education Foundation / PrathamOrgAI |
| official_url | https://huggingface.co/datasets/PrathamOrgAI/ReadNet |
| download_url | https://huggingface.co/datasets/PrathamOrgAI/ReadNet/tree/main |
| license | CC BY-NC 4.0 |
| commercial_use | No |
| redistribution | Attribution and noncommercial; verify audio-link terms before redistribution |
| children | Released subset count UNVERIFIED; 200000+ refers to wider collection |
| recordings | Viewer approximately 42.2k rows; downloaded HI_Letters has 8783 rows |
| duration_hours | Approximately 87 released hours; 2500 broader collection (card) |
| age_range | 5–16 broader collection (card) |
| exact_age | Not exposed in inspected CSV |
| age_precision | Unavailable in inspected CSV |
| language | Hindi and Marathi |
| task | Read letters, words, paragraphs and stories |
| audio | External WAV URLs in CSV; audio not tested |
| audio_format | WAV links; sampling rate UNVERIFIED |
| transcripts | Transcribed Text column |
| alignment | Row-level URL/text pair; word timestamps not exposed |
| child_identifiers | No explicit ID column; URL-token meaning UNVERIFIED |
| clinical_labels | None in inspected CSV |
| recording_conditions | UNVERIFIED |
| missing_metadata | Individual age, documented child ID, task/session mapping |
| source_task_bias | Literacy and language; released subset selection |
| review1 | Exclude from age regression with current released fields |
| future_dld | Potential multilingual ASR/reading research |
| evidence_status | Publisher card, file tree and one actual 8783-row/two-column CSV inspected |

## Edmonton Narrative Norms Instrument (ENNI)

| Field | Finding |
|---|---|
| publisher | Phyllis Schneider and colleagues, University of Alberta |
| official_url | https://talkbank.org/childes/access/Clinical-Eng/ENNI.html |
| download_url | https://talkbank.org/childes/access/Clinical-Eng/ENNI.html |
| license | TalkBank default CC BY-NC-SA 3.0; verify specific terms |
| commercial_use | No under default licence |
| redistribution | TalkBank access/confidentiality rules; authors request copies of publications |
| children | 361 included: 286 control, 75 language-impaired (publisher) |
| recordings | UNVERIFIED |
| duration_hours | UNVERIFIED |
| age_range | 4–9;11 |
| exact_age | CHAT headers documented; files not acquired |
| age_precision | CHAT age documented; completeness UNVERIFIED |
| language | English |
| task | Picture-story generation |
| audio | CONFLICT: corpus page says not available but has media link; DrivenData reports audio use |
| audio_format | UNVERIFIED |
| transcripts | CHAT |
| alignment | Story gems documented; audio alignment UNVERIFIED |
| child_identifiers | Participant files documented; cross-file grouping needs verification |
| clinical_labels | TD and language impairment; not equivalent to current DLD diagnostic criteria |
| recording_conditions | Schools, preschools, daycare; story elicitation |
| missing_metadata | Current audio availability and alignment |
| source_task_bias | Clinical group, elicitation and selection effects |
| review1 | Reserve; resolve contradictory audio documentation first |
| future_dld | Stronger future clinical-language research candidate after label/access audit |
| evidence_status | Official corpus description and conflicting DrivenData directory inspected |

## Samrómur Children 21.09 (SLR117)

| Field | Finding |
|---|---|
| publisher | Reykjavik University LVL and Almannarómur |
| official_url | https://openslr.org/117 |
| download_url | https://openslr.trmal.net/resources/117/samromur_children_21.09.zip |
| license | CC BY 4.0 |
| commercial_use | Allowed with attribution |
| redistribution | Allowed with attribution |
| children | UNVERIFIED |
| recordings | More than 137000 validated recordings (publisher) |
| duration_hours | UNVERIFIED |
| age_range | 4–17 |
| exact_age | Per-record age availability UNVERIFIED |
| age_precision | UNVERIFIED |
| language | Icelandic |
| task | Prompt reading |
| audio | 6.8 GB archive advertised; not downloaded |
| audio_format | 16 kHz 16-bit mono FLAC |
| transcripts | Prompt metadata; spoken deviations UNVERIFIED |
| alignment | Recording/prompt mapping |
| child_identifiers | Speaker folders and speaker_ID-utterance_ID filenames; speaker-disjoint official splits |
| clinical_labels | UNVERIFIED |
| recording_conditions | Crowdsourced |
| missing_metadata | Individual age precision and demographics uninspected |
| source_task_bias | Crowdsourcing, prompt reading and language mismatch |
| review1 | Exclude from initial English-only model |
| future_dld | Future multilingual speech research after age audit |
| evidence_status | Official OpenSLR resource inspected; archive not acquired |
