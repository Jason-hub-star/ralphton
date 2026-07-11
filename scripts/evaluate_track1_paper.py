#!/usr/bin/env python3
"""Deterministic gate for a Track 1 paper written by the Ralph loop.

The loop LLM is the author; this script is the judge (never edited by the
loop). It fails the paper unless:

1. Structure — required sections `## Title / Abstract / Claims / Evidence /
   Limitations` exist (extra sections allowed) and Claims is a numbered list
   of 3-8 items.
2. See-through rule — `## Evidence` contains a markdown table
   `| claim | metric | value | source |` where source is
   `<repo-relative-path>#<json-key>`; every row is verified by opening the
   JSON and comparing the value (rounded to the paper's precision). Sources
   must live under `runs/` but outside `runs/track1*` (the loop's own
   writable namespace), so cited numbers cannot be fabricated.
3. Claim-evidence link — every claim number has at least one verified table
   row, or the claim is marked `(needs experiment)`; at least one
   needs-experiment claim must exist (the review agent's next-experiment
   selector lands on it).
4. Hygiene — no TODO/TBD/FIXME/PLACEHOLDER/lorem-ipsum markers; Limitations
   lists at least two items.

Usage: python3 scripts/evaluate_track1_paper.py <paper.md> [--run-id ID]
Exit 0 on PASS, 1 on FAIL, 2 on usage errors.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime

REQUIRED_SECTIONS = ["title", "abstract", "claims", "evidence", "limitations"]
TABLE_COLUMNS = ["claim", "metric", "value", "source"]
NEEDS_EXPERIMENT_MARKER = "(needs experiment)"


def split_sections(text):
    """Map lowercase h2 heading -> list of body lines."""
    sections = {}
    current = None
    for line in text.splitlines():
        match = re.match(r"^##\s+(.+?)\s*$", line)
        if match:
            current = match.group(1).strip().lower()
            sections.setdefault(current, [])
        elif current is not None:
            sections[current].append(line)
    return sections


def parse_claims(lines):
    """Return [(number, item_text)] from a numbered markdown list."""
    claims = []
    for line in lines:
        match = re.match(r"^\s*(\d+)[.)]\s+(.*)$", line)
        if match:
            claims.append([int(match.group(1)), match.group(2)])
        elif claims and line.strip():
            claims[-1][1] += " " + line.strip()
    return [(num, text) for num, text in claims]


def parse_evidence_table(lines, problems):
    """Return list of row dicts keyed by TABLE_COLUMNS, or []."""
    rows = []
    header_idx = None
    table_lines = [ln for ln in lines if ln.strip().startswith("|")]
    if not table_lines:
        problems.append("evidence section has no markdown table")
        return rows

    def cells(line):
        return [c.strip().strip("`").strip() for c in line.strip().strip("|").split("|")]

    header = [c.lower() for c in cells(table_lines[0])]
    try:
        header_idx = {col: header.index(col) for col in TABLE_COLUMNS}
    except ValueError:
        problems.append(
            "evidence table header must contain columns %s (got %s)"
            % ("|".join(TABLE_COLUMNS), "|".join(header))
        )
        return rows

    for line in table_lines[1:]:
        row_cells = cells(line)
        if all(re.fullmatch(r":?-{2,}:?", c or "-") for c in row_cells):
            continue  # separator row
        if len(row_cells) < len(header):
            problems.append("evidence table row has too few cells: %s" % line.strip())
            continue
        rows.append({col: row_cells[header_idx[col]] for col in TABLE_COLUMNS})
    return rows


def lookup(data, dotted_key):
    node = data
    for part in dotted_key.split("."):
        if not isinstance(node, dict) or part not in node:
            raise KeyError(dotted_key)
        node = node[part]
    return node


def verify_row(row, problems):
    """Open row['source'] as <path>#<key> and compare with row['value']."""
    source = row["source"]
    if "#" not in source:
        problems.append("source %r is not <path>#<json-key>" % source)
        return False
    path, key = source.split("#", 1)
    normalized = os.path.normpath(path)
    if not normalized.startswith("runs/") or normalized.startswith("runs/track1") or ".." in normalized.split(os.sep):
        problems.append("source path %r must be under runs/ and outside runs/track1*" % path)
        return False
    if not os.path.isfile(normalized):
        problems.append("source file not found: %s" % path)
        return False
    try:
        with open(normalized) as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        problems.append("source %s is not readable JSON: %s" % (path, exc))
        return False
    try:
        actual = lookup(data, key)
    except KeyError:
        problems.append("key %r not found in %s" % (key, path))
        return False

    claimed = row["value"]
    try:
        claimed_num = float(claimed)
        actual_num = float(actual)
    except (TypeError, ValueError):
        if str(actual) != claimed:
            problems.append(
                "value mismatch for %s: paper says %r, ground truth is %r"
                % (source, claimed, actual)
            )
            return False
        return True
    decimals = len(claimed.split(".")[1]) if "." in claimed else 0
    if abs(round(actual_num, decimals) - claimed_num) > 1e-12:
        problems.append(
            "value mismatch for %s: paper says %s, ground truth is %s"
            % (source, claimed, actual)
        )
        return False
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paper")
    parser.add_argument("--run-id", default=None)
    args = parser.parse_args()

    if not os.path.isfile(args.paper):
        print("paper not found: %s" % args.paper, file=sys.stderr)
        return 2
    with open(args.paper) as handle:
        text = handle.read()

    problems = []

    # 1. Structure
    sections = split_sections(text)
    missing = [s for s in REQUIRED_SECTIONS if s not in sections]
    if missing:
        problems.append("missing required section(s): %s" % ", ".join(missing))
    claims = parse_claims(sections.get("claims", []))
    if not 3 <= len(claims) <= 8:
        problems.append("claims must be a numbered list of 3-8 items (got %d)" % len(claims))
    needs_experiment = {
        num for num, item in claims if NEEDS_EXPERIMENT_MARKER in item.lower()
    }
    if claims and not needs_experiment:
        problems.append("at least one claim must be marked %r" % NEEDS_EXPERIMENT_MARKER)

    # 2. See-through rule
    rows = parse_evidence_table(sections.get("evidence", []), problems)
    verified = sum(1 for row in rows if verify_row(row, problems))

    # 3. Claim-evidence link
    claim_ids = {num for num, _ in claims}
    cited = set()
    for row in rows:
        try:
            ref = int(row["claim"])
        except ValueError:
            problems.append("evidence row cites non-numeric claim %r" % row["claim"])
            continue
        if claim_ids and ref not in claim_ids:
            problems.append("evidence row cites unknown claim %d" % ref)
        cited.add(ref)
    for num in sorted(claim_ids - cited - needs_experiment):
        problems.append("claim %d has no evidence row and no %r marker" % (num, NEEDS_EXPERIMENT_MARKER))

    # 4. Hygiene
    if re.search(r"\b(TODO|TBD|FIXME|PLACEHOLDER)\b", text):
        problems.append("placeholder marker (TODO/TBD/FIXME/PLACEHOLDER) present")
    if re.search(r"lorem\s+ipsum", text, re.IGNORECASE):
        problems.append("lorem ipsum filler present")
    limitation_items = [
        ln for ln in sections.get("limitations", [])
        if re.match(r"^\s*(?:[-*]|\d+[.)])\s+\S", ln)
    ]
    if len(limitation_items) < 2:
        problems.append("limitations must list at least 2 items (got %d)" % len(limitation_items))

    verdict = "PASS" if not problems else "FAIL"
    scorecard = (
        "[%s] run=%s paper=%s sections=%s claims=%d needs_experiment=%d "
        "evidence_rows=%d verified=%d/%d limitations=%d verdict=%s"
        % (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            args.run_id or "-",
            args.paper,
            "OK" if not missing else "MISSING",
            len(claims),
            len(needs_experiment),
            len(rows),
            verified,
            len(rows),
            len(limitation_items),
            verdict,
        )
    )
    for problem in problems:
        print("FAIL: %s" % problem)
    print(scorecard)
    if args.run_id:
        run_dir = os.path.join("runs", args.run_id)
        os.makedirs(run_dir, exist_ok=True)
        with open(os.path.join(run_dir, "track1_gate.log"), "a") as handle:
            for problem in problems:
                handle.write("FAIL: %s\n" % problem)
            handle.write(scorecard + "\n")
    print("TRACK1 GATE %s" % verdict if verdict == "PASS" else "TRACK1 GATE FAIL (%d problem(s))" % len(problems))
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
