"""Audit actual source-frame bytes, recorded requests and reproduced scores."""

import hashlib, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from revision_pilot.media import sha256
from revision_pilot.evaluate import score_row


def main():
    cfg = json.loads((ROOT / "configs/pilot.json").read_text())
    report = json.loads((ROOT / "results/baselines.json").read_text())
    sources = {s["id"]: s for s in json.loads((ROOT / "sources.json").read_text())}
    cases = {c["id"]: c for c in cfg["cases"]}
    assert report["config_sha256"] == sha256(ROOT / "configs/pilot.json")
    expected = {(c["id"], v["name"]) for c in cfg["cases"] for v in cfg["conditions"]}
    actual = {(r["case_id"], r["condition"]) for r in report["results"]}
    assert len(report["results"]) == len(expected) and actual == expected
    checked = 0
    for row in report["results"]:
        case = cases[row["case_id"]]
        assert row["score"] == score_row(case, row["response"])
        request = {
            k: row[k]
            for k in ["case_id", "condition", "checkpoint", "frames", "prompt"]
        }
        assert (
            hashlib.sha256(json.dumps(request, sort_keys=True).encode()).hexdigest()
            == row["request_sha256"]
        )
        idx = ROOT / sources[case["source_id"]]["frame_index"]
        lookup = {f["sha256"]: f for f in json.loads(idx.read_text())["frames"]}
        for selected in row["frames"]:
            assert selected["time"] <= row["checkpoint"]
            f = lookup[selected["sha256"]]
            assert f["time"] == selected["time"]
            assert sha256(idx.parent / f["file"]) == selected["sha256"]
            checked += 1
    result = {
        "status": "passed",
        "complete_calls": len(actual),
        "frame_references_checked": checked,
        "scope": "engineering integrity only; labels and core-task eligibility not independently verified",
    }
    (ROOT / "results/audit.json").write_text(json.dumps(result, indent=2))
    print(result)


if __name__ == "__main__":
    main()
