# Intervening-footage nine-call diagnostic

This follows the completed two-clip test on the same HoloAssist table-assembly recording. It is a prespecified extension, not an independent dataset replication or a new method.

## Frozen design

| Condition | Incoming packets per model update |
|---|---|
| Chronological | [0], [1], [2,3,4,5], [6] |
| Delayed | [0], [2,3,4,5], [1], [6] |
| Together | [0,1,2,3,4,5] in one request |

Compare streams after their third updates, when each has seen packets 0–5, and after the fourth update, when each has also seen packet 6. Expected historical state around source time 72s is `no`; latest state at both comparison points is `yes`. Labels are used only for scoring, not in model prompts. Earlier-only latest states at packets 0 and 1 should be `no`; the historical answer should remain unknown until packet 1 arrives.

The four sampled source frames in each existing MP4 and capture-time mapping are unchanged. The intervening packets are grouped into one update to keep the total to nine calls. This is not a test of a native continuous streaming architecture, and it does not isolate elapsed time from the amount/content of intervening footage. It tests this particular longer input history and arrival-order intervention.

Each streaming condition starts with empty memory and carries its own raw previous model answer forward. Historical frame buffers are not retained. Fresh hosted sessions prevent cross-condition chat history. The three conditions execute concurrently, but steps within each condition are sequential. Hosted load may affect duration, so timing is not a latency benchmark.

The service is Qwen's public demo declaring Qwen3-VL-235B-A22B-Instruct; live weights and decoding parameters cannot be pinned. The API has no system-role field, so the instruction block is prepended to the user prompt. This implementation detail is recorded in protocol.json. No automatic retries or outcome-based example changes are used.

## Run

Use the same dependencies as ../two_clip_diagnostic/requirements.txt, then:

```bash
python experiments/intervening_video/run.py
```

Existing completed responses are reused only if prompts match exactly. Recorded errors stop that condition and are not silently retried. For an independent rerun, preserve this directory and create a separate run copy. All media are referenced from the existing sibling evidence_revision_pilot/streaming_trial directory; no downloads or model weights are required for inference.

## Interpretation

- Together and chronological succeed, delayed fails: a candidate effect requiring independent replication and error diagnosis.
- Together fails: evidence understanding is a confound.
- Chronological fails: ordinary sequential updating is a confound.
- All comparison points succeed: no positive evidence of a delayed-update failure on this example.

Read every intermediate response; final-answer accuracy can hide earlier errors. The earlier two-clip experiment and this extension share a source episode and are not independent samples. No confidence interval or population-level failure rate should be inferred from this run.

## Observed infrastructure amendment

One explicit infrastructure-only retry of chronological_1 was authorized after the first upstream AppError; both error records are retained. The retry failed too. Six calls completed and two downstream calls remain blocked. See RESULTS.md. Do not interpret the initial no-automatic-retry setting as evidence that no manual retry occurred.

## Completed status (supersedes partial status above)

All nine calls completed after an additional user-requested infrastructure resumption, recorded in completion_amendment.json. Eleven attempts total, including two archived service errors. No completed model answer was replaced. All three matched conditions returned historical unknown/current yes. See RESULTS.md for the no-go decision on scaling the current claim.
