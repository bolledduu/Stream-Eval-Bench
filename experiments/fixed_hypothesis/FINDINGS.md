# Completed two-video prototype: findings and decision

**The fixed prototype is complete: all ten planned conditions have saved, parseable model answers.** Eleven core requests were needed because one upstream service failure was recovered once. Both the error and the successful recovery are retained. Four separately proposed post-hoc repeat requests were blocked by automatic approval review; no repeat results exist.

## Goal

Test whether later visual evidence can fill the correct earlier record while leaving an unrelated, still-hidden fact unknown. Keep the central question fixed and separate seeing a fact from assigning it to the correct historical observation.

## Data and model

- Two existing HoloAssist recordings: camera handling (`z176-sep-05-22-dslr`) and printer operation (`R071-19July-BigPrinter`).
- Camera snapshots: 10.0142 s and 17.0241 s. Printer snapshots: 19.2864 s and 42.6331 s.
- Initial uncertainty was created with gray masks over the relevant region. The later reveal is the original unmasked frame. These are controlled delayed frame observations, not naturally occurring livestream replays.
- Public backend declares `qwen3-vl-235b-a22b-instruct`. Exact weights, decoding settings and provider caching are not independently controlled.
- Joint and update use the **same image bytes** and common task instructions. Update additionally receives the model's own initial answer. Original visual context is retained in both, so the comparison does not remove evidence from one condition.

## What the model actually did

| Test | Camera | Printer |
|---|---|---|
| Initial masked observations | Correctly left both unknown | Assigned illuminated/dark despite the target display being hidden |
| Recognize the revealed fact alone | Correct: lens | Correct: dark |
| Joint matching and answering | Wrong: matched E1 reveal to E2 | Correct: matched reveal to E2; E1 unknown, E2 dark |
| Update with its prior answer | Wrong: wrote lens into E2 instead of E1 | Wrong: matched reveal to E1; E1 illuminated, E2 unknown |
| No new evidence | Correctly retained unknown/unknown | Repeated the unsupported illuminated/dark claims |

Both standalone recognition responses renamed the requested JSON key: `part` and `display` instead of `value`. Their meanings are correct; strict schema compliance failed. RESULTS.md retains both interpretations rather than calling recognition wrong.

## The clearest example: printer

The later unmasked frame belongs to **E2**, whose display is dark. E1's display remains hidden, so E1 must remain unknown.

- **Correct answer:** E1=unknown; E2=dark; matched_record=E2.
- **Joint answer actually returned:** exactly that correct answer.
- **Update answer actually returned:** E1=illuminated; E2=unknown; matched_record=E1.
- The update explanation also says the display is dark while its stored E1 value remains illuminated. This is an additional response-internal inconsistency in this single answer.

The comparison contains a concrete failure, not an infrastructure error. However, one joint/update pair cannot distinguish a reproducible prior-history effect from response variability. We therefore call it an **observed history-conditioned discrepancy**, not proof that prior answers cause failure in general.

## What the camera teaches us

The model recognizes the detached lens, but assigns its full view to the wrong initial observation even without prior answer history. This is a static association failure. The update error does not isolate a streaming-specific mechanism on this case. It still demonstrates why recognition-only evaluation is insufficient for this controlled task.

## Predeclared gates and honest interpretation

The original qualification rule required initial unknown/unknown, correct recognition and correct joint answering before interpreting an update failure. Neither case satisfies every gate: the camera fails joint matching; the printer fails initial uncertainty. Strict recognition schema compliance also fails, although the semantic answers are correct.

Thus the narrowly predeclared clean-abstention-to-revision hypothesis is **not confirmed** by this run. We do not change those gates after seeing results. The printer discrepancy nevertheless supplies a concrete exploratory follow-up: whether unsupported early claims interfere with subsequent evidence association and correction. This is related to the original retrospective-evidence question, not a demonstrated new benchmark contribution.

## Decision

1. **Prototype implementation: complete.** Ten conditions answered; raw prompts, outputs, hashes, source metadata, failures, amendments and scoring are saved.
2. **Observed weaknesses: concrete.** Correct object/state recognition did not ensure correct historical association. Printer answering changed from correct to incorrect when its own earlier answer was included.
3. **Research direction: retain the central question, but do not claim the specific mechanism is established.** The priority is repeating the printer joint/update pair, then separating initial unsupported claims from general association difficulty.
4. **Full benchmark/paper claims: not yet justified.** Two controlled frame episodes are not evidence of natural-stream prevalence, native realtime failure, reproducibility, multi-model generality or novelty.

## Verification and reproduction

The final audit passed 16 integrity/parity checks: every request image hash matches, joint/update inputs are identical, the only prompt difference is the exact prior model answer, and withheld controls reuse the prefix image. Six scorer tests pass. Manual comparison to raw outputs caught and corrected an identifier-normalization bug: the scorer lowercased returned E1/E2 values but not their references. Both sides now normalize consistently; no raw response or reference answer was changed. Regression tests cover correct and incorrect record identifiers.

See `RESULTS.md` for every value and explanation, `results.json` for consolidated raw responses, `first_pass_results.json` for the original incomplete first-pass record, `attempts/` for the preserved service error, and `final_audit.json` for integrity checks. `protocol.json` remains the original frozen protocol; subsequent recovery and proposed repetition have separate amendments.

The proposed four-request repeat check is unexecuted because automatic approval review requires separate permission for that expanded scope. It is not silently counted as complete or as a model failure.
