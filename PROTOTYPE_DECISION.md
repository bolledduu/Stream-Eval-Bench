# Prototype decision: do not scale the current claim

## Latest completed controlled prototype — 2026-10-09

The fixed two-source HoloAssist prototype is now **complete: ten planned conditions returned model answers**, with one archived upstream error recovered once (eleven core requests). See `experiments/fixed_hypothesis/FINDINGS.md` for the decision and `RESULTS.md` for every output.

- Both revealed facts were recognized correctly in standalone requests, with renamed JSON keys recorded separately as schema noncompliance.
- Camera: joint and incremental answering both associated the reveal with the wrong historical record. This is not an isolated streaming-update failure.
- Printer: joint answering was correct; answering with its own earlier response was wrong on the same final image. Its initial masked-view answer already contained unsupported claims. This is an exploratory history-conditioned discrepancy, not a replicated causal effect.
- Neither case passes every predeclared clean-initial-uncertainty qualification gate. The gates have not been changed after observing the results.
- Four proposed post-hoc repetitions were blocked by automatic approval review and remain unexecuted. They are not included in completed counts.

This follow-up uses controlled occlusions and delayed original frames, not validated natural streaming replays. Keep the retrospective-evidence question, investigate the observed discrepancy, and do not yet scale a benchmark around an established streaming-specific failure claim. The previous pilot record follows below and is retained for provenance.

## What is complete

The bounded diagnostic work is complete: the prior two-clip experiment (5 calls), intervening-footage comparison (9 calls), and endpoint-recognition controls across all three recordings (6 calls). These are **20 saved model responses** from the hosted demo declaring Qwen3-VL-235B-A22B-Instruct. Two extra infrastructure-error attempts occurred in the nine-call experiment and are archived. These totals exclude older lost hosted logs and the separate local-model pilots.

All three original videos were re-downloaded and hash-verified. A 1fps source review inspected 266 frames across seven contact sheets. This is a coarse assistant review, not exhaustive frame-by-frame or independent human annotation.

## Results

| Diagnostic | Result | What follows |
|---|---|---|
| Endpoint recognition: three videos, image/video each | 6/6 expected answers correct | Basic endpoint recognition works for these requests. |
| Two-clip historical update | All three final conditions correct; one intermediate chronological error | Explicitly timestamped simple delayed updating can work. |
| Longer historical update | Together, chronological and delayed all returned earlier=unknown/latest=yes at matched checkpoints | Historical retrieval/update fails here, but no delayed-specific difference was observed. |
| Full original-event-revelation task | Zero currently validated question/evidence pairs | The original hypothesis has not received a valid direct test. This is a data/annotation gap, not a scored model failure. |

## Scientific verdict

**No-go for building a full benchmark around a claimed delayed-arrival-specific failure on the current evidence.** This is a decision about investment and claims, not proof that the broader research direction is impossible.

The six new controls remove one overly broad explanation: the model is not universally unable to recognize the selected states or accept video packets. They do not identify why larger historical questions fail. The longer task can fail due to temporal grounding, prompt interpretation, multi-video reasoning, video sampling, memory or combinations. Together-control failure prevents attribution specifically to delayed streaming.

Our original question requires later evidence to resolve a previously unclear fact about an identifiable earlier event while preserving unrelated/current facts. The selected lens/cap, display and tray cases are primarily physical-state examples. We have not verified the necessary initial uncertainty, later revealing evidence and same-event correspondence for them. Rearranging clips alone does not establish those properties.

The printer paper-handling segment may merit annotation for reverse-side visibility, but sheet identity and initial uncertainty are unverified. It was not assigned ground truth or scored. No claim is made that these datasets, or even these entire recordings, lack suitable events.

## What is not complete

Validation of the full original hypothesis, replay versus genuinely repeated-action discrimination, independent human annotation, independent-episode replication of an order effect, multi-model replication, and novelty verification. These cannot honestly be labeled complete from the present three-video diagnostic. No new framework or novel method has been established.

## Files

- experiments/two_clip_diagnostic/RESULTS.md: prior short test.
- experiments/intervening_video/RESULTS.md: complete nine-call comparison.
- experiments/format_controls/RESULTS.md: six new controls and limitations.
- experiments/source_suitability/README.md: suitability review and admission criteria.
- Each experiment retains raw responses and reproducible inputs or pinned source references.

## Stop rule for this pilot

Do not spend more calls trying to force the current table case to produce a delayed-specific failure. Do not select examples based on model failures. Before a new research-phase experiment, define and independently validate a small fixed set of original-event-revelation episodes. Without those annotations there is no defensible ground truth for the original benchmark task, regardless of code quality.
