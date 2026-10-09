"""Frozen-config prefix-only comparison, exact inputs, raw outputs and hashes."""

import argparse, datetime, hashlib, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from revision_pilot.media import select_prefix, sha256
from revision_pilot.evaluate import score_row, summarize


def construct_prompt(case, history=None):
    prompt = (
        "The images are chronological observations from one continuous video. Use only the shown evidence.\n"
        + case["question"]
        + "\n"
    )
    prompt += "\n".join(f"{key}: {value}" for key, value in case["options"].items())
    prompt += "\nReturn only the letter of the best answer. Choose the insufficient-evidence option when the shown frames do not establish the answer."
    if history:
        prompt += "\nYour earlier answers (may be wrong):\n" + json.dumps(history)
    return prompt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/pilot.json")
    ap.add_argument("--model", default="model")
    ap.add_argument("--output", default="results/baselines.json")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    cfg = json.loads((ROOT / args.config).read_text())
    sources = {s["id"]: s for s in json.loads((ROOT / "sources.json").read_text())}
    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    histories = {}
    model = None
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    if not args.dry_run:
        from revision_pilot.model import LocalVLM

        model = LocalVLM(str(ROOT / args.model))
    for condition in cfg["conditions"]:
        for case in cfg["cases"]:
            source = sources[case["source_id"]]
            idxpath = ROOT / source["frame_index"]
            index = json.loads(idxpath.read_text())
            if case["checkpoint"] > source["duration_seconds"]:
                raise ValueError("Checkpoint past end")
            frames = (
                []
                if condition["policy"] == "text_only"
                else select_prefix(
                    index["frames"],
                    case["checkpoint"],
                    condition["budget"],
                    condition["policy"],
                    case.get("excluded_intervals", []),
                )
            )
            group = (condition["name"], case.get("trajectory_id", case["id"]))
            prompt = construct_prompt(
                case, histories.get(group) if condition["policy"] == "history" else None
            )
            request = {
                "case_id": case["id"],
                "condition": condition["name"],
                "checkpoint": case["checkpoint"],
                "frames": [{"time": f["time"], "sha256": f["sha256"]} for f in frames],
                "prompt": prompt,
            }
            response = None
            latency = None
            if model:
                response, latency = model.generate(
                    [(f["time"], idxpath.parent / f["file"]) for f in frames],
                    prompt,
                    cfg["max_new_tokens"],
                )
            rows.append(
                {
                    **request,
                    "request_sha256": hashlib.sha256(
                        json.dumps(request, sort_keys=True).encode()
                    ).hexdigest(),
                    "response": response,
                    "latency_seconds": latency,
                    "status": "model_returned" if model else "dry_run",
                    "score": score_row(case, response) if model else None,
                }
            )
            if model:
                histories.setdefault(group, []).append(
                    {"checkpoint": case["checkpoint"], "answer": response}
                )
            manifest = json.loads((ROOT / "provenance/model_files.json").read_text())
            report = {
                "started_utc": started,
                "protocol": "synchronous sampled-prefix; not wall-clock live evaluation",
                "config_sha256": sha256(ROOT / args.config),
                "model": manifest["model"],
                "model_revision": manifest["revision"],
                "environment": model.metadata if model else None,
                "results": rows,
                "summary": summarize(rows) if model else {"model_calls": 0},
            }
            out.write_text(json.dumps(report, indent=2))
            print(case["id"], condition["name"], repr(response), latency, flush=True)


if __name__ == "__main__":
    main()
