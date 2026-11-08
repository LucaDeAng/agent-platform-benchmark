"""Validate the evidence, apply the not-applicable rules and write docs/results.md.

Usage:
    uv run python scripts/benchmark.py check            # validate data files
    uv run python scripts/benchmark.py check-raw FILE   # validate one per-platform raw file
    uv run python scripts/benchmark.py merge            # data/raw/*.csv -> data/evidence.csv
    uv run python scripts/benchmark.py sample           # draw the 10% re-verification sample
    uv run python scripts/benchmark.py build            # write docs/results.md

Standard library only. Every number in docs/results.md is computed here from the CSV files.
"""

from __future__ import annotations

import csv
import random
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
EVIDENCE = DATA / "evidence.csv"
PLATFORMS = DATA / "platforms.csv"
CRITERIA = DATA / "criteria.csv"
REVERIFY = DATA / "reverification.csv"
RESULTS = ROOT / "docs" / "results.md"

SEED = 20261108
SAMPLE_SHARE = 0.10

EVIDENCE_FIELDS = ["platform_id", "criterion_id", "status", "value", "source_type", "url", "accessed", "note"]
REVERIFY_FIELDS = ["platform_id", "criterion_id", "original_status", "recheck_status", "agree", "rechecked", "note"]

STATUSES = ("documented", "vendor_states", "not_found", "not_applicable")
DOC_SOURCES = {"docs", "trust", "pricing", "legal"}
CLAIM_SOURCES = {"marketing", "blog", "press"}

# criterion -> parent criterion; child becomes not_applicable when parent is not_found
NA_RULES = {"tel_native": "ch_voice", "tel_byoc": "ch_voice", "eval_judge_cal": "eval_judge"}

SYMBOL = {"documented": "D", "vendor_states": "V", "not_found": "·", "not_applicable": "n/a"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def criteria() -> list[dict[str, str]]:
    return read_csv(CRITERIA)


def included_platforms() -> list[dict[str, str]]:
    return [p for p in read_csv(PLATFORMS) if p["included"] == "yes"]


def validate(rows: list[dict[str, str]], platform_ids: list[str], criterion_ids: list[str]) -> list[str]:
    errors: list[str] = []
    seen: Counter[tuple[str, str]] = Counter()
    for i, r in enumerate(rows, start=2):
        where = f"row {i} ({r.get('platform_id')}, {r.get('criterion_id')})"
        if set(r) != set(EVIDENCE_FIELDS):
            errors.append(f"{where}: columns {sorted(r)}")
            continue
        seen[(r["platform_id"], r["criterion_id"])] += 1
        if r["platform_id"] not in platform_ids:
            errors.append(f"{where}: unknown platform")
        if r["criterion_id"] not in criterion_ids:
            errors.append(f"{where}: unknown criterion")
        s = r["status"]
        if s not in STATUSES:
            errors.append(f"{where}: bad status {s!r}")
        if s == "documented" and r["source_type"] not in DOC_SOURCES:
            errors.append(f"{where}: documented needs source_type in {sorted(DOC_SOURCES)}")
        if s == "vendor_states" and r["source_type"] not in CLAIM_SOURCES:
            errors.append(f"{where}: vendor_states needs source_type in {sorted(CLAIM_SOURCES)}")
        if s in ("documented", "vendor_states") and not r["url"].startswith("http"):
            errors.append(f"{where}: missing url")
        if s == "not_found" and r["url"]:
            errors.append(f"{where}: not_found must not carry a url")
        if not r["accessed"]:
            errors.append(f"{where}: missing access date")
        if not r["note"]:
            errors.append(f"{where}: missing note")
        if len(r["note"]) > 400:
            errors.append(f"{where}: note longer than 400 characters")
    for key, n in seen.items():
        if n > 1:
            errors.append(f"duplicate cell {key}")
    for p in platform_ids:
        for c in criterion_ids:
            if (p, c) not in seen:
                errors.append(f"missing cell ({p}, {c})")
    return errors


def apply_na(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    status = {(r["platform_id"], r["criterion_id"]): r["status"] for r in rows}
    out = []
    for r in rows:
        r = dict(r)
        parent = NA_RULES.get(r["criterion_id"])
        if parent and status.get((r["platform_id"], parent)) == "not_found" and r["status"] == "not_found":
            r["status"] = "not_applicable"
            r["note"] = f"{parent} not found, so not applicable. " + r["note"]
        out.append(r)
    return out


def cmd_check() -> int:
    plats = [p["platform_id"] for p in included_platforms()]
    crits = [c["criterion_id"] for c in criteria()]
    errors = validate(read_csv(EVIDENCE), plats, crits)
    for e in errors:
        print(e)
    print(f"{len(errors)} problem(s)")
    return 1 if errors else 0


def cmd_check_raw(path: str) -> int:
    rows = read_csv(Path(path))
    plats = sorted({r["platform_id"] for r in rows})
    crits = [c["criterion_id"] for c in criteria()]
    errors = validate(rows, plats, crits)
    for e in errors:
        print(e)
    print(f"{path}: {len(rows)} rows, {len(errors)} problem(s)")
    return 1 if errors else 0


def cmd_merge() -> int:
    plat_rows = read_csv(PLATFORMS)
    fields = list(plat_rows[0])
    updates = {}
    for path in sorted((DATA / "raw" / "platforms").glob("*.csv")):
        for r in read_csv(path):
            updates[r["platform_id"]] = r
    plat_rows = [updates.get(p["platform_id"], p) for p in plat_rows]
    write_csv(PLATFORMS, plat_rows, fields)
    print(f"updated {len(updates)} platform rows in {PLATFORMS.relative_to(ROOT)}")

    rows: list[dict[str, str]] = []
    for path in sorted((DATA / "raw").glob("*.csv")):
        rows.extend(read_csv(path))
    order_p = {p["platform_id"]: i for i, p in enumerate(included_platforms())}
    order_c = {c["criterion_id"]: i for i, c in enumerate(criteria())}
    rows.sort(key=lambda r: (order_p.get(r["platform_id"], 99), order_c.get(r["criterion_id"], 99)))
    write_csv(EVIDENCE, apply_na(rows), EVIDENCE_FIELDS)
    print(f"merged {len(rows)} rows into {EVIDENCE.relative_to(ROOT)}")
    return cmd_check()


def cmd_sample() -> int:
    rows = read_csv(EVIDENCE)
    k = round(len(rows) * SAMPLE_SHARE)
    picked = random.Random(SEED).sample(rows, k)
    existing = {(r["platform_id"], r["criterion_id"]): r for r in read_csv(REVERIFY)} if REVERIFY.exists() else {}
    out = []
    for r in picked:
        key = (r["platform_id"], r["criterion_id"])
        out.append(existing.get(key) or {
            "platform_id": r["platform_id"], "criterion_id": r["criterion_id"],
            "original_status": r["status"], "recheck_status": "", "agree": "", "rechecked": "", "note": "",
        })
    write_csv(REVERIFY, out, REVERIFY_FIELDS)
    print(f"sampled {k} of {len(rows)} cells into {REVERIFY.relative_to(ROOT)}")
    return 0


def link(r: dict[str, str]) -> str:
    sym = SYMBOL[r["status"]]
    return f"[{sym}]({r['url']})" if r["url"] else sym


def cmd_build() -> int:
    plats = included_platforms()
    crits = criteria()
    rows = apply_na(read_csv(EVIDENCE))
    errors = validate(rows, [p["platform_id"] for p in plats], [c["criterion_id"] for c in crits])
    if errors:
        print("\n".join(errors))
        return 1
    cell = {(r["platform_id"], r["criterion_id"]): r for r in rows}
    groups: dict[str, list[dict[str, str]]] = {}
    for c in crits:
        groups.setdefault(c["group"], []).append(c)

    L: list[str] = []
    L.append("# Results")
    L.append("")
    first, last = min(r["accessed"] for r in rows), max(r["accessed"] for r in rows)
    span = first if first == last else f"{first} to {last}"
    L.append(f"Generated by `scripts/benchmark.py` from `data/evidence.csv`. Snapshot of public pages accessed "
             f"{span}. {len(plats)} platforms x {len(crits)} criteria = {len(rows)} cells.")
    L.append("")
    L.append("Legend: **D** documented in vendor product docs, trust centre, pricing or legal pages; "
             "**V** vendor states it on marketing, blog or press pages only; **·** not found with the "
             "search procedure (unknown, not absent); **n/a** not applicable (see METHOD.md). "
             "Every D and V links to its source. All statuses are vendor-published and unverified; "
             "rows are in alphabetical order and are not a ranking.")
    L.append("")
    plats_sorted = sorted(plats, key=lambda p: p["name"].lower())

    L.append("## Platforms and how they were searched")
    L.append("")
    L.append("**Public docs**: whether product documentation is readable without a login (`no` means most "
             "cells can only be V or ·). **Search coverage**: whether web searches were available for that "
             "platform (`partial`/`none` means its · cells rest on a narrower search; see METHOD.md, "
             "change 2). **Signal**: inclusion rule C met.")
    L.append("")
    L.append("| Platform | Public docs | Search coverage | Signal | Signal source |")
    L.append("|---|---|---|---|---|")
    for p in plats_sorted:
        L.append(f"| {p['name']} | {p['public_docs']} | {p['search_coverage']} | {p['signal']} | "
                 f"[link]({p['signal_url']}) |")
    L.append("")
    excluded = [p for p in read_csv(PLATFORMS) if p["included"] != "yes"]
    for p in excluded:
        L.append(f"Excluded candidate: **{p['name']}**. {p['signal_note']}.")
        L.append("")
    for g, cs in groups.items():
        L.append(f"## {g}")
        L.append("")
        L.append("| Platform | " + " | ".join(c["short"] for c in cs) + " |")
        L.append("|---|" + "---|" * len(cs))
        for p in plats_sorted:
            L.append(f"| {p['name']} | " + " | ".join(link(cell[(p['platform_id'], c['criterion_id'])]) for c in cs) + " |")
        L.append("")
        L.append("Columns: " + "; ".join(f"**{c['short']}** = {c['label']}" for c in cs) + ".")
        L.append("")

    L.append("## Counts per criterion")
    L.append("")
    L.append(f"Out of {len(plats)} platforms.")
    L.append("")
    L.append("| Criterion | D documented | V vendor states | D + V | not found | n/a |")
    L.append("|---|---|---|---|---|---|")
    for c in crits:
        cnt = Counter(cell[(p["platform_id"], c["criterion_id"])]["status"] for p in plats)
        L.append(f"| {c['label']} (`{c['criterion_id']}`) | {cnt['documented']} | {cnt['vendor_states']} | "
                 f"{cnt['documented'] + cnt['vendor_states']} | {cnt['not_found']} | {cnt['not_applicable']} |")
    L.append("")

    L.append("## Recorded values")
    L.append("")
    L.append("Short values recorded with the evidence (billing unit, deployment model, MCP direction, "
             "messaging channels, number of EU official languages listed, AI-caller mechanism). "
             "No prices are reproduced.")
    L.append("")
    value_crits = [c for c in crits if c["has_value"] == "yes"]
    L.append("| Platform | " + " | ".join(c["short"] for c in value_crits) + " |")
    L.append("|---|" + "---|" * len(value_crits))
    for p in plats_sorted:
        vals = []
        for c in value_crits:
            r = cell[(p["platform_id"], c["criterion_id"])]
            vals.append(r["value"].replace("|", "/") if r["value"] else "")
        L.append(f"| {p['name']} | " + " | ".join(vals) + " |")
    L.append("")

    L.append("## Re-verification sample")
    L.append("")
    if REVERIFY.exists():
        rv = read_csv(REVERIFY)
        done = [r for r in rv if r["agree"] in ("yes", "no")]
        agree = sum(r["agree"] == "yes" for r in done)
        if done:
            L.append(f"{len(rv)} cells drawn at random (seed {SEED}, {int(SAMPLE_SHARE * 100)}% of {len(rows)}); "
                     f"{len(done)} re-checked; {agree} agree with the recorded status "
                     f"({agree / len(done):.0%}). Disagreements were corrected in `data/evidence.csv` "
                     f"and are listed in `data/reverification.csv`.")
        else:
            L.append("Sample drawn, not yet re-checked.")
    else:
        L.append("Not yet drawn.")
    L.append("")

    RESULTS.write_text("\n".join(L), encoding="utf-8")
    print(f"wrote {RESULTS.relative_to(ROOT)}")
    return 0


def main(argv: list[str]) -> int:
    if len(argv) == 3 and argv[1] == "check-raw":
        return cmd_check_raw(argv[2])
    cmds = {"check": cmd_check, "merge": cmd_merge, "sample": cmd_sample, "build": cmd_build}
    if len(argv) != 2 or argv[1] not in cmds:
        print(__doc__)
        return 2
    return cmds[argv[1]]()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
