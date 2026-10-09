# Completed two-clip experiment

Five model calls completed on 9 October 2026 UTC (8 October Pacific). Public demo declares Qwen3-VL-235B-A22B-Instruct; backend weights and decoding settings are not independently verified.

| Condition / step | Earlier state | Latest state | Assessment |
|---|---|---|---|
| Both clips together | no | yes | Correct |
| Chronological: earlier clip only | no | yes | Latest state incorrect; expected no |
| Chronological: after later clip | no | yes | Correct final answer |
| Delayed: later clip only | unknown | yes | Correct |
| Delayed: after earlier clip | no | yes | Correct historical update and preservation |

**Result:** The proposed delayed-evidence failure was not observed on this example. The model changed the historical field from unknown to no when the earlier footage arrived, while retaining the correct latest state. Both chronological and delayed final answers matched the together control. A final-answer-only score would conceal the intermediate chronological error.

**Decision:** Do not cite this example as evidence of an arrival-order-specific research gap. It is a useful successful-update control for future experiments. The intermediate error is not evidence for the proposed mechanism.

**Limits:** One source recording, one run per condition, two packets with four sampled frames each, supplied capture timestamps, explicit preservation instructions, and external two-field text memory. This does not test natural replay detection, event identity matching, long streams, bounded-memory stress, throughput, or a native streaming VLM. Success here neither proves general reliability nor rules out the broader hypothesis. No inference about novelty follows from this experiment.

**Audit:** All five responses are retained. Each second streaming step received its own model-produced first-step response verbatim. Identical video bytes were used across conditions; hashes verified. All five outputs parsed as JSON. Expected answers were not supplied in prompts. Exact prompts, raw outputs, durations, and timestamps are in results.json. The protocol and code were frozen before results were collected.

Files: run.py (resumable runner), README.md (protocol), results.json (raw results and audit), earlier.mp4 and later.mp4 (exact inputs), experiment_record.json (plain JSON containing the code, reports, and encoded input files; no ZIP).
