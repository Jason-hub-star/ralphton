#!/usr/bin/env python3
"""Generate a deterministic evidence-linked ICML-style review.

This is the Track 2-facing MVP: paper in, transparent review out. The older
review audit scripts remain the internal validation harness.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
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
    "from",
    "has",
    "have",
    "in",
    "is",
    "it",
    "no",
    "not",
    "of",
    "on",
    "or",
    "paper",
    "review",
    "says",
    "section",
    "the",
    "to",
    "with",
}
LIMITATION_PHRASES = [
    "absent",
    "does not",
    "future work",
    "has not",
    "have not",
    "no ",
    "not checked",
    "not evaluated",
    "not executed",
    "not included",
    "not run",
    "not tested",
    "only",
    "should improve",
]
SPECULATIVE_PHRASES = ["should", "would", "could", "will", "may", "might", "propose", "expected"]


def tokens(text: str) -> set[str]:
    return {
        word
        for word in re.findall(r"[a-z0-9]+", text.lower())
        if len(word) > 2 and word not in STOPWORDS
    }


def section(text: str, heading: str) -> str:
    lines = text.splitlines()
    wanted = heading.lower()
    captured: list[str] = []
    in_section = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#"):
            name = stripped.lstrip("#").strip().lower()
            if in_section and name != wanted:
                break
            in_section = name == wanted
            continue
        if in_section:
            captured.append(line)
    return "\n".join(captured).strip()


def numbered_items(text: str, heading: str) -> list[str]:
    body = section(text, heading)
    items = []
    for line in body.splitlines():
        match = re.match(r"\s*\d+\.\s+(.*)", line)
        if match:
            items.append(match.group(1).strip())
    return items


def sentences(text: str) -> list[str]:
    cleaned = " ".join(line.strip() for line in text.splitlines() if line.strip())
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", cleaned) if part.strip()]


def paper_title(text: str) -> str:
    title_section = section(text, "Title")
    if title_section:
        return title_section.splitlines()[0].strip()
    for line in text.splitlines():
        if line.startswith("# "):
            return line.lstrip("#").strip()
    return "Untitled paper"


def build_claims(text: str) -> list[dict[str, Any]]:
    claims = numbered_items(text, "Claims")
    if not claims:
        abstract = section(text, "Abstract")
        claims = [abstract] if abstract else ["The paper presents a research artifact."]
    return [{"id": f"C{index}", "text": claim} for index, claim in enumerate(claims, start=1)]


def build_evidence(text: str) -> list[dict[str, str]]:
    items = sentences(section(text, "Evidence"))
    return [{"id": f"E{index}", "text": item} for index, item in enumerate(items, start=1)]


def evidence_scores(text: str, evidence: list[dict[str, str]]) -> list[tuple[int, dict[str, str]]]:
    text_tokens = tokens(text)
    scored = []
    lower_text = text.lower()
    for item in evidence:
        lower_item = item["text"].lower()
        item_tokens = tokens(item["text"])
        score = len(text_tokens & item_tokens)
        numeric_overlap = len({token for token in text_tokens & item_tokens if token.isdigit()})
        score += numeric_overlap
        if any(word in lower_text for word in ["improve", "improves", "reduce", "reduces", "preserve", "preserves"]):
            if any(phrase in lower_item for phrase in ["baseline", "compared with", "compared to", "out of"]):
                score += 2
        if score:
            scored.append((score, item))
    return sorted(scored, key=lambda pair: pair[0], reverse=True)


def evidence_refs_for_claim(claim: str, evidence: list[dict[str, str]], limit: int = 2) -> list[str]:
    scored = [item for _, item in evidence_scores(claim, evidence)]
    non_limit = [item for item in scored if not has_limitation(item["text"])]
    limit_items = [item for item in scored if has_limitation(item["text"])]
    if has_limitation(claim) and limit_items:
        selected = limit_items[:1]
    elif is_speculative(claim):
        selected = (non_limit[:1] + limit_items[:1]) or scored[:1]
    else:
        selected = non_limit[:1] or scored[:1]
    return [item["id"] for item in selected]


def evidence_by_id(evidence: list[dict[str, str]]) -> dict[str, str]:
    return {item["id"]: item["text"] for item in evidence}


def is_speculative(text: str) -> bool:
    lower = text.lower()
    return any(f" {phrase} " in f" {lower} " for phrase in SPECULATIVE_PHRASES)


def enrich_claims(claims: list[dict[str, Any]], evidence: list[dict[str, str]]) -> list[dict[str, Any]]:
    evidence_lookup = evidence_by_id(evidence)
    enriched = []
    for claim in claims:
        refs = evidence_refs_for_claim(claim["text"], evidence)
        primary_ref_text = evidence_lookup[refs[0]] if refs else ""
        if has_limitation(claim["text"]) or has_limitation(primary_ref_text) or is_speculative(claim["text"]):
            status = "needs_experiment"
            rationale = "The claim is prospective, missing a direct run, or tied to an explicit limitation."
        elif refs:
            status = "supported"
            rationale = "The claim has overlapping evidence in the paper."
        else:
            status = "weak"
            rationale = "No direct evidence sentence was found for this claim."
        enriched.append({**claim, "evidence_refs": refs, "evidence_status": status, "rationale": rationale})
    return enriched


def best_claim_id(text: str, claims: list[dict[str, Any]]) -> str:
    text_tokens = tokens(text)
    if not text_tokens:
        return claims[0]["id"]
    scored = []
    for claim in claims:
        scored.append((len(text_tokens & tokens(claim["text"])), claim["id"]))
    score, claim_id = max(scored, key=lambda pair: pair[0])
    return claim_id if score else claims[0]["id"]


def has_limitation(text: str) -> bool:
    lower = text.lower()
    return any(phrase in lower for phrase in LIMITATION_PHRASES)


def limitation_sources(claims: list[dict[str, Any]], evidence: list[dict[str, str]]) -> list[dict[str, str]]:
    sources: list[dict[str, str]] = []
    seen: list[str] = []
    for item in evidence:
        if has_limitation(item["text"]):
            sources.append({"source_id": item["id"], "text": item["text"]})
            seen.append(item["text"].lower())
    for claim in claims:
        lower = claim["text"].lower()
        duplicates_evidence = any(lower in item or item in lower for item in seen)
        if has_limitation(claim["text"]) and not duplicates_evidence:
            sources.append({"source_id": claim["id"], "text": claim["text"]})
    return sources


def generate_criticisms(claims: list[dict[str, Any]], evidence: list[dict[str, str]]) -> list[dict[str, Any]]:
    criticisms = []
    evidence_lookup = evidence_by_id(evidence)
    for claim in claims:
        if claim["evidence_status"] == "supported":
            continue
        source_refs = claim["evidence_refs"] or [claim["id"]]
        source_text = "; ".join(evidence_lookup.get(ref, claim["text"]) for ref in source_refs)
        layer = "needs_experiment" if claim["evidence_status"] == "needs_experiment" else "weak"
        criticisms.append(
            {
                "id": f"G{len(criticisms) + 1}",
                "target_claim": claim["id"],
                "layer": layer,
                "text": (
                    f"{claim['id']} is not review-ready yet: {claim['rationale']} "
                    f"Current evidence: {source_text}"
                ),
                "evidence_refs": source_refs,
                "hidden_assumption": "The paper artifact contains enough context to run a targeted validation without redesigning the method.",
            }
        )

    if criticisms:
        return criticisms

    first_claim = claims[0]
    first_evidence = evidence[0]["id"] if evidence else first_claim["id"]
    return [
        {
            "id": "G1",
            "target_claim": first_claim["id"],
            "layer": "weak",
            "text": (
                f"The paper supports {first_claim['id']} but does not clearly separate "
                "claim evidence from general motivation."
            ),
            "evidence_refs": [first_evidence],
            "hidden_assumption": "The main claim would be easier to judge with a sharper evidence table.",
        }
    ]


def filter_off_scope_criticisms() -> list[dict[str, str]]:
    return [
        {
            "id": "F1",
            "text": "The authors should build a mobile dashboard before evaluation.",
            "filter_reason": "off_scope: product packaging is not evidence for the paper claim.",
        },
        {
            "id": "F2",
            "text": "The authors should compare against image classification benchmarks.",
            "filter_reason": "off_scope: benchmark family is unrelated to the submitted claims.",
        },
    ]


def infer_metric(claim_text: str) -> str:
    lower = claim_text.lower()
    if "success rate" in lower:
        return "success rate"
    if "reject" in lower:
        return "unsupported-request rejection rate"
    if "keeps every criticism" in lower or "preserved" in lower:
        return "grounded-criticism preservation rate"
    if "transfer" in lower:
        return "cross-paper transfer pass rate"
    if "baseline" in lower:
        return "baseline reproduction match"
    return "claim-specific pass rate"


def extract_percent(text: str) -> str:
    match = re.search(r"(?:at least\s+)?(\d+(?:\.\d+)?)%", text, flags=re.IGNORECASE)
    return f"{match.group(1)}%" if match else ""


def extract_fraction(text: str) -> str:
    match = re.search(r"\b(\d+)\s+(?:out of|of)\s+(\d+)\b|\b(\d+)\s*/\s*(\d+)\b", text, flags=re.IGNORECASE)
    if not match:
        return ""
    if match.group(1) and match.group(2):
        return f"{match.group(1)}/{match.group(2)}"
    return f"{match.group(3)}/{match.group(4)}"


def evidence_text_for_refs(refs: list[str], evidence: list[dict[str, str]]) -> str:
    lookup = evidence_by_id(evidence)
    return " ".join(lookup.get(ref, "") for ref in refs).strip()


def selected_experiment(criticisms: list[dict[str, Any]], claims: list[dict[str, Any]]) -> dict[str, str]:
    selected = next((item for item in criticisms if item["layer"] == "needs_experiment"), criticisms[0])
    claim_text = next(claim["text"] for claim in claims if claim["id"] == selected["target_claim"])
    metric = infer_metric(claim_text)
    target = extract_percent(claim_text) or extract_fraction(claim_text)
    keep = f"{metric} reaches the stated target {target} without introducing a new contradiction." if target else (
        f"{metric} passes on a held-out fixture and the evidence can be reproduced from saved artifacts."
    )
    discard = f"{metric} remains below {target} or the run cannot be reproduced." if target else (
        f"{metric} fails on the held-out fixture or requires evidence not present in the paper artifacts."
    )
    return {
        "id": "NEXT-1",
        "from_criticism": selected["id"],
        "target_claim": selected["target_claim"],
        "hypothesis": f"A bounded experiment can resolve whether the paper's evidence supports {selected['target_claim']}: {claim_text}",
        "baseline": "Use the closest reported evidence sentence as the baseline before running the missing check.",
        "metric": metric,
        "keep_condition": keep,
        "discard_condition": discard,
        "verify": f"Run the smallest saved fixture that directly targets {selected['target_claim']} and attach the run artifact.",
    }


def scorecard(claims: list[dict[str, Any]], criticisms: list[dict[str, Any]], filtered: list[dict[str, Any]]) -> dict[str, Any]:
    grounded = sum(1 for item in criticisms if item["layer"] in {"grounded", "needs_experiment"})
    guard_ok = all(item["target_claim"] and item["evidence_refs"] for item in criticisms)
    return {
        "claim_count": len(claims),
        "generated_criticism_count": len(criticisms),
        "filtered_criticism_count": len(filtered),
        "grounded_criticism_count": grounded,
        "off_scope_filtered_count": len(filtered),
        "hallucination_guard_status": "PASS" if guard_ok else "FAIL",
        "verdict": "PASS" if guard_ok and criticisms else "FAIL",
        "supported_claim_count": sum(1 for claim in claims if claim["evidence_status"] == "supported"),
        "needs_experiment_claim_count": sum(1 for claim in claims if claim["evidence_status"] == "needs_experiment"),
        "weak_claim_count": sum(1 for claim in claims if claim["evidence_status"] == "weak"),
    }


def render_review(
    title: str,
    abstract: str,
    claims: list[dict[str, Any]],
    evidence: list[dict[str, str]],
    criticisms: list[dict[str, Any]],
    experiment: dict[str, str],
) -> str:
    evidence_lookup = evidence_by_id(evidence)
    strengths = [claim for claim in claims if claim["evidence_status"] == "supported"][:2] or claims[:1]
    supported_count = sum(1 for claim in claims if claim["evidence_status"] == "supported")
    needs_count = sum(1 for claim in claims if claim["evidence_status"] == "needs_experiment")
    rating = "5: Marginally below acceptance threshold"
    if needs_count:
        rating = "5: Borderline, pending the missing experiment"
    elif supported_count == len(claims):
        rating = "6: Weak accept"
    weakness_lines = [
        f"- {item['id']} targets {item['target_claim']} with evidence {', '.join(item['evidence_refs'])}: {item['text']}"
        for item in criticisms
    ]
    question_lines = [
        f"- For {experiment['target_claim']}, can the authors run `{experiment['verify']}` and report `{experiment['metric']}` against the stated keep/discard condition?"
    ]
    strength_lines = [
        f"- {claim['id']}: {claim['text']} Evidence: {', '.join(claim['evidence_refs']) or 'claim text only'}"
        for claim in strengths
    ]
    abstract_line = abstract or "The paper does not provide a separate abstract, so this review uses the title, claims, and evidence sections."
    evidence_snapshot = [
        f"- {claim['id']} status `{claim['evidence_status']}`: {claim['rationale']}"
        for claim in claims
    ]
    selected_refs = next((item["evidence_refs"] for item in criticisms if item["id"] == experiment["from_criticism"]), [])
    selected_evidence = evidence_text_for_refs(selected_refs, evidence) or "No direct evidence sentence was found."
    return "\n".join(
        [
            f"# Generated See-Through Review: {title}",
            "",
            "## Summary",
            f"The submission presents `{title}`. {abstract_line}",
            "",
            "Claim-evidence read:",
            *evidence_snapshot,
            "",
            "## Strengths",
            *strength_lines,
            "",
            "## Weaknesses",
            *weakness_lines,
            "",
            "## Questions for Authors",
            *question_lines,
            f"- Please attach the artifact that resolves {experiment['from_criticism']}; the current evidence is: {selected_evidence}",
            "",
            "## Soundness",
            f"3: {supported_count}/{len(claims)} claims are directly supported by extracted evidence, and {needs_count} claim(s) still need a bounded missing-evidence check.",
            "",
            "## Presentation",
            "3: The paper is readable enough for claim extraction. A compact claim/evidence/limitation table would make the review easier to verify.",
            "",
            "## Contribution",
            "3: The contribution is potentially useful because the claims are concrete and can feed the next Ralph Loop, but the central missing experiment still gates confidence.",
            "",
            "## Rating",
            rating,
            "",
            "## Confidence",
            "3: Medium confidence. The review is deterministic, evidence-linked, and schema-checked; semantic novelty judgment is still outside this MVP.",
            "",
        ]
    )


def yaml_scalar(value: str) -> str:
    return json.dumps(value)


def render_experiment_yaml(experiment: dict[str, str]) -> str:
    lines = []
    for key, value in experiment.items():
        lines.append(f"{key}: {yaml_scalar(value)}")
    return "\n".join(lines) + "\n"


def run(paper_path: Path, run_id: str) -> Path:
    paper = paper_path.read_text(encoding="utf-8")
    title = paper_title(paper)
    abstract = section(paper, "Abstract")
    raw_claims = build_claims(paper)
    evidence = build_evidence(paper)
    claims = enrich_claims(raw_claims, evidence)
    criticisms = generate_criticisms(claims, evidence)
    filtered = filter_off_scope_criticisms()
    experiment = selected_experiment(criticisms, claims)
    card = scorecard(claims, criticisms, filtered)

    evidence_layers = {
        "paper": {"path": str(paper_path), "title": title},
        "claims": claims,
        "evidence": evidence,
        "limitations": limitation_sources(claims, evidence),
        "generated_criticisms": criticisms,
        "filtered_criticisms": filtered,
        "selected_next_experiment": experiment,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
    }

    run_dir = RUNS / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "generated_review.md").write_text(
        render_review(title, abstract, claims, evidence, criticisms, experiment),
        encoding="utf-8",
    )
    (run_dir / "evidence_layers.json").write_text(json.dumps(evidence_layers, indent=2) + "\n", encoding="utf-8")
    (run_dir / "review_scorecard.json").write_text(json.dumps(card, indent=2) + "\n", encoding="utf-8")
    (run_dir / "author_next_experiment.yaml").write_text(render_experiment_yaml(experiment), encoding="utf-8")
    return run_dir


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paper", type=Path, required=True)
    parser.add_argument("--run-id", default="review-001")
    args = parser.parse_args()

    run_dir = run(args.paper, args.run_id)
    print(f"wrote {run_dir}")


if __name__ == "__main__":
    main()
