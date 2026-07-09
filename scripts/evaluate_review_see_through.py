#!/usr/bin/env python3
"""Evaluate Review See-Through against labeled fixtures."""

from __future__ import annotations

import argparse
import json
import shutil
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

import review_see_through as rst


ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "runs"
LABELS = ["grounded", "weak", "off_scope", "contradicted", "needs_experiment"]
REPORT_FILES = ["metrics.json", "confusion_matrix.md", "case_table.md", "scorecard.log"]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def pct(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 4) if denominator else 0.0


def verdict_for_case(correct: int, total: int, next_ok: bool) -> str:
    if correct == total and next_ok:
        return "PASS"
    if correct >= max(1, total - 1) and next_ok:
        return "PARTIAL"
    return "FAIL"


def evaluate_case(case_dir: Path, case_run_root: Path) -> dict[str, Any]:
    paper = (case_dir / "paper.md").read_text(encoding="utf-8")
    review = (case_dir / "review.md").read_text(encoding="utf-8")
    labels = load_json(case_dir / "labels.json")
    run_dir = rst.run_case(case_dir.name, paper, review, base_dir=case_run_root)
    payload = load_json(run_dir / "review_layers.json")

    expected_by_id = {item["criticism_id"]: item for item in labels["criticisms"]}
    predicted_by_id = {item["id"]: item for item in payload["review_layers"]}
    selected = payload["selected_experiment"]["from_review"]
    raw_selected = payload["review_layers"][0]["id"] if payload["review_layers"] else ""

    rows = []
    correct = 0
    for criticism_id, expected in expected_by_id.items():
        predicted = predicted_by_id.get(criticism_id)
        predicted_layer = predicted["layer"] if predicted else "missing"
        predicted_claims = predicted["target_claims"] if predicted else []
        expected_layer = expected["expected_layer"]
        expected_claims = expected["target_claims"]
        is_correct = predicted_layer == expected_layer
        target_claim_correct = sorted(predicted_claims) == sorted(expected_claims)
        correct += int(is_correct)
        rows.append(
            {
                "case_id": case_dir.name,
                "criticism_id": criticism_id,
                "expected_layer": expected_layer,
                "predicted_layer": predicted_layer,
                "expected_claims": expected_claims,
                "predicted_claims": predicted_claims,
                "correct": is_correct,
                "target_claim_correct": target_claim_correct,
                "error_type": "ok" if is_correct else f"{expected_layer}->{predicted_layer}",
                "should_be_next_experiment": bool(expected["should_be_next_experiment"]),
                "selected_as_next": criticism_id == selected,
                "raw_baseline_selected": criticism_id == raw_selected,
                "rationale": expected["rationale"],
            }
        )

    next_ok = any(row["should_be_next_experiment"] and row["selected_as_next"] for row in rows)
    raw_next_ok = any(row["should_be_next_experiment"] and row["raw_baseline_selected"] for row in rows)
    return {
        "case_id": case_dir.name,
        "run_dir": str(run_dir),
        "rows": rows,
        "correct": correct,
        "total": len(rows),
        "next_ok": next_ok,
        "raw_next_ok": raw_next_ok,
        "verdict": verdict_for_case(correct, len(rows), next_ok),
    }


def confusion_matrix(rows: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    matrix: dict[str, dict[str, int]] = {label: {inner: 0 for inner in LABELS + ["missing"]} for label in LABELS}
    for row in rows:
        expected = row["expected_layer"]
        predicted = row["predicted_layer"]
        matrix.setdefault(expected, {inner: 0 for inner in LABELS + ["missing"]})
        matrix[expected][predicted] = matrix[expected].get(predicted, 0) + 1
    return matrix


def write_confusion_matrix(path: Path, matrix: dict[str, dict[str, int]]) -> None:
    header = ["expected \\ predicted"] + LABELS + ["missing"]
    lines = ["# Confusion Matrix", "", "| " + " | ".join(header) + " |", "|" + "|".join(["---"] * len(header)) + "|"]
    for expected in LABELS:
        row = [expected] + [str(matrix.get(expected, {}).get(predicted, 0)) for predicted in LABELS + ["missing"]]
        lines.append("| " + " | ".join(row) + " |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_case_table(path: Path, cases: list[dict[str, Any]], rows: list[dict[str, Any]]) -> None:
    lines = [
        "# Case Table",
        "",
        "| case | verdict | correct/total | see-through next ok | raw first-criticism ok |",
        "|---|---|---:|---|---|",
    ]
    for case in cases:
        lines.append(
            f"| {case['case_id']} | {case['verdict']} | {case['correct']}/{case['total']} | "
            f"{case['next_ok']} | {case['raw_next_ok']} |"
        )

    lines.extend(
        [
            "",
            "## Criticism Rows",
            "",
            "| case | criticism | expected | predicted | correct | target claims ok | see-through selected | raw selected |",
            "|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in rows:
        lines.append(
            f"| {row['case_id']} | {row['criticism_id']} | {row['expected_layer']} | "
            f"{row['predicted_layer']} | {row['correct']} | {row['target_claim_correct']} | {row['selected_as_next']} | "
            f"{row['raw_baseline_selected']} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def summarize(cases: list[dict[str, Any]], rows: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(rows)
    correct = sum(1 for row in rows if row["correct"])
    target_claim_correct = sum(1 for row in rows if row["target_claim_correct"])
    expected_counts = Counter(row["expected_layer"] for row in rows)
    error_counts = Counter(row["error_type"] for row in rows if row["error_type"] != "ok")

    off_scope_total = expected_counts["off_scope"]
    off_scope_caught = sum(1 for row in rows if row["expected_layer"] == "off_scope" and row["predicted_layer"] == "off_scope")

    grounded_total = expected_counts["grounded"]
    grounded_preserved = sum(1 for row in rows if row["expected_layer"] == "grounded" and row["predicted_layer"] == "grounded")

    selected_total = sum(1 for row in rows if row["selected_as_next"])
    selected_true = sum(1 for row in rows if row["selected_as_next"] and row["should_be_next_experiment"])
    raw_selected_total = sum(1 for row in rows if row["raw_baseline_selected"])
    raw_selected_true = sum(1 for row in rows if row["raw_baseline_selected"] and row["should_be_next_experiment"])
    see_through_next = pct(selected_true, selected_total)
    raw_next = pct(raw_selected_true, raw_selected_total)

    return {
        "case_count": len(cases),
        "criticism_count": total,
        "layer_accuracy": pct(correct, total),
        "target_claim_accuracy": pct(target_claim_correct, total),
        "error_summary": dict(error_counts),
        "off_scope_catch_rate": pct(off_scope_caught, off_scope_total),
        "grounded_preservation_rate": pct(grounded_preserved, grounded_total),
        "next_experiment_precision": see_through_next,
        "raw_review_baseline": "first criticism in the raw review",
        "raw_next_experiment_precision": raw_next,
        "see_through_next_experiment_gain": round(see_through_next - raw_next, 4),
        "case_verdicts": {case["case_id"]: case["verdict"] for case in cases},
        "label_distribution": dict(expected_counts),
    }


def evaluate(fixtures: Path, run_id: str) -> Path:
    run_dir = RUNS / run_id
    case_run_root = run_dir / "cases"
    run_dir.mkdir(parents=True, exist_ok=True)

    case_dirs = sorted(path for path in fixtures.iterdir() if path.is_dir())
    cases = [evaluate_case(case_dir, case_run_root) for case_dir in case_dirs]
    rows = [row for case in cases for row in case["rows"]]
    matrix = confusion_matrix(rows)
    metrics = summarize(cases, rows)
    metrics["confusion_matrix"] = matrix
    metrics["generated_at"] = datetime.now().isoformat(timespec="seconds")

    (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    write_confusion_matrix(run_dir / "confusion_matrix.md", matrix)
    write_case_table(run_dir / "case_table.md", cases, rows)

    score = (
        f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] run={run_id} "
        f"cases={metrics['case_count']} criticisms={metrics['criticism_count']} "
        f"layer_accuracy={metrics['layer_accuracy']:.4f} "
        f"target_claim_accuracy={metrics['target_claim_accuracy']:.4f} "
        f"off_scope_catch_rate={metrics['off_scope_catch_rate']:.4f} "
        f"grounded_preservation_rate={metrics['grounded_preservation_rate']:.4f} "
        f"next_experiment_precision={metrics['next_experiment_precision']:.4f} "
        f"raw_next_experiment_precision={metrics['raw_next_experiment_precision']:.4f} "
        f"see_through_next_experiment_gain={metrics['see_through_next_experiment_gain']:.4f}\n"
    )
    (run_dir / "scorecard.log").write_text(score, encoding="utf-8")
    return run_dir


def unique_archive_dir(run_id: str, timestamp: str) -> Path:
    base = RUNS / "archive" / f"{timestamp}_{run_id}"
    candidate = base
    suffix = 1
    while candidate.exists():
        candidate = RUNS / "archive" / f"{timestamp}_{run_id}_{suffix}"
        suffix += 1
    return candidate


def archive_run(run_dir: Path, fixtures: Path, run_id: str) -> Path:
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
    archive_dir = unique_archive_dir(run_id, timestamp)
    archive_dir.mkdir(parents=True)

    for name in REPORT_FILES:
        shutil.copy2(run_dir / name, archive_dir / name)

    metrics = load_json(run_dir / "metrics.json")
    manifest = {
        "run_id": run_id,
        "timestamp": timestamp,
        "fixtures": str(fixtures),
        "archive_path": str(archive_dir),
        "source_run_dir": str(run_dir),
        "report_files": REPORT_FILES,
    }
    (archive_dir / "run_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    current_dir = RUNS / "current"
    current_dir.mkdir(parents=True, exist_ok=True)
    (current_dir / f"{run_id}.txt").write_text(str(archive_dir) + "\n", encoding="utf-8")

    ledger_row = {
        "run_id": run_id,
        "timestamp": timestamp,
        "fixtures": str(fixtures),
        "archive_path": str(archive_dir),
        "layer_accuracy": metrics["layer_accuracy"],
        "target_claim_accuracy": metrics.get("target_claim_accuracy"),
        "next_experiment_precision": metrics["next_experiment_precision"],
        "raw_next_experiment_precision": metrics.get("raw_next_experiment_precision"),
        "see_through_next_experiment_gain": metrics.get("see_through_next_experiment_gain"),
        "case_verdicts": metrics["case_verdicts"],
        "error_summary": metrics.get("error_summary", {}),
    }
    index_path = RUNS / "index.jsonl"
    with index_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(ledger_row, sort_keys=True) + "\n")

    return archive_dir


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate Review See-Through fixtures.")
    parser.add_argument("--fixtures", default="fixtures")
    parser.add_argument("--run-id", default="eval-001")
    parser.add_argument("--archive", action="store_true", help="Append an immutable copy under runs/archive and update run ledger.")
    args = parser.parse_args()

    fixtures = Path(args.fixtures)
    if not fixtures.is_absolute():
        fixtures = ROOT / fixtures
    run_dir = evaluate(fixtures, args.run_id)
    print(f"Wrote {run_dir}")
    if args.archive:
        archive_dir = archive_run(run_dir, fixtures, args.run_id)
        print(f"Archived {archive_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
