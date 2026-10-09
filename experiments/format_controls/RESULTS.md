# Endpoint recognition controls: complete

Six calls completed on the public demo declaring Qwen3-VL-235B-A22B-Instruct. No errors or retries. All expected labels were visually screened before inference.

| Recording | Endpoint image | Four-frame video | Expected |
|---|---|---|---|
| camera | yes | yes | yes |
| table | no | no | no |
| printer | no | no | no |

Camera: lens visibly mounted on camera body at the endpoint of existing camera_1 packet. Table: tray separate from frame at endpoint of existing table_1 packet. Printer: no illuminated interface on the large central LCD at source time approximately 43 seconds; surrounding illuminated buttons are irrelevant.

Camera/table reuse prior hashed PNG/MP4 inputs. Printer uses frames extracted at requested source times 40,41,42,43 seconds, scaled to 512x288 and encoded with libx264 CRF10 at 1fps. Its endpoint PNG is the last pre-encoding frame. Source recording hashes are in ../source_suitability/source_audit.json.

Interpretation: all three endpoint states were recognized in these straightforward questions. This rules out a blanket claim that the service cannot process our videos or recognize these states. It does not establish accurate time grounding or association inside larger contexts. It does not reveal internal provider sampling or prove that every frame was used.

These are diagnostic controls, not independent replications of the original hypothesis. Image requests contain only the endpoint, whereas video requests include preceding frames and lossy encoding; differences would not uniquely isolate input-format effects. The camera contains a state transition; the table and printer have stable target endpoint states. The wording and task differ from prior historical-update requests, so this is not a clean causal ablation of those failures.

Expected labels are assistant-screened, not independently human-validated. One call per condition, three source episodes, one public backend with unpinned weights/decoding. Six correct answers do not support population-level reliability claims.

Run: install ../two_clip_diagnostic/requirements.txt, then execute run.py. It resumes stored responses. Use a separate copy with an empty responses directory for an independent rerun; preserve the original results. Raw prompts, responses, expected labels, hashes and elapsed times are in results.json. The protocol and scoring rule were saved before calls.
