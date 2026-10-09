# Retrospective evidence: source qualification and bounded diagnostic

## Purpose
Find an earlier event with an initially poor view and a later, more revealing view of that same event. This is a closer test of the original question than changes in a table's assembly state. The aim is to test the hypothesis, not manufacture a failure.

## Candidate audit

| Candidate | What was actually inspected | Decision |
|---|---|---|
| NBA Celtics–Lakers, hand contact on rebound | Full clip sampled at 1 fps, plus full-resolution contact frame at 43 s. Initial wide view followed by several alternate-angle replays. NBA description independently identifies hand contact. | Selected for a ONE-case diagnostic. Human prefix ambiguity remains provisional; educational editing is not original livestream continuity. |
| NBA Knicks–76ers, January 24, 2026, out-of-bounds review | Contact sheet of a 21 s clip with wide view and closer replays. Official archive records overturned possession. | Deferred: possession ruling does not by itself identify the physical last touch; further frame review and factual annotation needed. |
| NFL Joey Blount overturned recovery TD | Full 57 s clip sampled at 1 fps; original play, multiple close replays, referee ruling at end. | Deferred: exact physical reason for overturn not yet independently established. Do not infer knee-before-release from the title. |
| NBA Dallas–Minnesota, May 24, 2024 | Official written explanation and video metadata; media download failed. | Not visually validated. Rule change would confound an unspecified possession question. |

Sources:
- https://videorulebook.nba.com/archive/out-of-bounds-violation-hand-as-part-of-the-ball-on-an-out-of-bounds-play/
- https://official.nba.com/archive/challenge-oob-knicks-76ers/
- https://www.nfl.com/videos/joey-blount-has-an-unreal-fumble-recovery-td-overturned-after-replay-review
- https://official.nba.com/nba-expands-use-of-instant-replay-on-out-of-bounds-reviews/

## Selected case
Question: during the contested rebound, does the reaching white player's hand contact the green player's hand holding the ball, or directly the ball?

Official reference: hand. Initial segment: source [0,9) s. Later segment: [39,47) s. These are nonadjacent excerpts in the original order, omitting intermediate replays deliberately for this controlled two-segment test. Both retain the source resolution, motion and frame rate; audio is removed to avoid narration leakage. Scoreboards/identities remain visible, so memorization is not ruled out. The later view makes the hands much larger, but fine contact remains visually difficult. Two independent human annotators have NOT qualified this pair.

Four conditions: prefix only; later evidence only; both segments together; later evidence plus the model's own prefix response. The latter uses external text memory and is not a native persistent video stream. It therefore tests one implementation of retrospective updating, not all streaming VLMs. Both recognition controls must pass before interpreting an update failure as a candidate temporal-memory problem. A control failure blocks that interpretation.

The prompt's auxiliary boolean and event-count schema includes example values. These fields are therefore cued and **must not be used as evidence of preservation or replay-counting ability**. Only the contact field is the primary diagnostic, with all three categories enumerated rather than an expected category supplied. The target is explicitly asked at each stage; this does not measure spontaneous discovery or spontaneous revision.

## Reproduce
Run from this directory:
```bash
python3 -m pip install gradio_client==1.8.0 'httpx[socks]'
python3 prepare.py
python3 run.py
```
FFmpeg is required. The public backend is not pinned and may be unavailable or change. Saved responses are reused, including errors; there are no automatic retries. Raw prompts, responses, input hashes and elapsed times are retained. `protocol.json` is written before any model request. Media, web-page copies and review contact sheets are excluded from Git; this is not a redistribution license for the source videos.

## Claim boundary
Even a successful four-call diagnostic establishes neither a new benchmark's novelty nor a general failure rate. Before a benchmark go decision: independent source qualification, multiple domains, new-event and wrong-event controls, matched information/memory budgets, and replicated runs on stable backends are still required.
