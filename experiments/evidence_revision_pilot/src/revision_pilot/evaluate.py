"""Score option letters; keep provisional controls separate from verified core cases."""

import re


def parse_choice(text, labels):
    match = re.match(r"^\s*(?:Answer\s*:\s*)?([A-Z])(?:\s*$|[.):](?:\s|$))", text, re.I)
    return (
        match.group(1).upper() if match and match.group(1).upper() in labels else None
    )


def score_row(case, response):
    choice = parse_choice(response, set(case["options"]))
    expected = case.get("expected")
    return {
        "parsed_choice": choice,
        "expected": expected,
        "correct": choice == expected if expected is not None else None,
        "protocol_failure": choice is None,
        "annotation_status": case["annotation_status"],
        "core_revision_eligible": case.get("core_revision_eligible", False),
    }


def summarize(rows):
    scored = [r for r in rows if r["score"]["correct"] is not None]
    core = [
        r
        for r in scored
        if r["score"]["core_revision_eligible"]
        and r["score"]["annotation_status"] == "independently_verified"
    ]
    return {
        "completed_calls": len(rows),
        "provisional_scored_calls": len(scored),
        "provisional_correct": sum(r["score"]["correct"] for r in scored),
        "protocol_failures": sum(r["score"]["protocol_failure"] for r in rows),
        "verified_core_revision_calls": len(core),
        "verified_core_revision_accuracy": sum(r["score"]["correct"] for r in core)
        / len(core)
        if core
        else None,
        "conclusion": "No verified core episode: central hypothesis remains untested.",
    }
