# Controlled historical-record update pilot

This is an original small evaluation harness, not a proposed novel method.
It uses six reference views from three HoloAssist recordings and constructed partial-to-full reveals. Each model call receives sampled still images in one request. Initial memory and replay status are supplied. It does not implement an end-to-end live video agent.

Read RESULTS.md for the corrected outcomes. The valid main run is results/qwen.json. The old cached run under results/invalidated_cached is invalidated: a real-image equivalence audit found that per-image features differed from normal joint-image encoding. The current experiment.py uses the unmodified model forward. The legacy vision_cache.py is retained only to document and reproduce the failed optimization; it is not used by the corrected experiment.

## Files

- protocol.json: frozen cases, labels, source timestamps, masks and image hashes.
- inputs/: exact full, masked and withheld PNGs.
- model_manifest.json: pinned Qwen model revision and weight checksums.
- restore_model.py: fetch precisely that snapshot and verify transfer checksums.
- experiment.py: five conditions; greedy local inference; raw response and field-level scoring; resume after each saved trial.
- analyze.py: verify protocol, prompts, input hashes and scores; deduplicate withheld controls.
- followups.py and camera_followups.py: separate post-hoc diagnostics, not pooled with the main run.
- simple_baselines.py: one-image and read-then-write controls on the selected table case. These are standard baselines, not novelty claims.
- audit_inputs.py: verify mask integrity and the trivial pixel-match baseline.
- audit_real_cache.py: historical audit that exposed the cache issue. Its original result is saved; do not use it as the active experiment runner.
- test_design.py: checks preservation scoring and paired-condition construction.
- results/invalidation.json: why the first execution was superseded.

## Reproduce

From the pilot parent directory, using Python 3.12:

```bash
python -m venv .venv
.venv/bin/pip install torch==2.6.0+cpu torchvision==0.21.0+cpu --index-url https://download.pytorch.org/whl/cpu
.venv/bin/pip install transformers==4.49.0 accelerate==1.4.0 Pillow==11.1.0
.venv/bin/python direct_revision/restore_model.py
.venv/bin/python -m unittest discover -s direct_revision -p test_design.py
.venv/bin/python direct_revision/audit_inputs.py
.venv/bin/python direct_revision/experiment.py
.venv/bin/python direct_revision/followups.py
.venv/bin/python direct_revision/camera_followups.py
.venv/bin/python direct_revision/simple_baselines.py
.venv/bin/python direct_revision/analyze.py
.venv/bin/python direct_revision/write_report.py
```

The main runner resumes existing results. To make a fresh independent execution, first preserve and move the existing results/qwen.json to a separate run directory. Do not merge it with another model or execution path. CPU latency is an implementation measurement, not evidence of real-time capability.

## Scope limits

Three source sessions do not establish a population failure rate. These labels are assistant-screened, not independently human-validated. Unknown-to-known completion is tested, not correction of a previously false belief. Same-frame reveals make pixel matching trivial. Actual continuous streaming, naturally delayed evidence, stronger models, and held-out domains remain untested. A high-confidence research gap or novelty claim is not established by this pilot.
