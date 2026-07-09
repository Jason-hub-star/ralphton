#!/usr/bin/env python3
"""Evaluate generated review extraction on Track 1-style paper fixtures."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import generate_see_through_review as generator


ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "runs"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def pct(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 4) if denominator else 0.0


def evaluate_case(case_dir: Path, run_id: str) -> dict[str, Any]:
    labels = load_json(case_dir / "labels.json")
    run_dir = generator.run(case_dir / "paper.md", f"{run_id}/cases/{case_dir.name}")
    payload = load_json(run_dir / "evidence_layers.json")
    scorecard = load_json(run_dir / "review_scorecard.json")

    predicted_claims = {claim["id"]: claim for claim in payload["claims"]}
    expected_claims = {claim["id"]: claim for claim in labels["claims"]}
    claim_count_ok = len(predicted_claims) == labels["expected_claim_count"]

    claim_rows = []
    status_correct = 0
    evidence_expected_total = 0
    evidence_hit_total = 0
    evidence_pred_total = 0
    evidence_pred_hit_total = 0
    for claim_id, expected in expected_claims.items():
        predicted = predicted_claims.get(claim_id, {})
        predicted_status = predicted.get("evidence_status", "missing")
        predicted_refs = set(predicted.get("evidence_refs", []))
        expected_refs = set(expected["expected_evidence_refs"])
        status_ok = predicted_status == expected["expected_status"]
        hits = len(predicted_refs & expected_refs)
        status_correct += int(status_ok)
        evidence_expected_total += len(expected_refs)
        evidence_hit_total += hits
        evidence_pred_total += len(predicted_refs)
        evidence_pred_hit_total += hits
        claim_rows.append(
            {
                "claim_id": claim_id,
                "expected_status": expected["expected_status"],
                "predicted_status": predicted_status,
                "status_ok": status_ok,
                "expected_evidence_refs": sorted(expected_refs),
                "predicted_evidence_refs": sorted(predicted_refs),
                "evidence_refs_ok": expected_refs.issubset(predicted_refs),
            }
        )

    predicted_limitations = payload["limitations"]
    limitation_hits = 0
    for expected in labels["limitations"]:
        for predicted in predicted_limitations:
            if (
                predicted.get("source_id") == expected["source_id"]
                and expected["text_contains"].lower() in predicted.get("text", "").lower()
            ):
                limitation_hits += 1
                break

    selected_target = payload["selected_next_experiment"].get("target_claim")
    selected_ok = selected_target == labels["selected_next_experiment"]["target_claim"]
    status_accuracy = pct(status_correct, len(expected_claims))
    evidence_recall = pct(evidence_hit_total, evidence_expected_total)
    evidence_precision = pct(evidence_pred_hit_total, evidence_pred_total)
    limitation_recall = pct(limitation_hits, len(labels["limitations"]))
    verdict = "PASS" if all(
        [
            claim_count_ok,
            status_accuracy == 1.0,
            evidence_recall >= 0.8,
            limitation_recall == 1.0,
            selected_ok,
            scorecard.get("hallucination_guard_status") == "PASS",
        ]
    ) else "FAIL"

    return {
        "case_id": case_dir.name,
        "run_dir": str(run_dir),
        "claim_count_ok": claim_count_ok,
        "claim_status_accuracy": status_accuracy,
        "evidence_ref_recall": evidence_recall,
        "evidence_ref_precision": evidence_precision,
        "limitation_recall": limitation_recall,
        "selected_target": selected_target,
        "selected_target_ok": selected_ok,
        "scorecard_verdict": scorecard.get("verdict"),
        "hallucination_guard_status": scorecard.get("hallucination_guard_status"),
        "claim_rows": claim_rows,
        "verdict": verdict,
    }


def summarize(cases: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "case_count": len(cases),
        "claim_count_accuracy": pct(sum(1 for case in cases if case["claim_count_ok"]), len(cases)),
        "claim_status_accuracy": round(sum(case["claim_status_accuracy"] for case in cases) / len(cases), 4),
        "evidence_ref_recall": round(sum(case["evidence_ref_recall"] for case in cases) / len(cases), 4),
        "evidence_ref_precision": round(sum(case["evidence_ref_precision"] for case in cases) / len(cases), 4),
        "limitation_recall": round(sum(case["limitation_recall"] for case in cases) / len(cases), 4),
        "selected_target_accuracy": pct(sum(1 for case in cases if case["selected_target_ok"]), len(cases)),
        "case_verdicts": {case["case_id"]: case["verdict"] for case in cases},
        "verdict": "PASS" if all(case["verdict"] == "PASS" for case in cases) else "FAIL",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
    }


def write_case_table(path: Path, cases: list[dict[str, Any]]) -> None:
    lines = [
        "# Real Fixture Case Table",
        "",
        "| case | verdict | claim count | status acc | evidence recall | evidence precision | limitation recall | selected target ok |",
        "|---|---|---|---:|---:|---:|---:|---|",
    ]
    for case in cases:
        lines.append(
            f"| {case['case_id']} | {case['verdict']} | {case['claim_count_ok']} | "
            f"{case['claim_status_accuracy']:.4f} | {case['evidence_ref_recall']:.4f} | "
            f"{case['evidence_ref_precision']:.4f} | {case['limitation_recall']:.4f} | "
            f"{case['selected_target_ok']} |"
        )

    lines.extend(
        [
            "",
            "## Claim Rows",
            "",
            "| case | claim | expected status | predicted status | status ok | expected refs | predicted refs | refs ok |",
            "|---|---|---|---|---|---|---|---|",
        ]
    )
    for case in cases:
        for row in case["claim_rows"]:
            lines.append(
                f"| {case['case_id']} | {row['claim_id']} | {row['expected_status']} | "
                f"{row['predicted_status']} | {row['status_ok']} | "
                f"{', '.join(row['expected_evidence_refs'])} | {', '.join(row['predicted_evidence_refs'])} | "
                f"{row['evidence_refs_ok']} |"
            )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def evaluate(fixtures: Path, run_id: str) -> Path:
    run_dir = RUNS / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    case_dirs = sorted(path for path in fixtures.iterdir() if path.is_dir())
    cases = [evaluate_case(case_dir, run_id) for case_dir in case_dirs]
    metrics = summarize(cases)

    (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    write_case_table(run_dir / "case_table.md", cases)
    score = (
        f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] run={run_id} "
        f"cases={metrics['case_count']} claim_count_accuracy={metrics['claim_count_accuracy']:.4f} "
        f"claim_status_accuracy={metrics['claim_status_accuracy']:.4f} "
        f"evidence_ref_recall={metrics['evidence_ref_recall']:.4f} "
        f"limitation_recall={metrics['limitation_recall']:.4f} "
        f"selected_target_accuracy={metrics['selected_target_accuracy']:.4f} "
        f"verdict={metrics['verdict']}\n"
    )
    (run_dir / "scorecard.log").write_text(score, encoding="utf-8")
    return run_dir


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixtures", type=Path, default=ROOT / "fixtures-real")
    parser.add_argument("--run-id", default="eval-real-001")
    args = parser.parse_args()

    run_dir = evaluate(args.fixtures, args.run_id)
    print(f"Wrote {run_dir}")


if __name__ == "__main__":
    main()
