#!/usr/bin/env python3
"""Summarize archived Review See-Through runs."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "runs"
REPORT_FILES = ["metrics.json", "confusion_matrix.md", "case_table.md", "scorecard.log", "run_manifest.json"]
METRICS = [
    "layer_accuracy",
    "target_claim_accuracy",
    "next_experiment_precision",
    "raw_next_experiment_precision",
    "see_through_next_experiment_gain",
]


def load_index(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        row = json.loads(line)
        row["_line"] = line_no
        rows.append(row)
    return rows


def metric(row: dict[str, Any], name: str) -> float:
    value = row.get(name)
    return float(value) if value is not None else 0.0


def best_run(rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not rows:
        return None
    return max(
        rows,
        key=lambda row: (
            metric(row, "next_experiment_precision"),
            metric(row, "layer_accuracy"),
            metric(row, "target_claim_accuracy"),
            metric(row, "see_through_next_experiment_gain"),
            row.get("timestamp", ""),
        ),
    )


def latest_run(rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    return max(rows, key=lambda row: row.get("timestamp", "")) if rows else None


def trend(rows: list[dict[str, Any]]) -> dict[str, float]:
    if len(rows) < 2:
        return {}
    ordered = sorted(rows, key=lambda row: row.get("timestamp", ""))
    first = ordered[0]
    last = ordered[-1]
    return {name: round(metric(last, name) - metric(first, name), 4) for name in METRICS}


def aggregate_errors(rows: list[dict[str, Any]]) -> Counter:
    counts: Counter = Counter()
    for row in rows:
        counts.update(row.get("error_summary", {}))
    return counts


def check_archive(row: dict[str, Any]) -> list[str]:
    issues = []
    archive_path = Path(row.get("archive_path", ""))
    if not archive_path.exists():
        return [f"missing archive path: {archive_path}"]
    for name in REPORT_FILES:
        if not (archive_path / name).is_file():
            issues.append(f"missing {archive_path / name}")
    manifest_path = archive_path / "run_manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("run_id") != row.get("run_id"):
            issues.append(f"manifest run_id mismatch: {manifest_path}")
        if manifest.get("archive_path") != str(archive_path):
            issues.append(f"manifest archive_path mismatch: {manifest_path}")
    return issues


def check_current_pointers(rows: list[dict[str, Any]], current_dir: Path) -> list[str]:
    issues = []
    latest_by_run: dict[str, dict[str, Any]] = {}
    for row in rows:
        run_id = row["run_id"]
        if run_id not in latest_by_run or row.get("timestamp", "") > latest_by_run[run_id].get("timestamp", ""):
            latest_by_run[run_id] = row
    for run_id, row in sorted(latest_by_run.items()):
        pointer = current_dir / f"{run_id}.txt"
        if not pointer.exists():
            issues.append(f"missing current pointer: {pointer}")
            continue
        pointed = pointer.read_text(encoding="utf-8").strip()
        if pointed != row["archive_path"]:
            issues.append(f"stale current pointer for {run_id}: {pointed}")
    return issues


def next_action(best: dict[str, Any] | None, integrity_ok: bool) -> str:
    if not integrity_ok:
        return "Fix archive integrity before adding more runs."
    if not best:
        return "Create the first archived evaluation run."
    if metric(best, "target_claim_accuracy") < 1.0:
        return "Improve target-claim mapping or add constrained extraction."
    if metric(best, "next_experiment_precision") < 1.0:
        return "Improve next-experiment selection."
    return "Add a new frozen validation batch and archive it."


def render_markdown(rows: list[dict[str, Any]], archive_issues: list[str], pointer_issues: list[str]) -> str:
    best = best_run(rows)
    latest = latest_run(rows)
    errors = aggregate_errors(rows)
    deltas = trend(rows)
    integrity_ok = not archive_issues and not pointer_issues

    lines = [
        "# Run Summary",
        "",
        f"- archived rows: {len(rows)}",
        f"- archive integrity: {'PASS' if integrity_ok else 'FAIL'}",
    ]
    if latest:
        lines.append(f"- latest run: {latest['run_id']} @ {latest['timestamp']}")
    if best:
        lines.append(
            f"- best run: {best['run_id']} @ {best['timestamp']} "
            f"(layer={metric(best, 'layer_accuracy'):.4f}, target={metric(best, 'target_claim_accuracy'):.4f}, "
            f"next={metric(best, 'next_experiment_precision'):.4f})"
        )
    lines.append(f"- next action: {next_action(best, integrity_ok)}")

    lines.extend(["", "## Recent Trend", "", "| metric | delta |", "|---|---:|"])
    for name in METRICS:
        lines.append(f"| {name} | {deltas.get(name, 0.0):+.4f} |")

    lines.extend(["", "## Error Summary", ""])
    if errors:
        lines.extend(["| error type | count |", "|---|---:|"])
        for name, count in sorted(errors.items()):
            lines.append(f"| {name} | {count} |")
    else:
        lines.append("No archived error_summary entries.")

    lines.extend(["", "## Archive Integrity", ""])
    if integrity_ok:
        lines.append("PASS: archive files and current pointers are present.")
    else:
        for issue in archive_issues + pointer_issues:
            lines.append(f"- {issue}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize archived Review See-Through runs.")
    parser.add_argument("--index", default=str(RUNS / "index.jsonl"))
    parser.add_argument("--current-dir", default=str(RUNS / "current"))
    parser.add_argument("--output")
    args = parser.parse_args()

    rows = load_index(Path(args.index))
    archive_issues = [issue for row in rows for issue in check_archive(row)]
    pointer_issues = check_current_pointers(rows, Path(args.current_dir))
    markdown = render_markdown(rows, archive_issues, pointer_issues)

    if args.output:
        Path(args.output).write_text(markdown, encoding="utf-8")
    print(markdown)
    return 1 if archive_issues or pointer_issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
