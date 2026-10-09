# Fixed-hypothesis prototype

## The question stays fixed

Can evidence received later improve a specific earlier record without changing a different record whose fact remains unknown?

This prototype tests that necessary sub-capability using two real HoloAssist recordings already in the codebase. It makes uncertainty and delayed revelation controlled experimental variables. It does not require finding a naturally occurring replay in ordinary assembly footage. It does not claim that the masks occurred in the source videos.

## Concrete tasks

| Recording | Earlier snapshots | What is hidden initially | Later evidence | Correct final record |
|---|---|---|---|---|
| Camera, `z176-sep-05-22-dslr` | E1 at 10.0142 s; E2 at 17.0241 s | The camera and detached part | Original unmasked E1 frame | E1=lens; E2=unknown |
| Printer, `R071-19July-BigPrinter` | E1 at 19.2864 s; E2 at approximately 42.65 s (exact indexed time in cases.json) | Central LCD region | Original unmasked E2 frame | E1=unknown; E2=dark |

E2 stays the latest capture in both cases. The initial unmasked E2 camera frame would show a cap and the initial printer E1 frame would show an illuminated display, but those frames are **not supplied** to this experiment. The correct answer is about evidence the model has actually received, not all facts known to the experimenter.

The source clips and extracted frames come from the existing pilot. Source URLs, hashes, source timestamps, masks and frame hashes remain in `../source_suitability/source_audit.json`, `../evidence_revision_pilot/direct_revision/protocol.json`, and local `cases.json`. The controlled fuller view matches one initial frame exactly outside the mask. It is therefore a lower-bound association task, not challenging cross-camera identity tracking.

## Five conditions per source

1. **Prefix:** two obscured observations. The model must produce its own unknown/unknown answer.
2. **Recognition:** the unmasked target frame alone. Can it see the fact?
3. **Joint:** obscured observations and the fuller target view together. Can it associate and update correctly without an earlier commitment?
4. **Update:** byte-identical image to joint, plus its own previously generated prefix answer. Can it revise its record?
5. **Withheld:** original obscured observations plus its prefix answer; no revealing frame. Does it avoid inventing a revelation?

The model is told that the additional view refers to one earlier observation. It must determine which one from visible context. We therefore do not score autonomous replay detection or new-event discrimination. An explicitly labelled replay diagnostic is worthwhile only as a first functional test; it cannot support claims about those untested abilities.

## Interpretation before looking at results

- Recognition failure: perception problem; not evidence of updating-specific failure.
- Joint association failure: static matching/reasoning problem; not evidence of incremental updating-specific failure.
- Qualified joint pass, update fail: candidate history-conditioned failure with equal visual evidence; replication required.
- Qualified update pass: the controlled prototype works on that case. Do not redefine the task to dismiss a positive result.
- Withheld update: unsupported inference; report separately.
- Service/schema error: no usable scientific answer for that condition.

The condition of interest holds the final visual evidence constant. This prevents the previous mistake of interpreting missing visual memory as a purely streaming-specific defect. It retains visual history and implements prior decision state as a model-produced text answer. It is **not** a native recurrent video model, continuous realtime video, long-term memory experiment, or a new method contribution. No 100% confidence, universal failure, novelty or conference acceptance claim follows from two episodes.

## Run

```bash
python3 -m pip install Pillow gradio_client==1.8.0 'httpx[socks]'
python3 prepare.py
python3 run.py
python3 analyze.py
python3 -m unittest test_scoring.py
```

The protocol and hashes are written before inference. Responses are atomic, include exact prompts, and are reused on resume. There are no automatic retries or selection based on model failures. Requests use separate sessions, at most two concurrent cases. Source provider app inspection confirmed image uploads are added to server-side session history; no answer labels are sent as metadata. Hosted weights and decoding remain uncontrolled.

If the qualified tests pass, the responsible decision is: **the basic mechanism works in these cases; do not claim it is broken.** Broader work would need justified natural cases or a pre-specified difficulty axis, rather than more calls seeking a desired failure.
