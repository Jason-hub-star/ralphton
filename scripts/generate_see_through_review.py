#!/usr/bin/env python3
"""Generate an evidence-linked ICML-style review.

Two-layer design:
- LLM brain (default on the CLI): claim/evidence extraction, criticism
  drafting, and off-scope self-review via scripts/llm_client.py.
- Deterministic guards (always on): schema shape, evidence-ref existence,
  verbatim quote verification against the paper, off-scope token-overlap
  partition, rubric-anchored scoring, and rendering.

The deterministic heuristic path is preserved as `--offline` (and as the
default when `run()` is called from the evaluation harnesses) so the
regression fixtures stay reproducible without network access.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "runs"
OFF_SCOPE_MIN_OVERLAP = 3
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
ETHICAL_KEYWORDS = [
    "human subject",
    "personal data",
    "personally identifiable",
    "patient",
    "medical record",
    "surveillance",
    "deanonym",
    "crowdworker",
]


def tokens(text: str) -> set[str]:
    return {
        word
        for word in re.findall(r"[a-z0-9]+", text.lower())
        if len(word) > 2 and word not in STOPWORDS
    }


def normalize_ws(text: str) -> str:
    return " ".join(text.split())


def quote_in_paper(quote: str, paper: str) -> bool:
    return bool(quote.strip()) and normalize_ws(quote) in normalize_ws(paper)


def section(text: str, heading: str) -> str:
    """Return the body of a heading, tolerating deeper sub-headings."""
    wanted = heading.lower()
    captured: list[str] = []
    in_section = False
    base_level = 0
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            level = len(stripped) - len(stripped.lstrip("#"))
            name = stripped.lstrip("#").strip().lower()
            if in_section:
                if level <= base_level:
                    break
                continue
            if name == wanted:
                in_section = True
                base_level = level
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


# ---------------------------------------------------------------------------
# Deterministic (offline) extraction path — regression baseline.
# ---------------------------------------------------------------------------


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


def evidence_refs_for_claim(claim: str, evidence: list[dict[str, str]]) -> list[str]:
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


def has_limitation(text: str) -> bool:
    lower = text.lower()
    return any(phrase in lower for phrase in LIMITATION_PHRASES)


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


# ---------------------------------------------------------------------------
# Off-scope filter (deterministic, applies to both paths).
# ---------------------------------------------------------------------------


def partition_off_scope(
    criticisms: list[dict[str, Any]],
    claims: list[dict[str, Any]],
    evidence: list[dict[str, str]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    paper_tokens: set[str] = set()
    for item in claims:
        paper_tokens |= tokens(item["text"])
    for item in evidence:
        paper_tokens |= tokens(item["text"])

    kept: list[dict[str, Any]] = []
    filtered: list[dict[str, Any]] = []
    for item in criticisms:
        if item.get("layer") == "off_scope":
            filtered.append({**item, "filter_reason": item.get("filter_reason", "off_scope: flagged during self-review")})
            continue
        overlap = len(tokens(item["text"]) & paper_tokens)
        if overlap < OFF_SCOPE_MIN_OVERLAP:
            filtered.append(
                {
                    **item,
                    "filter_reason": (
                        f"off_scope: only {overlap} content tokens overlap the paper's claims/evidence "
                        f"(threshold {OFF_SCOPE_MIN_OVERLAP})"
                    ),
                }
            )
        else:
            kept.append(item)
    return kept, filtered


# ---------------------------------------------------------------------------
# LLM path: extraction -> criticisms -> self-review, each behind guards.
# ---------------------------------------------------------------------------


class GuardError(Exception):
    """A stage output failed a deterministic guard."""


SYSTEM_TEMPLATE = """You are Review See-Through, an ICML-style review agent.
Ground every statement in the paper text below. Never invent quotes,
numbers, citations, or experiments that are not in the paper. Quotes must
be copied verbatim from the paper.

<paper>
{paper}
</paper>"""

STAGE1_INSTRUCTIONS = """Extract the paper's core structure.
- claims: 2 to 7 central claims the authors make (paraphrase is fine).
  For each claim: status is "supported" when the paper contains direct
  evidence for it, "needs_experiment" when the claim is prospective or an
  explicit limitation blocks it, "weak" when no direct evidence exists.
  evidence_indexes are 0-based indexes into your evidence array.
- evidence: verbatim sentences from the paper that carry results, numbers,
  comparisons, or explicit limitations. Copy them exactly.
- limitations: verbatim sentences stating limitations or missing work.
Return JSON only."""

STAGE1_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["claims", "evidence", "limitations"],
    "properties": {
        "claims": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["text", "status", "evidence_indexes", "rationale"],
                "properties": {
                    "text": {"type": "string"},
                    "status": {"type": "string", "enum": ["supported", "needs_experiment", "weak"]},
                    "evidence_indexes": {"type": "array", "items": {"type": "integer"}},
                    "rationale": {"type": "string"},
                },
            },
        },
        "evidence": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["quote"],
                "properties": {"quote": {"type": "string"}},
            },
        },
        "limitations": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["quote"],
                "properties": {"quote": {"type": "string"}},
            },
        },
    },
}

STAGE2_INSTRUCTIONS_TEMPLATE = """Here are the extracted claims and evidence (JSON):
{layers}

Write the review body.
- summary: 2-4 sentences describing what the paper does and finds.
- criticisms: 1 to 4 weaknesses. Each must reference one target_claim id,
  cite evidence_refs (E-ids), include a verbatim quote from the paper that
  the criticism rests on, name the hidden_assumption, and set layer:
  "grounded" (direct contradiction/gap in the paper), "needs_experiment"
  (resolvable by one bounded experiment), "weak" (soft concern), or
  "off_scope" (would require work outside the paper's scope — these are
  filtered out, so use it for criticisms you considered and rejected).
- prior_works: 1-3 sentences on how the paper relates to prior work,
  based only on what the paper itself cites or states. If the paper cites
  nothing, say so.
- originality / significance / clarity: one sentence each.
- questions: 1-3 numbered-style questions for the authors, each tied to a
  specific claim or missing piece of evidence.
Return JSON only."""

STAGE2_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["summary", "criticisms", "prior_works", "originality", "significance", "clarity", "questions"],
    "properties": {
        "summary": {"type": "string"},
        "criticisms": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["target_claim", "layer", "text", "evidence_refs", "quote", "hidden_assumption"],
                "properties": {
                    "target_claim": {"type": "string"},
                    "layer": {"type": "string", "enum": ["grounded", "needs_experiment", "weak", "off_scope"]},
                    "text": {"type": "string"},
                    "evidence_refs": {"type": "array", "items": {"type": "string"}},
                    "quote": {"type": "string"},
                    "hidden_assumption": {"type": "string"},
                },
            },
        },
        "prior_works": {"type": "string"},
        "originality": {"type": "string"},
        "significance": {"type": "string"},
        "clarity": {"type": "string"},
        "questions": {"type": "array", "items": {"type": "string"}},
    },
}

STAGE3_INSTRUCTIONS_TEMPLATE = """Here is the draft criticism list (JSON):
{criticisms}

Self-review each criticism as a skeptical meta-reviewer. A criticism must
be dropped (keep=false) when it asks for work outside the paper's scope,
restates a limitation the authors already acknowledge without adding a
check, or is not anchored in the quoted paper text.
Return JSON only."""

STAGE3_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["decisions"],
    "properties": {
        "decisions": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["id", "keep", "reason"],
                "properties": {
                    "id": {"type": "string"},
                    "keep": {"type": "boolean"},
                    "reason": {"type": "string"},
                },
            },
        }
    },
}


def _run_stage(
    call: Callable[[str], dict],
    instructions: str,
    guard: Callable[[dict], list[str]],
) -> dict:
    payload = call(instructions)
    problems = guard(payload)
    if not problems:
        return payload
    retry_instructions = (
        instructions
        + "\n\nYour previous answer failed these checks — fix them:\n- "
        + "\n- ".join(problems)
    )
    payload = call(retry_instructions)
    problems = guard(payload)
    if problems:
        raise GuardError("; ".join(problems))
    return payload


def guard_stage1(payload: dict, paper: str) -> list[str]:
    problems = []
    if not payload["claims"]:
        problems.append("at least one claim is required")
    evidence_count = len(payload["evidence"])
    for index, item in enumerate(payload["evidence"]):
        if not quote_in_paper(item["quote"], paper):
            problems.append(f"evidence[{index}] quote is not verbatim from the paper")
    for index, item in enumerate(payload["limitations"]):
        if not quote_in_paper(item["quote"], paper):
            problems.append(f"limitations[{index}] quote is not verbatim from the paper")
    for index, claim in enumerate(payload["claims"]):
        if any(ref < 0 or ref >= evidence_count for ref in claim["evidence_indexes"]):
            problems.append(f"claims[{index}] has an evidence_index out of range")
        if claim["status"] == "supported" and not claim["evidence_indexes"]:
            problems.append(f"claims[{index}] is 'supported' but cites no evidence")
    return problems


def guard_stage2(payload: dict, paper: str, claim_ids: set[str], evidence_ids: set[str]) -> list[str]:
    problems = []
    if not payload["criticisms"]:
        problems.append("at least one criticism is required")
    for index, item in enumerate(payload["criticisms"]):
        if item["target_claim"] not in claim_ids:
            problems.append(f"criticisms[{index}] targets unknown claim {item['target_claim']}")
        unknown = [ref for ref in item["evidence_refs"] if ref not in evidence_ids]
        if unknown:
            problems.append(f"criticisms[{index}] cites unknown evidence {unknown}")
        if not quote_in_paper(item["quote"], paper):
            problems.append(f"criticisms[{index}] quote is not verbatim from the paper")
    return problems


def llm_pipeline(paper: str) -> dict[str, Any]:
    from llm_client import complete_json

    system = SYSTEM_TEMPLATE.format(paper=paper)

    def call(schema: dict) -> Callable[[str], dict]:
        return lambda instructions: complete_json(system, instructions, schema)

    stage1 = _run_stage(call(STAGE1_SCHEMA), STAGE1_INSTRUCTIONS, lambda p: guard_stage1(p, paper))

    evidence = [
        {"id": f"E{index}", "text": item["quote"]}
        for index, item in enumerate(stage1["evidence"], start=1)
    ]
    claims = []
    for index, claim in enumerate(stage1["claims"], start=1):
        refs = [f"E{ref + 1}" for ref in claim["evidence_indexes"]]
        claims.append(
            {
                "id": f"C{index}",
                "text": claim["text"],
                "evidence_refs": refs,
                "evidence_status": claim["status"],
                "rationale": claim["rationale"],
            }
        )
    evidence_texts = {normalize_ws(item["text"]): item["id"] for item in evidence}
    limitations = [
        {"source_id": evidence_texts.get(normalize_ws(item["quote"]), "PAPER"), "text": item["quote"]}
        for item in stage1["limitations"]
    ]

    layers_json = json.dumps({"claims": claims, "evidence": evidence}, indent=2)
    claim_ids = {claim["id"] for claim in claims}
    evidence_ids = {item["id"] for item in evidence}
    stage2 = _run_stage(
        call(STAGE2_SCHEMA),
        STAGE2_INSTRUCTIONS_TEMPLATE.format(layers=layers_json),
        lambda p: guard_stage2(p, paper, claim_ids, evidence_ids),
    )

    criticisms = [
        {"id": f"G{index}", **item}
        for index, item in enumerate(stage2["criticisms"], start=1)
    ]

    stage3 = _run_stage(
        call(STAGE3_SCHEMA),
        STAGE3_INSTRUCTIONS_TEMPLATE.format(criticisms=json.dumps(criticisms, indent=2)),
        lambda p: [],
    )
    drop_reasons = {item["id"]: item["reason"] for item in stage3["decisions"] if not item["keep"]}
    for item in criticisms:
        if item["id"] in drop_reasons:
            item["layer"] = "off_scope"
            item["filter_reason"] = f"off_scope: {drop_reasons[item['id']]}"

    return {
        "claims": claims,
        "evidence": evidence,
        "limitations": limitations,
        "criticisms": criticisms,
        "summary": stage2["summary"],
        "prior_works": stage2["prior_works"],
        "originality": stage2["originality"],
        "significance": stage2["significance"],
        "clarity": stage2["clarity"],
        "questions": stage2["questions"],
    }


# ---------------------------------------------------------------------------
# Next-experiment selection (deterministic, both paths).
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Rubric-anchored scoring + ICML-form rendering.
# ---------------------------------------------------------------------------


def overall_recommendation(claims: list[dict[str, Any]], kept: list[dict[str, Any]]) -> tuple[int, str]:
    total = len(claims)
    supported = sum(1 for claim in claims if claim["evidence_status"] == "supported")
    needs = sum(1 for claim in claims if claim["evidence_status"] == "needs_experiment")
    weak = sum(1 for claim in claims if claim["evidence_status"] == "weak")
    ratio = supported / total if total else 0.0

    if ratio == 1.0 and not kept:
        return 5, f"Strong accept anchor: all {total} claims are directly supported and no grounded weakness survived review."
    if ratio >= 0.75 and weak == 0:
        return 4, (
            f"Accept anchor: {supported}/{total} claims are directly supported; the remaining "
            f"{needs} claim(s) are gated by one bounded, well-specified missing experiment."
        )
    if ratio >= 0.5:
        return 3, (
            f"Weak accept anchor: {supported}/{total} claims are supported, but {needs + weak} claim(s) "
            "still lack a direct run or direct evidence, so acceptance leans on the proposed next experiment."
        )
    if supported >= 1:
        return 2, (
            f"Weak reject anchor: only {supported}/{total} claims are supported; "
            f"{weak} claim(s) have no direct evidence in the paper."
        )
    return 1, f"Reject anchor: none of the {total} extracted claims are supported by direct evidence in the paper."


def ethical_issues_line(paper: str) -> str:
    lower = paper.lower()
    hits = sorted({keyword for keyword in ETHICAL_KEYWORDS if keyword in lower})
    if hits:
        return f"Potential areas to double-check based on paper text: {', '.join(hits)}. A human ethics reviewer should confirm."
    return "No ethical concerns were identified from the paper text."


def prior_works_fallback(paper: str) -> str:
    if section(paper, "References") or section(paper, "Related Work"):
        return (
            "The paper includes a references/related-work section; this review did not "
            "independently verify those citations against the literature."
        )
    return (
        "The paper does not include a references or related-work section, so novelty "
        "claims cannot be positioned against prior work from the paper text alone."
    )


STATUS_LABELS = {
    "supported": "Supported",
    "needs_experiment": "Partially supported (missing one bounded experiment)",
    "weak": "Unsupported (no direct evidence found)",
}


def render_review(
    title: str,
    paper: str,
    claims: list[dict[str, Any]],
    evidence: list[dict[str, str]],
    kept: list[dict[str, Any]],
    experiment: dict[str, str],
    extras: dict[str, Any],
) -> str:
    evidence_lookup = evidence_by_id(evidence)
    recommendation, anchor = overall_recommendation(claims, kept)

    claim_lines = []
    for claim in claims:
        refs = ", ".join(claim["evidence_refs"]) or "no evidence ref"
        claim_lines.append(
            f"- {claim['id']} — {STATUS_LABELS[claim['evidence_status']]} ({refs}): {claim['text']}"
        )
        for ref in claim["evidence_refs"]:
            if ref in evidence_lookup:
                claim_lines.append(f"  - {ref}: \"{evidence_lookup[ref]}\"")

    weakness_lines = []
    for item in kept:
        weakness_lines.append(
            f"- {item['id']} (targets {item['target_claim']}, evidence {', '.join(item['evidence_refs']) or 'none'}): {item['text']}"
        )
        if item.get("quote"):
            weakness_lines.append(f"  - Anchored in the paper text: \"{item['quote']}\"")
        weakness_lines.append(f"  - Hidden assumption: {item['hidden_assumption']}")
    if not weakness_lines:
        weakness_lines.append("- No grounded weakness survived the off-scope filter.")

    question_lines = [f"{index}. {question}" for index, question in enumerate(extras.get("questions", []), start=1)]
    next_index = len(question_lines) + 1
    question_lines.append(
        f"{next_index}. For {experiment['target_claim']}, can the authors run the smallest saved fixture "
        f"that directly targets this claim and report {experiment['metric']}, judged against the stated "
        "keep/discard condition below?"
    )

    summary_text = extras.get("summary") or (
        f"The submission presents `{title}`. "
        + (section(paper, "Abstract") or "The paper provides claims and evidence sections which this review analyzes.")
    )

    return "\n".join(
        [
            f"# ICML-Style Review: {title}",
            "",
            "## Summary",
            summary_text,
            "",
            "## Claims and Evidence",
            "Each central claim, its substantiation status, and the verbatim evidence it rests on:",
            *claim_lines,
            "",
            "Weaknesses (each linked to a claim and evidence layer):",
            *weakness_lines,
            "",
            "## Relation to Prior Works",
            extras.get("prior_works") or prior_works_fallback(paper),
            "",
            "## Other Aspects",
            f"- Originality: {extras.get('originality') or 'The contribution is narrow but concrete; originality is hard to place without verified citations.'}",
            f"- Significance: {extras.get('significance') or 'Significance rests on whether the central claims survive the one proposed missing experiment.'}",
            f"- Clarity: {extras.get('clarity') or 'The paper is structured enough for claim extraction; a compact claim/evidence/limitation table would improve verifiability.'}",
            "",
            "## Questions for Authors",
            *question_lines,
            "",
            "Proposed next experiment (keep/discard contract):",
            f"- Hypothesis: {experiment['hypothesis']}",
            f"- Metric: {experiment['metric']}",
            f"- Keep when: {experiment['keep_condition']}",
            f"- Discard when: {experiment['discard_condition']}",
            "",
            "## Ethical Issues",
            ethical_issues_line(paper),
            "",
            "## Overall Recommendation",
            f"{recommendation}: {anchor}",
            "",
        ]
    )


# ---------------------------------------------------------------------------
# Scorecard + run orchestration.
# ---------------------------------------------------------------------------


def scorecard(
    claims: list[dict[str, Any]],
    kept: list[dict[str, Any]],
    filtered: list[dict[str, Any]],
    paper: str,
    mode: str,
    degraded: bool,
    degraded_reason: str,
) -> dict[str, Any]:
    grounded = sum(1 for item in kept if item["layer"] in {"grounded", "needs_experiment"})
    guard_ok = all(item["target_claim"] and item["evidence_refs"] for item in kept)
    quotes = [item["quote"] for item in kept if item.get("quote")]
    quotes_verified = sum(1 for quote in quotes if quote_in_paper(quote, paper))
    if quotes and quotes_verified != len(quotes):
        guard_ok = False
    recommendation, _ = overall_recommendation(claims, kept)
    return {
        "mode": mode,
        "degraded": degraded,
        "degraded_reason": degraded_reason,
        "claim_count": len(claims),
        "generated_criticism_count": len(kept),
        "filtered_criticism_count": len(filtered),
        "grounded_criticism_count": grounded,
        "off_scope_filtered_count": len(filtered),
        "quote_span_count": len(quotes),
        "quote_span_verified_count": quotes_verified,
        "overall_recommendation": recommendation,
        "hallucination_guard_status": "PASS" if guard_ok else "FAIL",
        "verdict": "PASS" if guard_ok and kept else "FAIL",
        "supported_claim_count": sum(1 for claim in claims if claim["evidence_status"] == "supported"),
        "needs_experiment_claim_count": sum(1 for claim in claims if claim["evidence_status"] == "needs_experiment"),
        "weak_claim_count": sum(1 for claim in claims if claim["evidence_status"] == "weak"),
    }


def yaml_scalar(value: str) -> str:
    return json.dumps(value)


def render_experiment_yaml(experiment: dict[str, str]) -> str:
    lines = []
    for key, value in experiment.items():
        lines.append(f"{key}: {yaml_scalar(value)}")
    return "\n".join(lines) + "\n"


def heuristic_layers(paper: str) -> dict[str, Any]:
    raw_claims = build_claims(paper)
    evidence = build_evidence(paper)
    claims = enrich_claims(raw_claims, evidence)
    return {
        "claims": claims,
        "evidence": evidence,
        "limitations": limitation_sources(claims, evidence),
        "criticisms": generate_criticisms(claims, evidence),
    }


def run(paper_path: Path, run_id: str, use_llm: bool = False) -> Path:
    paper = paper_path.read_text(encoding="utf-8")
    title = paper_title(paper)

    mode = "heuristic"
    degraded = False
    degraded_reason = ""
    extras: dict[str, Any] = {}
    layers: dict[str, Any]

    if use_llm:
        try:
            layers = llm_pipeline(paper)
            extras = layers
            mode = "llm"
        except Exception as error:  # GuardError, LLMUnavailable, network, parsing
            layers = heuristic_layers(paper)
            degraded = True
            degraded_reason = f"{type(error).__name__}: {error}"
    else:
        layers = heuristic_layers(paper)

    claims = layers["claims"]
    evidence = layers["evidence"]
    kept, filtered = partition_off_scope(layers["criticisms"], claims, evidence)
    experiment_pool = kept or layers["criticisms"]
    experiment = selected_experiment(experiment_pool, claims)
    card = scorecard(claims, kept, filtered, paper, mode, degraded, degraded_reason)

    evidence_layers = {
        "paper": {"path": str(paper_path), "title": title},
        "mode": mode,
        "degraded": degraded,
        "claims": claims,
        "evidence": evidence,
        "limitations": layers["limitations"],
        "generated_criticisms": kept,
        "filtered_criticisms": filtered,
        "selected_next_experiment": experiment,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
    }

    run_dir = RUNS / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "generated_review.md").write_text(
        render_review(title, paper, claims, evidence, kept, experiment, extras),
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
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Force the deterministic heuristic path (no LLM calls).",
    )
    args = parser.parse_args()

    run_dir = run(args.paper, args.run_id, use_llm=not args.offline)
    card = json.loads((run_dir / "review_scorecard.json").read_text(encoding="utf-8"))
    print(f"wrote {run_dir} mode={card['mode']} degraded={card['degraded']} verdict={card['verdict']}")


if __name__ == "__main__":
    main()
