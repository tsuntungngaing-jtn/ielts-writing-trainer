#!/usr/bin/env python3
"""Validate a structured IELTS feedback *artifact*, not IELTS scoring accuracy.

Standard-library only. The checks catch missing-input scoring, malformed band
values, invented verbatim quotes and non-actionable priority records.
"""
import argparse
import json
import sys
from pathlib import Path

TASK_CRITERION = {
    "academic_task1": "TA",
    "general_task1": "TA",
    "task2": "TR",
}
DRAFT_KINDS = {"independent", "revision", "assisted", "model", "unknown"}
LABEL = "unofficial_training_estimate"


def valid_band(value):
    """Accept null or 0..9 in half-band steps; reject bools."""
    if value is None:
        return True
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and 0 <= value <= 9
        and float(value * 2).is_integer()
    )


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def validate_report(report):
    errors = []
    if not isinstance(report, dict):
        return ["Report must be a JSON object."]

    task = report.get("task_type")
    if task not in TASK_CRITERION:
        return ["task_type must be academic_task1, general_task1 or task2."]
    main = TASK_CRITERION[task]
    fields = {main, "CC", "LR", "GRA"}

    prompt = report.get("prompt")
    essay = report.get("essay")
    if not isinstance(prompt, str):
        errors.append("prompt must be a string (empty if unavailable).")
        prompt = ""
    if not isinstance(essay, str):
        errors.append("essay must be a string.")
        essay = ""

    visual = report.get("visual_available")
    if not isinstance(visual, bool):
        errors.append("visual_available must be a boolean.")

    if report.get("score_label") != LABEL:
        errors.append("score_label must be unofficial_training_estimate.")
    if report.get("draft_kind") not in DRAFT_KINDS:
        errors.append("Invalid draft_kind.")
    if report.get("draft_kind") == "model":
        errors.append("Do not assign student-performance scores to AI model essays.")

    scores = report.get("scores")
    if not isinstance(scores, dict):
        return errors + ["scores must be an object."]
    expected = fields | {"overall"}
    if set(scores) != expected:
        errors.append("scores keys must be exactly " + ", ".join(sorted(expected)) + ".")
    for key in expected:
        if not valid_band(scores.get(key)):
            errors.append(f"Invalid band for {key}: expected null or 0..9 in 0.5 steps.")

    missing_context = not prompt.strip() or (
        task == "academic_task1" and visual is not True
    )
    if missing_context and scores.get(main) is not None:
        errors.append(f"{main} must be null without the full task context.")
    if missing_context and scores.get("overall") is not None:
        errors.append("overall must be null when task context is missing.")
    if scores.get("overall") is not None and any(
        scores.get(key) is None for key in fields
    ):
        errors.append("overall requires all four criteria to be scored.")

    evidence = report.get("evidence")
    seen = set()
    if not isinstance(evidence, list):
        errors.append("evidence must be an array.")
        evidence = []
    for index, item in enumerate(evidence):
        if not isinstance(item, dict):
            errors.append(f"evidence[{index}] must be an object.")
            continue
        criterion = item.get("criterion")
        if criterion not in fields:
            errors.append(f"evidence[{index}] uses a wrong criterion.")
        quote = item.get("quote")
        if not nonempty(quote) or quote not in essay:
            errors.append(f"evidence[{index}] quote is not verbatim in essay.")
        if not nonempty(item.get("finding")):
            errors.append(f"evidence[{index}] needs a finding.")
        if not nonempty(item.get("next_action")):
            errors.append(f"evidence[{index}] needs a next_action.")
        if criterion in fields and nonempty(quote) and quote in essay:
            seen.add(criterion)
    for criterion in fields:
        if scores.get(criterion) is not None and criterion not in seen:
            errors.append(f"Scored criterion {criterion} needs quoted essay evidence.")

    priorities = report.get("priorities")
    if not isinstance(priorities, list) or len(priorities) > 3:
        errors.append("priorities must be an array of at most three items.")
    else:
        for index, item in enumerate(priorities):
            if not isinstance(item, dict):
                errors.append(f"priorities[{index}] must be an object.")
                continue
            if not nonempty(item.get("issue")) or not nonempty(item.get("action")):
                errors.append(f"priorities[{index}] needs issue and action.")
            if "quote" in item and (
                not nonempty(item["quote"]) or item["quote"] not in essay
            ):
                errors.append(f"priorities[{index}] quote is not verbatim in essay.")
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path, help="JSON feedback artifact")
    args = parser.parse_args(argv)
    try:
        data = json.loads(args.report.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"Cannot load report: {exc}", file=sys.stderr)
        return 2
    errors = validate_report(data)
    if errors:
        for problem in errors:
            print("FAIL:", problem, file=sys.stderr)
        return 1
    print("PASS: structural checks only; band accuracy NOT validated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
