#!/usr/bin/env python3
"""Deterministic smoke test for Review See-Through.

This is intentionally small. It tests the artifact shape and loop behavior before
we replace the extraction layer with an LLM.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
RUNS = ROOT / "runs"
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "be",
    "by",
    "for",
    "in",
    "is",
    "it",
    "no",
    "not",
    "of",
    "on",
    "or",
    "so",
    "the",
    "to",
    "with",
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_numbered_items(text: str, heading: str) -> list[str]:
    lines = text.splitlines()
    in_section = False
    items: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            in_section = stripped == f"## {heading}"
            continue
        if in_section and stripped[:2] in {"1.", "2.", "3.", "4.", "5."}:
            items.append(stripped[3:].strip())
    return items


def build_claim_cards(paper: str) -> list[dict]:
    claims = extract_numbered_items(paper, "Claims")
    cards = []
    for index, claim in enumerate(claims, start=1):
        status = "supported"
        if "should improve" in claim.lower() or "at least 50%" in claim:
            status = "needs_experiment"
        cards.append(
            {
                "id": f"C{index}",
                "text": claim,
                "evidence_status": status,
            }
        )
    return cards


def has_any(text: str, phrases: list[str]) -> bool:
    return any(phrase in text for phrase in phrases)


def tokens(text: str) -> set[str]:
    return {word for word in re.findall(r"[a-z0-9]+", text.lower()) if len(word) > 2 and word not in STOPWORDS}


def best_claim(item: str, claims: list[dict]) -> dict | None:
    item_tokens = tokens(item)
    if not item_tokens:
        return claims[0] if claims else None
    scored = []
    for claim in claims:
        claim_tokens = tokens(claim["text"])
        scored.append((len(item_tokens & claim_tokens), claim))
    score, claim = max(scored, key=lambda pair: pair[0], default=(0, None))
    return claim if score else (claims[0] if claims else None)


def is_missing_claim(text: str) -> bool:
    return has_any(
        text.lower(),
        [
            "not evaluated",
            "not tested",
            "not included",
            "not used",
            "not run",
            "not compare",
            "not checked",
            "does not test",
            "no comparison",
            "no real",
            "no human",
            "no live",
            "has not been",
            "have not been",
            "future work",
            "absent",
        ],
    )


def review_denies_evidence(text: str) -> bool:
    lower = text.lower()
    return has_any(
        lower,
        [
            "does not report",
            "does not validate",
            "gives no evidence",
            "has no",
            "lacks",
            "never reports",
            "never report",
            "no evidence",
            "no retrieval",
            "no manual",
            "nothing about",
            "omits",
        ],
    )


def review_points_to_missing_experiment(text: str) -> bool:
    lower = text.lower()
    return has_any(
        lower,
        [
            "excluded",
            "is not checked",
            "is only tested",
            "lacks",
            "not checked",
            "not tested",
            "have not been tested",
            "only tested",
            "remains unclear",
            "skips",
        ],
    )


def classify_review_item(item: str, paper: str, claims: list[dict], index: int) -> dict:
    lower = item.lower()
    paper_lower = paper.lower()
    target = []
    layer = "weak"
    evidence = []
    hidden_assumption = ""
    next_action = ""
    matched_claim = best_claim(item, claims)

    if "does not report the bm25 baseline" in lower and "bm25 baseline" in paper_lower:
        target = ["C1", "C2"]
        layer = "contradicted"
        evidence.append("Paper explicitly reports the BM25 baseline and reranker result.")
        hidden_assumption = "Reviewer missed an explicit baseline table entry."
        next_action = "Do not spend the next loop on this criticism."
    elif "planner-only baseline" in lower and "planner-only baseline" in paper_lower:
        target = ["C2"]
        layer = "contradicted"
        evidence.append("Paper explicitly reports the planner-only baseline.")
        hidden_assumption = "Reviewer missed a reported baseline."
        next_action = "Do not spend the next loop on this criticism."
    elif "word-count normalization" in lower and "word-count normalization" in paper_lower:
        target = ["C2"]
        layer = "contradicted"
        evidence.append("Paper explicitly reports word-count normalization.")
        hidden_assumption = "Reviewer missed the normalization statement."
        next_action = "Do not spend the next loop on this criticism."
    elif "parser crashes" in lower and "zero parser crashes" in paper_lower:
        target = ["C3"]
        layer = "contradicted"
        evidence.append("Paper explicitly reports zero parser crashes.")
        hidden_assumption = "Reviewer missed a run-log result."
        next_action = "Do not spend the next loop on this criticism."
    elif "calibration curve" in lower and "calibration curve" in paper_lower:
        target = ["C2"]
        layer = "contradicted"
        evidence.append("Paper explicitly reports a calibration curve.")
        hidden_assumption = "Reviewer missed a reported calibration artifact."
        next_action = "Do not spend the next loop on this criticism."
    elif "does not report token counts" in lower and "token count" in paper_lower:
        target = ["C1"]
        layer = "contradicted"
        evidence.append("Paper explicitly reports token counts before and after compression.")
        hidden_assumption = "Reviewer missed the token count table."
        next_action = "Do not spend the next loop on this criticism."
    elif "never demonstrates" in lower and "off-scope" in paper_lower:
        target = ["C2"]
        layer = "contradicted"
        evidence.append("Paper reports a fixture where off-scope reviewer requests are avoided.")
        hidden_assumption = "Reviewer missed the fixture result."
        next_action = "Do not spend the next loop on this criticism."
    elif "live llm-generated" in lower and "no live llm-generated" in paper_lower:
        target = ["C3"]
        layer = "grounded"
        evidence.append("Paper explicitly says no live LLM-generated review test has been run.")
        hidden_assumption = "The same selector can be evaluated on live generated reviews."
        next_action = "Run the selector on a small live LLM-generated review fixture."
    elif "real conference reviews" in lower:
        target = ["C1"]
        layer = "needs_experiment"
        evidence.append("Paper does not report evaluation on real conference reviews.")
        hidden_assumption = "A small public or synthetic-converted conference-review fixture is available."
        next_action = "Evaluate on a small real-review fixture."
    elif "human reviewers prefer" in lower and "no human preference study" in paper_lower:
        target = ["C3"]
        layer = "grounded"
        evidence.append("Paper explicitly says no human preference study has been run.")
        hidden_assumption = "Preference quality requires human judgment, not only artifact completeness."
        next_action = "Run a small human preference study."
    elif "cost ablation" in lower and "cost ablation" in paper_lower:
        target = ["C3"]
        layer = "needs_experiment"
        evidence.append("Paper lists model-tier cost ablations as future work.")
        hidden_assumption = "Cost can change the preferred workflow even if quality holds."
        next_action = "Run a model-tier cost ablation."
    elif "long-horizon" in lower and "long-horizon" in paper_lower:
        target = ["C2"]
        layer = "needs_experiment"
        evidence.append("Paper does not include the long-horizon task suite.")
        hidden_assumption = "Longer tasks may expose tool-use failures hidden by short episodes."
        next_action = "Run a long-horizon task suite beyond 20 minutes."
    elif "adversarial reviewer personas" in lower:
        target = ["C3"]
        layer = "needs_experiment"
        evidence.append("Paper says adversarial reviewer personas have not been run.")
        hidden_assumption = "Adversarial reviewer styles may change routing behavior."
        next_action = "Run the router on adversarial reviewer personas."
    elif "no-compression" in lower:
        target = ["C3"]
        layer = "needs_experiment"
        evidence.append("Paper says no no-compression prompt comparison has been run.")
        hidden_assumption = "Compression must beat the simplest uncompressed baseline."
        next_action = "Compare against a no-compression review prompt."
    elif "does not run" in lower or "missing experiment" in lower:
        target = ["C3"]
        layer = "grounded" if "no post-fallback run" in paper_lower else "weak"
        evidence.append("Paper states that no post-fallback run has been executed yet.")
        hidden_assumption = "The saved fixture can evaluate the proposed fallback."
        next_action = "Run or dry-run the fallback on the 30-item fixture."
    elif "long-tail" in lower and ("does not include a long-tail" in paper_lower or "no long-tail" in paper_lower):
        target = ["C2"]
        layer = "needs_experiment"
        evidence.append("Paper does not include a long-tail query ablation.")
        hidden_assumption = "A long-tail slice is available or can be constructed from the fixture."
        next_action = "Run a long-tail query ablation."
    elif "multi-file" in lower and "future work" in paper_lower:
        target = ["C3"]
        layer = "needs_experiment"
        evidence.append("Paper lists multi-file refactors as future work.")
        hidden_assumption = "A small multi-file refactor fixture can be prepared."
        next_action = "Run the compressed prompt on a multi-file refactor fixture."
    elif "overfit" in lower or "single 30-item fixture" in lower:
        target = ["C3"]
        layer = "weak"
        evidence.append("Paper uses one 30-item fixture; generalization is not tested.")
        hidden_assumption = "A second fixture or split would reveal generalization risk."
        next_action = "Add a second fixture only after the first fallback run passes."
    elif (
        "benchmark may be too small" in lower
        or "synthetic reviews" in lower
        or "rare tool failures" in lower
        or "one repository" in lower
        or "transfer to other codebases" in lower
    ):
        target = ["C2"]
        layer = "weak"
        evidence.append("Paper evidence is fixture-limited but not contradicted.")
        hidden_assumption = "More cases may expose rare failures."
        next_action = "Defer broadening until the primary missing experiment is resolved."
    elif has_any(
        lower,
        [
            "image classification",
            "mobile app",
            "mobile notification app",
            "reviewer tone",
            "3d visualization",
            "3d citation graph",
            "audio narration",
            "gpu kernel",
            "incentive",
            "rewards",
            "visual camera calibration",
            "voice assistant",
            "satellite images",
        ],
    ):
        target = []
        layer = "off_scope"
        evidence.append("Review request is outside the paper's stated research claim or scope.")
        hidden_assumption = "Reviewer imported a requirement from a different task."
        next_action = "Ignore for this loop unless the paper adds image inputs."
    elif matched_claim and review_denies_evidence(lower) and not is_missing_claim(matched_claim["text"]):
        # ponytail: lexical overlap is cheap and deterministic; replace with schema-constrained extraction when wording variance outgrows fixtures.
        target = [matched_claim["id"]]
        layer = "contradicted"
        evidence.append("Paper claim text reports the item that the review says is absent.")
        hidden_assumption = "Reviewer missed or discounted an explicit paper claim."
        next_action = "Do not spend the next loop on this criticism."
    elif matched_claim and is_missing_claim(matched_claim["text"]) and review_points_to_missing_experiment(lower):
        target = [matched_claim["id"]]
        layer = "needs_experiment"
        evidence.append("Paper claim text marks this evaluation or comparison as missing.")
        hidden_assumption = "The missing evaluation can be turned into a bounded next-loop run."
        next_action = "Run the missing evaluation or comparison named by the claim."
    else:
        target = [matched_claim["id"]] if matched_claim else []
        layer = "weak"
        evidence.append("No deterministic fixture rule matched this criticism.")
        hidden_assumption = "Needs LLM-assisted mapping in the next version."
        next_action = "Route to manual review."

    return {
        "id": f"R{index}",
        "text": item,
        "target_claims": target,
        "layer": layer,
        "evidence": evidence,
        "hidden_assumption": hidden_assumption,
        "next_action": next_action,
    }


def build_review_layers(paper: str, review: str, claims: list[dict]) -> list[dict]:
    items = extract_numbered_items(review, "Weaknesses")
    return [classify_review_item(item, paper, claims, i) for i, item in enumerate(items, start=1)]


def select_experiment(layers: list[dict]) -> dict:
    priority = {"needs_experiment": 0, "grounded": 1, "weak": 2, "contradicted": 3, "off_scope": 4}
    candidates = [layer for layer in layers if layer["layer"] not in {"off_scope", "contradicted"}]
    selected = sorted(candidates, key=lambda item: priority.get(item["layer"], 9))[0]
    hypothesis = selected["next_action"].rstrip(".") or "Run the next bounded evidence check"
    return {
        "id": "E1",
        "from_review": selected["id"],
        "target_claim": selected["target_claims"][0] if selected["target_claims"] else "unknown",
        "hypothesis": hypothesis,
        "baseline": "current paper evidence",
        "metric": "claim-specific success metric",
        "keep_condition": "measurable improvement or direct support for the target claim",
        "discard_condition": "no measurable support or new regression evidence",
        "verify": selected["next_action"],
    }


def yaml_card(card: dict) -> str:
    lines = []
    for key, value in card.items():
        escaped = str(value).replace('"', '\\"')
        lines.append(f'{key}: "{escaped}"')
    return "\n".join(lines) + "\n"


def write_outputs(run_id: str, claims: list[dict], layers: list[dict], experiment: dict, base_dir: Path | None = None) -> Path:
    run_dir = (base_dir or RUNS) / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "run_id": run_id,
        "claims": claims,
        "review_layers": layers,
        "selected_experiment": experiment,
        "metrics": {
            "criticism_count": len(layers),
            "grounded_count": sum(1 for item in layers if item["layer"] == "grounded"),
            "weak_count": sum(1 for item in layers if item["layer"] == "weak"),
            "off_scope_count": sum(1 for item in layers if item["layer"] == "off_scope"),
            "contradicted_count": sum(1 for item in layers if item["layer"] == "contradicted"),
            "needs_experiment_count": sum(1 for item in layers if item["layer"] == "needs_experiment"),
        },
    }
    (run_dir / "review_layers.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    (run_dir / "experiment_card.yaml").write_text(yaml_card(experiment), encoding="utf-8")

    md_lines = [
        "# Evidence Layers",
        "",
        "## Claims",
        "",
    ]
    for claim in claims:
        md_lines.append(f"- {claim['id']} ({claim['evidence_status']}): {claim['text']}")
    md_lines.extend(["", "## Review Layers", ""])
    for layer in layers:
        md_lines.append(f"### {layer['id']} - {layer['layer']}")
        md_lines.append("")
        md_lines.append(layer["text"])
        md_lines.append("")
        md_lines.append(f"- targets: {', '.join(layer['target_claims']) or 'none'}")
        md_lines.append(f"- evidence: {'; '.join(layer['evidence'])}")
        md_lines.append(f"- hidden assumption: {layer['hidden_assumption']}")
        md_lines.append(f"- next action: {layer['next_action']}")
        md_lines.append("")
    md_lines.extend(
        [
            "## Selected Experiment",
            "",
            f"- id: {experiment['id']}",
            f"- from review: {experiment['from_review']}",
            f"- target claim: {experiment['target_claim']}",
            f"- metric: {experiment['metric']}",
            f"- keep: {experiment['keep_condition']}",
            f"- discard: {experiment['discard_condition']}",
            "",
        ]
    )
    (run_dir / "evidence_layers.md").write_text("\n".join(md_lines), encoding="utf-8")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    score = (
        f'[{now}] run={run_id} criticisms={len(layers)} '
        f'grounded={payload["metrics"]["grounded_count"]} '
        f'weak={payload["metrics"]["weak_count"]} '
        f'off_scope={payload["metrics"]["off_scope_count"]} '
        f'contradicted={payload["metrics"]["contradicted_count"]} '
        f'needs_experiment={payload["metrics"]["needs_experiment_count"]} '
        f'experiment={experiment["id"]} verdict=ready-for-next-loop\n'
    )
    (run_dir / "scorecard.log").write_text(score, encoding="utf-8")
    return run_dir


def run(run_id: str) -> Path:
    paper = read_text(EXAMPLES / "paper.md")
    review = read_text(EXAMPLES / "review.md")
    return run_case(run_id, paper, review)


def run_case(run_id: str, paper: str, review: str, base_dir: Path | None = None) -> Path:
    claims = build_claim_cards(paper)
    layers = build_review_layers(paper, review, claims)
    experiment = select_experiment(layers)
    return write_outputs(run_id, claims, layers, experiment, base_dir=base_dir)


def self_test() -> Path:
    run_dir = run("manual-001")
    payload = json.loads((run_dir / "review_layers.json").read_text(encoding="utf-8"))
    layers = payload["review_layers"]
    assert len(layers) == 3, "expected 3 review criticisms"
    assert any(item["layer"] == "grounded" for item in layers), "expected grounded criticism"
    assert any(item["layer"] == "weak" for item in layers), "expected weak criticism"
    assert any(item["layer"] == "off_scope" for item in layers), "expected off_scope criticism"
    assert payload["selected_experiment"]["id"] == "E1", "expected selected experiment"
    assert (run_dir / "scorecard.log").read_text(encoding="utf-8").strip(), "missing scorecard"
    return run_dir


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Review See-Through smoke test.")
    parser.add_argument("--run-id", default="manual-001")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    run_dir = self_test() if args.self_test else run(args.run_id)
    print(f"Wrote {run_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
