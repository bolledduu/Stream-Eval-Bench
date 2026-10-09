# Two-clip arrival-order diagnostic

This is a five-call exploratory experiment on one HoloAssist table assembly recording. It is not a benchmark or evidence of population-level failure rates.

Source: `z060-june-28-22-gladom_assemble.mp4`, redistributed in lmms-lab/EgoIT-99K at revision `a57f1f2078a7b01ea87014050fdb3afe169e54f1`. Original source SHA-256: `0f45226c0138d890cfb474fea4f387e865c6731acc083bf32147dc93da8a3b39`.

Earlier packet samples capture seconds 64.019, 67.993, 71.934, 75.908. Later packet samples 112.009, 114.647, 117.285, 119.924. Each MP4 encodes four real frames at one frame per second. Source time and playback time differ and are disclosed in every prompt. Around 72 seconds the tray is off the frame; at the later endpoint it rests on the frame. Labels were checked visually by the researcher, not by independent annotators.

Frozen conditions: both packets together; earlier then later; later then earlier. Streaming calls receive only the incoming packet and the previous model-produced JSON response. Each request uses a fresh client/session. The two conditions have equal visual evidence and update counts, but opposite order. The together control has a different context structure and is a qualification check, not a matched streaming baseline.

Expected final output in all conditions: `{"earlier":"no","latest":"yes"}`. Expected first chronological output: `{"earlier":"no","latest":"no"}`. Expected first delayed output: `{"earlier":"unknown","latest":"yes"}`.

Run `pip install gradio_client==1.8.0 'httpx[socks]'`, then run `python run.py` five times. Each invocation runs only the next unfinished request and saves its raw prompt, response, timing, and media hashes. An error is recorded and does not count as a completed response. The public service may change or become unavailable; its weight revision and decoding randomness are not exposed. The saved app code from the previous pilot declares Qwen3-VL-235B-A22B-Instruct, but that is not a guarantee about the live backend.

Interpretation: correct together and chronological outputs but an incorrect delayed output would be a candidate order effect. All correct outputs provide no positive evidence of that failure on this example. Incorrect together or chronological outputs prevent isolating the proposed delayed-evidence mechanism. A single trial cannot establish robustness, novelty, or conference suitability. This experiment supplies capture times and explicitly instructs preservation of newer facts; it does not test replay detection or autonomous event matching. Its external two-field memory also differs from a native streaming VLM architecture.
