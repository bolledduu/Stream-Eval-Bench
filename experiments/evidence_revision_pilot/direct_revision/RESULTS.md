# Corrected controlled evidence-update pilot

Model: Qwen/Qwen2-VL-2B-Instruct, pinned revision 895c3a49bc3fa70a340399125c650a463535e71c. CPU bfloat16, greedy decoding, unmodified joint-image inference.

**Scope:** six reference views from three HoloAssist recordings. Content was artificially masked and then revealed; the initial memory and old-record status were supplied. Each request contains still images. The target is unknown-to-known completion, not correction of a previously false assertion. This is not an end-to-end livestream benchmark, natural delayed-evidence dataset, or test of autonomous replay detection.

**Correction:** the earlier per-image feature cache failed an audit against normal joint-image encoding (maximum feature difference 25.125). Its research results are invalidated and retained under `results/invalidated_cached`. Every main trial and both diagnostic triplets were rerun without that cache. Do not cite old accuracy counts as evidence.

| Test | Correct / unique requests |
|---|---:|
| recognition | 4 / 6 |
| static_matching | 2 / 6 |
| visual_update | 0 / 6 |
| oracle_update | 1 / 6 |
| withheld_update | 3 / 3 |

The unchanged-background pixel-match sanity baseline obtains 6/6. It is not a novel method or evidence about naturally changing viewpoints. Thirty main calls represent 27 unique requests: each source has two identical withheld-evidence controls. They are not independent observations. There are only three source sessions.

| Source / record | Target value | Read fact | Match record | Update | Update with supplied ID |
|---|---|---|---|---|---|
| camera / E1 | lens | Fail | Pass | Fail | Fail |
| camera / E2 | cap | Pass | Fail | Fail | Fail |
| printer / E1 | illuminated | Pass | Fail | Fail | Pass |
| printer / E2 | dark | Fail | Fail | Fail | Fail |
| table / E1 | no | Pass | Pass | Fail | Fail |
| table / E2 | yes | Pass | Fail | Fail | Fail |

## Separate post-hoc diagnostics

These cases were selected during exploration, not a held-out test. Text-supplied facts remove perception and are a diagnostic control, not a proposed novel method.

### followups.json

- table_0_context_recognition: PASS; actual output `{"value": "no"}`; expected `{"value": "no"}`.
- table_0_plain_oracle_update: FAIL; actual output `{"E1": "unknown", "E2": "unknown", "event_count": 2, "device": "table"}`; expected `{"E1": "no", "E2": "unknown", "event_count": 2, "device": "table"}`.
- table_0_text_oracle_update: PASS; actual output `{"E1": "no", "E2": "unknown", "event_count": 2, "device": "table"}`; expected `{"E1": "no", "E2": "unknown", "event_count": 2, "device": "table"}`.

### camera_followups.json

- camera_1_context_recognition: FAIL; actual output `{"value": "lens"}`; expected `{"value": "cap"}`.
- camera_1_plain_oracle_update: FAIL; actual output `{"E1": "unknown", "E2": "lens", "event_count": 2, "device": "camera"}`; expected `{"E1": "unknown", "E2": "cap", "event_count": 2, "device": "camera"}`.
- camera_1_text_oracle_update: PASS; actual output `{"E1": "unknown", "E2": "cap", "event_count": 2, "device": "camera"}`; expected `{"E1": "unknown", "E2": "cap", "event_count": 2, "device": "camera"}`.

### simple_baselines.json

- single_image_supplied_id: FAIL; actual output `{"E1": "unknown", "E2": "unknown", "event_count": 2, "device": "table"}`; expected `{"E1": "no", "E2": "unknown", "event_count": 2, "device": "table"}`.
- read_then_write_three_images: FAIL; actual output `{"E1": "yes", "E2": "unknown", "event_count": 3, "device": "table"}`; expected `{"observed_value": "no", "memory": {"E1": "no", "E2": "unknown", "event_count": 2, "device": "table"}}`.

## Interpretation limits

A correct answer in isolation does not guarantee correct perception in a multi-image request; use the context-recognition diagnostic before attributing an update error to memory. One correct E1 match does not establish robust matching; inspect both E1 and E2 and position bias.

No novelty, model-population failure rate, real-time throughput, or CVPR suitability follows from this pilot. Labels were assistant-screened and need independent human validation. A stronger-model replication and naturally occurring delayed evidence remain untested. The attempted hosted larger-model run produced no predictions.

All exact prompts, PNG input hashes, raw responses, expected values, per-field scoring, source references and invalidation history are retained.

## Decision from the completed controls

The pilot detects a reproducible visual-to-structured-record failure in this specific 2B model. It does not establish a streaming-specific research gap. In table E1, the model reads `no` correctly in the full three-image context, preserves `unknown` under the simpler visual update request, and correctly writes `no` when supplied as text. However, the one-image update also fails; therefore streaming history or long-term memory is not necessary for this failure. The read-then-write prompt also fails and does not follow its requested output schema. These findings remain compatible with generic multimodal instruction-following or task-composition weaknesses.

The camera case is not a clean integration counterexample: contextual recognition incorrectly says `lens` for the cap. Do not attribute its downstream wrong update exclusively to memory.

Recommendation: do not claim that this pilot proves a novel streaming-memory problem or validates a CVPR contribution. The missing decisive evidence is failure on natural, continuously revealed events in stronger models after perception, correspondence, prompt-format and ordinary state-change controls pass. No novel framework has been established here.
