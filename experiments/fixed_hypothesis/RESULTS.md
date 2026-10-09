# Fixed-hypothesis prototype: two HoloAssist sources

Primary question: can a fuller view update the correct earlier record while preserving the other record?

| Source | Initial uncertainty | Recognition | Joint answer | Update | No-new-evidence control |
|---|---|---|---|---|---|
| camera | pass | schema_error | fail | fail | pass |
| printer | fail | schema_error | pass | fail | fail |

## Case decisions

- camera: Not qualified for attributing an update failure; inspect the failed/missing gate.
- printer: Not qualified for attributing an update failure; inspect the failed/missing gate.

## Every observed answer

| Source | Condition | E1 / standalone value | E2 | Matched record | Latest record |
|---|---|---|---|---|---|
| camera | prefix | unknown | unknown | none | E2 |
| camera | recognition | lens | — | — | — |
| camera | joint | unknown | unknown | E2 | E2 |
| camera | update | unknown | lens | E2 | E2 |
| camera | withheld | unknown | unknown | none | E2 |
| printer | prefix | illuminated | dark | none | E2 |
| printer | recognition | dark | — | — | — |
| printer | joint | unknown | dark | E2 | E2 |
| printer | update | illuminated | unknown | E1 | E2 |
| printer | withheld | illuminated | dark | none | E2 |

## Reference answers

| Source | Prefix and withheld | Standalone recognition | Joint and update |
|---|---|---|---|
| camera | E1=unknown; E2=unknown; match=none | lens | E1=lens; E2=unknown; match=E1 |
| printer | E1=unknown; E2=unknown; match=none | dark | E1=unknown; E2=dark; match=E2 |

Latest record remains E2 in all record-based conditions. This is explicitly supplied capture-order metadata, not autonomous temporal inference.

## Recognition: semantic answer versus schema compliance

The strict table above requires the requested key `value`. The following transparent semantic audit reads a single scalar under a renamed key; it does not overwrite the strict scores or change original qualification decisions.

- camera: returned `{"part": "lens"}`; semantic recognition correct: **True**.
- printer: returned `{"display": "dark"}`; semantic recognition correct: **True**.

## Model explanations (verbatim raw outputs are in responses/)

- **camera_withheld:** No detached camera part is visible in either record; gray rectangles obscure lower portions where such items might appear, and no fuller view has been provided.
- **printer_update:** The fuller view matches E1: same blue card reader, same paper stack, same angle. It confirms the central display is dark (no glow or content visible). Since E2’s display area remains masked and no direct evidence exists for it, E2 status is unknown. E2 remains latest by capture order.
- **printer_joint:** The newly available fuller view matches E2’s spatial layout and angle, confirming the central display is dark. E1 remains unknown as no direct visual evidence from its own panel establishes display state.
- **camera_prefix:** No detached camera part is visible in either record; gray rectangles obscure lower portions where such items might appear, and no fuller view has been provided.
- **camera_joint:** The newly available fuller view shows hands holding a detached cylindrical lens assembly, matching the context of E2’s unmasked area which includes a monitor and keyboard layout consistent with E2’s visible frame. No such detail is visible in E1’s unmasked region.
- **printer_withheld:** In E1, the central rectangular display shows a visible blue screen with an icon, indicating illumination. In E2, the same area is dark and lacks any visible display content or glow.
- **camera_update:** The newly available fuller view shows hands holding a detached cylindrical lens assembly, matching the context of E2 (same keyboard layout and monitor edge visible). The right hand holds the lens; no cap is visible. E1 remains unknown as its gray rectangle still obscures the relevant area.
- **printer_prefix:** In E1, the central rectangular display shows a visible blue screen with an icon, indicating illumination. In E2, the same area is dark and lacks any visible display content or glow.

## Exact meaning of this test

Joint and update receive byte-identical final image panels. Only update also receives its own earlier answer. Thus a difference is an exploratory decision-history effect at equal visual evidence, not proof of a native streaming architecture defect.

Initial ambiguity is experimentally imposed by masks. Full views are original frames, not generated imagery. Replay status and capture order are provided; target record and its revealed value are not. Association is a controlled same-frame matching task. Successful latest-record output is not autonomous replay detection.

These are two independent recordings with one sampled episode each, not enough to estimate a population failure rate or establish novelty. No real-time latency claim; elapsed times include the public service queue. Recognition/schema errors and service errors are separate from semantic updating failures.

A PASS is a valid positive result for this controlled prototype. It must not be dismissed because it fails to support the desired failure hypothesis.

Saved requests: 10; completed responses: 10; infrastructure errors: 0.
Additional archived infrastructure attempts: 1. Total recorded attempts including these: 11.

## Post-hoc printer repeat check

These repeats were added after observing the original printer discrepancy. They reuse the exact original prompts, image and prefix memory; this measures downstream response variability on ONE episode, not independent data generalization. All scheduled repeats are shown.

| Trial | Joint score | Update score |
|---|---|---|
| original | pass | fail |
| repeat1 | unavailable | unavailable |
| repeat2 | unavailable | unavailable |

**Repeat execution status: blocked_by_automatic_approval_review.** Automatic approval review requires separate authorization for four additional post-hoc inference uploads beyond the approved ten conditions and recovery retry. No repeat result may be claimed.
