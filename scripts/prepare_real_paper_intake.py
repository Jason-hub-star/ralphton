#!/usr/bin/env python3
"""Prepare confirmed Track 1 papers for human-labeled real-fixture evaluation."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

import generate_see_through_review as generator


ROOT = Path(__file__).resolve().parents[1]


def draft_labels(paper_path: Path) -> dict[str, Any]:
    paper = paper_path.read_text(encoding="utf-8")
    claims = generator.enrich_claims(generator.build_claims(paper), generator.build_evidence(paper))
    evidence = generator.build_evidence(paper)
    criticisms = generator.generate_criticisms(claims, evidence)
    experiment = generator.selected_experiment(criticisms, claims)
    return {
        "label_source": "draft_from_current_generator_do_not_use_as_gold_without_human_review",
        "expected_claim_count": len(claims),
        "claims": [
            {
                "id": claim["id"],
                "expected_status": claim["evidence_status"],
                "expected_evidence_refs": claim["evidence_refs"],
                "human_review_required": True,
            }
            for claim in claims
        ],
        "limitations": [
            {
                "source_id": item["source_id"],
                "text_contains": item["text"][:80],
                "human_review_required": True,
            }
            for item in generator.limitation_sources(claims, evidence)
        ],
        "selected_next_experiment": {
            "target_claim": experiment["target_claim"],
            "human_review_required": True,
        },
    }


def prepare(papers: list[Path], output: Path, limit: int, overwrite: bool, dry_run: bool) -> list[str]:
    lines = []
    selected = papers[:limit]
    missing = [str(paper) for paper in selected if not paper.is_file()]
    if missing:
        raise FileNotFoundError(
            "paper file(s) not found (unmatched glob?): " + ", ".join(missing)
        )
    for index, paper in enumerate(selected, start=1):
        case_dir = output / f"case-{index:03d}"
        lines.append(f"{paper} -> {case_dir}")
        if dry_run:
            continue
        if case_dir.exists() and not overwrite:
            raise FileExistsError(f"{case_dir} already exists; pass --overwrite to replace it")
        case_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(paper, case_dir / "paper.md")
        labels = draft_labels(case_dir / "paper.md")
        (case_dir / "labels.draft.json").write_text(json.dumps(labels, indent=2) + "\n", encoding="utf-8")
    return lines


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("papers", nargs="+", type=Path)
    parser.add_argument("--output", type=Path, default=ROOT / "fixtures-real-pending")
    parser.add_argument("--limit", type=int, default=3)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    lines = prepare(args.papers, args.output, args.limit, args.overwrite, args.dry_run)
    for line in lines:
        print(line)
    if not args.dry_run:
        print("Wrote draft labels as labels.draft.json; review them before renaming to labels.json.")


if __name__ == "__main__":
    main()
