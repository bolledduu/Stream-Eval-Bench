# Research questions after the completed prototype

Updated 2026-10-09. These are proposed questions, not established findings or verified novelty claims.

## One central goal

Measure and improve selective retrospective correction in streaming video: when later footage clarifies an earlier event, associate it with the right event, correct only supported facts, and preserve understanding of the ongoing stream.

## Evidence motivating the questions

The completed two-source controlled HoloAssist prototype returned ten model answers. The camera's revealed lens was recognized, but its frame was associated with the wrong earlier observation even in the joint control. For the printer, joint answering was correct while answering with its own earlier response was wrong on identical final visual input. The printer's initial response already contained unsupported claims. Both findings are case-level observations; neither satisfies all original clean-initial-uncertainty qualification gates. Reproducibility, natural-stream prevalence and literature novelty are not established.

See `experiments/fixed_hypothesis/FINDINGS.md` and `RESULTS.md`. Four additional proposed repetitions are unexecuted because automatic approval review requested separate authorization. Do not describe them as completed.

## RQ1 — Associate later evidence with the correct earlier event

**When later footage resolves an earlier ambiguity, how reliably can a streaming VLM identify which earlier event the evidence belongs to, beyond simply recognizing what the new footage shows?**

- Purpose: separate recognition from historical event association. The camera example motivates this separation.
- Required comparison: standalone recognition, joint evidence association, and incremental association. Include visually similar competing earlier events and explicit same-event/new-event controls.
- Main measurements: event-association accuracy conditional on successful recognition; replay-versus-new-event discrimination reported separately.
- Example: two camera-handling actions occur. A later close view shows a detached lens. Seeing a lens is insufficient: the system must attach that information to the correct earlier action.

## RQ2 — Determine whether unsupported earlier answers impede correction

**Does a VLM's own unsupported earlier answer reduce the accuracy of later event association and correction compared with an uncertain earlier answer or no earlier answer, when the final visual evidence is identical?**

- Purpose: test a possible mechanism behind the printer discrepancy rather than assume the mechanism is proven.
- Required comparison: identical final frames with no prior answer, the model's actual earlier answer, and a controlled uncertain answer. Separate naturally generated histories from interventions; randomize condition order and repeat runs.
- Main measurements: paired differences in association and supported-correction accuracy, with response variability and independent episode counts reported.
- Example: the system initially guesses that a hidden printer display was illuminated. Later evidence shows which earlier observation had a dark display. Does the original guess lead it to attach that evidence to the wrong observation or retain a contradicted claim?

## RQ3 — Correct selectively while preserving the live state

**When a past event is corrected, can the system preserve unrelated verified facts and the latest live state, without treating replayed footage as a new event or revising facts that the new evidence does not support?**

- Purpose: measure whether correction is safe for the rest of the event record, not merely whether one answer changed.
- Required comparison: revealing evidence, irrelevant later evidence, replay of a different event, and genuinely new but visually similar actions. Use verified facts to test preservation, and unknown facts to test unsupported inference separately.
- Main measurements: justified-correction rate, collateral fact changes, false revisions, duplicate-event rate, and preservation of the latest live state.
- Example: a later replay establishes what part was removed earlier. It must not overwrite what is currently attached to the camera or count the old removal twice.

## RQ4 — Improve correction under deployment constraints

**Can an evidence-grounded update policy improve correct historical revisions while reducing wrong-event updates and collateral changes, under the same visual-memory and inference budget as standard history-conditioned prompting?**

- Purpose: turn the measured weaknesses into an intervention whose benefits and costs can be tested.
- Design requirement: establish event identity and claim-specific support before committing an update, while retaining the option to remain uncertain. This is a requirement, not a claim that a new algorithm has already been invented.
- Required comparison: ordinary history-conditioned prompting, joint-context reference, retrieval/reinspection and abstention baselines, and a proposed policy; equalize available frames, memory and inference budget.
- Main measurements: the same RQ1–RQ3 outcomes together with evidence inspected, memory consumption and measured latency. Penalize policies that avoid errors merely by refusing all corrections.

## Priority and boundaries

First repeat the printer comparison before investing in a larger benchmark. RQ2 is the most focused candidate hypothesis; RQ1 and RQ3 define the required controls and outcomes; RQ4 becomes justified only after a reproducible failure is established. Keep all four within streaming video and retrospective evidence.

The current controlled images do not establish native continuous-stream behavior. A natural-stream benchmark needs independently validated initial ambiguity, later resolving evidence and event identity. No question here is labelled 100% novel: that requires a separate, current comparison against the closest literature, and absolute absence of prior work cannot be guaranteed.
