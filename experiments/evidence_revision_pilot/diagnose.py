"""Separate unscored prompt-sensitivity checks, not added to the frozen comparison."""

import json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from revision_pilot.model import LocalVLM
from revision_pilot.media import select_prefix


def main():
    model = LocalVLM(str(ROOT / "model"))
    rows = []
    specs = [
        (
            "camera_single_frame",
            "holo_1",
            12,
            1,
            "Describe the main object the person is holding in this image.",
        ),
        (
            "printer_single_frame",
            "holo_2",
            22,
            1,
            "Describe the main device visible in this image.",
        ),
        (
            "camera_eight_frames",
            "holo_1",
            12,
            8,
            "Describe the main object the person is handling in these chronological images.",
        ),
    ]
    for name, source, checkpoint, budget, prompt in specs:
        folder = ROOT / "frames" / source
        index = json.loads((folder / "index.json").read_text())
        frames = select_prefix(index["frames"], checkpoint, budget)
        response, latency = model.generate(
            [(f["time"], folder / f["file"]) for f in frames], prompt, 48
        )
        rows.append(
            {
                "diagnostic": name,
                "source_id": source,
                "checkpoint": checkpoint,
                "frames": frames,
                "prompt": prompt,
                "response": response,
                "latency_seconds": latency,
            }
        )
        (ROOT / "results/diagnostics.json").write_text(
            json.dumps(
                {
                    "status": "post-hoc unscored capability checks; not part of frozen comparison",
                    "results": rows,
                },
                indent=2,
            )
        )
        print(name, repr(response), flush=True)


if __name__ == "__main__":
    main()
