# Intervening-footage experiment: partial execution, inconclusive mechanism

## Outcome

Six of nine planned model calls completed. One chronological request failed twice with an upstream Gradio AppError; no model answer was returned. Its two downstream calls were not executed because their required model-produced memory did not exist. Total attempts: eight (six responses and two service errors). Errors are not scored as incorrect model answers.

Model: public demo declaring Qwen3-VL-235B-A22B-Instruct. One HoloAssist table-assembly episode, seven existing four-frame video packets. No model weights or decoding settings independently pinned.

| Condition / step | Earlier | Latest | Interpretation |
|---|---|---|---|
| Chronological: packet 0 | unknown | unknown | Historical unknown appropriate; latest should be no |
| Chronological: packet 1 | — | — | Service error, including one retry |
| Chronological: packets 2–5 | — | — | Not run: upstream request failed |
| Chronological: continuation | — | — | Not run: upstream request failed |
| Delayed: packet 0 | unknown | unknown | Historical unknown appropriate; latest should be no |
| Delayed: packets 2–5 | unknown | yes | Correct: historical evidence not yet received |
| Delayed: historical packet 1 | unknown | yes | Historical answer should be no; latest yes is correct |
| Delayed: continuation | unknown | yes | Historical answer should be no; latest yes is correct |
| Together: packets 0–5 | unknown | yes | Historical answer should be no; latest yes is correct |

## What this means

The delayed sequence did not resolve the historical field after the older evidence arrived, and retained unknown through the continuation. However, the together control also returned historical unknown with all relevant packets available. Thus this is not evidence that arrival order caused the failure. Incomplete chronological execution is a second reason causal attribution is unavailable.

The preceding two-clip diagnostic succeeded. This extension differs in footage quantity/grouping and prompt wording, and the hosted generation settings are uncontrolled. Their difference cannot establish a causal effect of stream length.

## Execution integrity

The protocol was saved before inference. Completed outputs were never replaced. Conditions used isolated sessions; steps within each stream were sequential. Media hashes and matched packet sets were checked. The full delayed memory chain used previous raw model outputs verbatim. Six returned objects passed the JSON schema. One explicit, recorded infrastructure-only retry amended the initial no-retry protocol; it also failed. See retry_amendment.json and infrastructure_errors/.

## Decision

Do not use this run to claim a streaming-specific gap or strong confidence. No additional models or videos were searched to force a positive result. Before further inference, validate that each short packet supports its labeled endpoint and use a reliable backend with controllable settings. A complete chronological comparison and successful evidence-understanding controls are still required.

Files: run.py, retry_infrastructure.py, protocol.json, results.json, responses/, infrastructure_errors/, audit.json, run.log, retry.log. Media remain in the previously committed sibling streaming_trial directory. This run did not test camera or printer episodes, event association, or replay-versus-new-action discrimination.
