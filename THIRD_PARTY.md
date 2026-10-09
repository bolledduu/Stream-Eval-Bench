# Third-party provenance

The original repository MIT license applies to original project code; it does not grant rights to third-party source videos, derived frames, model artifacts, or reference app code.

## Data samples

PNG frames and small MP4 packets derive from three HoloAssist sessions redistributed through `lmms-lab/EgoIT-99K`, pinned revision `a57f1f2078a7b01ea87014050fdb3afe169e54f1`. Dataset permissions and conditions remain those of the original providers. Consult their terms before further redistribution or use. This repository does not claim ownership of the source recordings.

- Source redistribution: https://huggingface.co/datasets/lmms-lab/EgoIT-99K/tree/a57f1f2078a7b01ea87014050fdb3afe169e54f1/HoloAssist
- Exact session URLs, timestamps, hashes, and acquisition records are preserved under `experiments/evidence_revision_pilot/`.
- Full source recordings and model weights are not included.

## Reference hosted application

`experiments/evidence_revision_pilot/streaming_trial/hosted/app.py` and its original `README.md` are copied reference material from Qwen's public demo, **not original project code**:

- https://huggingface.co/spaces/Qwen/Qwen3-VL-235B-A22B-Instruct-Demo/tree/eb7f245e2c0d3b573dd8ed6addca9b7f6af26847
- The upstream card declares Apache-2.0. Preserve upstream attribution and applicable license conditions.
- The app is retained to document the service interface and declared backend used during the experiment; live deployment behavior may differ.
