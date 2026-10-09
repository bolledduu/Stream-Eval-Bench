# Completed intervening-footage prototype

**Decision: do not scale to a full benchmark on the current evidence.** The proposed delayed-arrival-specific failure was not established. This is a no-go for scaling this claim, not proof that the broader question has no value.

## Execution

All nine planned calls now have model responses. There were eleven total attempts: nine responses and two preserved infrastructure errors. The interrupted chronological branch was resumed under the documented completion amendment. No successful response was rerun or replaced. The resumption used identical prompts, packets, and model-produced predecessor memory.

Backend: official public demo declaring Qwen3-VL-235B-A22B-Instruct. Live weights/decoding settings unverified. Data: one HoloAssist table-assembly episode, seven existing four-frame MP4 packets. This is not three-video replication.

## Observed answers

| Condition / step | Earlier | Latest | Expected earlier / latest |
|---|---|---|---|
| Chronological: packet 0 | unknown | unknown | unknown / no |
| Chronological: packet 1 | unknown | yes | no / no |
| Chronological: matched checkpoint | unknown | yes | no / yes |
| Chronological: continuation | unknown | yes | no / yes |
| Delayed: packet 0 | unknown | unknown | unknown / no |
| Delayed: packets 2–5 | unknown | yes | unknown / yes |
| Delayed: historical packet 1 | unknown | yes | no / yes |
| Delayed: continuation | unknown | yes | no / yes |
| Together: packets 0–5 | unknown | yes | no / yes |

## Interpretation

At the matched checkpoint, chronological, delayed, and together conditions all returned historical unknown and current yes. Both streaming continuations retained that answer. The historical answer should have been no. Thus the historical question failed in all conditions; there is no observed delayed-specific difference at these checkpoints. Shared failure can conceal additional mechanisms, so this does not rule out arrival-order effects in general.

The chronological earlier-only packet also returned historical unknown and latest yes (both incorrect), providing an additional warning against attributing the later error specifically to memory or delay. The failure could involve visual interpretation, time-to-frame grounding, task instructions, hosted video processing, or combinations; this run does not isolate these causes.

The earlier two-clip pilot succeeded, while this extension did not. They differ in prompt wording, amount/grouping of footage, and uncontrolled hosted execution. Their difference is not a clean causal effect of duration, distractors, or memory load.

## Prototype conclusion

Completed: a matched comparison with raw response preservation and both exact memory-chain audits. Not established: a streaming-specific limitation, a novel method, a population failure rate, or confidence adequate for a full benchmark. No benchmark-scale data collection or method claim is justified by this prototype alone. The current hypothesis is unsupported by this pilot, not disproven universally.

## Audit and limitations

All nine responses parsed into the requested schema. Packet sets matched at both comparison points. Media hashes were verified before inference. All seven local videos contain four decodable frames. That audit cannot establish the hosted provider sampling policy or prove which visual information the model used.

Other limitations: one source episode, one completion per condition, supplied capture times, explicitly instructed preservation, external two-field text memory, grouped intervening packets, uncontrolled service settings, and a later resumption of the chronological condition. Labels are researcher-screened, not independently annotated. No statistical confidence interval or model-wide conclusion is warranted.

Infrastructure errors and deviations are recorded in infrastructure_errors/, retry_amendment.json and completion_amendment.json. PARTIAL_RESULTS.md is the superseded partial-run report. The authoritative current files are this report, results.json and audit.json.
