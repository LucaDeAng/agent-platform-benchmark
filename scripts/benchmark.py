"""Validate the evidence, apply the not-applicable rules, score, and write the outputs.

Usage:
    uv run python scripts/benchmark.py check            # validate data files
    uv run python scripts/benchmark.py sample           # draw the 10% re-verification sample
    uv run python scripts/benchmark.py scores           # write docs/scores.md and data/export/platforms.json
    uv run python scripts/benchmark.py build            # write docs/results.md, then run `scores`

During collection, per-platform files were merged into data/evidence.csv (see the git history and
METHOD.md, change 5); that step has been removed now that evidence.csv is the only data file.

Standard library only. Every number in docs/results.md, docs/scores.md and data/export/platforms.json
is computed here from the CSV files. Scores use exact fractions; they are rounded only for display.
"""

from __future__ import annotations

import csv
import json
import random
import sys
from collections import Counter
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
EVIDENCE = DATA / "evidence.csv"
PLATFORMS = DATA / "platforms.csv"
CRITERIA = DATA / "criteria.csv"
REVERIFY = DATA / "reverification.csv"
DIMENSIONS = DATA / "dimensions.csv"
RESULTS = ROOT / "docs" / "results.md"
SCORES = ROOT / "docs" / "scores.md"
EXPORT = DATA / "export" / "platforms.json"

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
    errors = validate(read_csv(EVIDENCE), plats, crits) + validate_dimensions(dimensions(), criteria())
    for e in errors:
        print(e)
    print(f"{len(errors)} problem(s)")
    return 1 if errors else 0


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
    L.append("The last column says how many of the not-found cells are on platforms whose search coverage was "
             "`partial` or `none` (METHOD.md, change 2), i.e. rest on a narrower search.")
    L.append("")
    L.append("| Criterion | D documented | V vendor states | D + V | not found | n/a | not found on partial/none coverage |")
    L.append("|---|---|---|---|---|---|---|")
    narrow = {p["platform_id"] for p in plats if p["search_coverage"] in ("partial", "none")}
    for c in crits:
        cs = [cell[(p["platform_id"], c["criterion_id"])] for p in plats]
        cnt = Counter(r["status"] for r in cs)
        nn = sum(r["status"] == "not_found" and r["platform_id"] in narrow for r in cs)
        L.append(f"| {c['label']} (`{c['criterion_id']}`) | {cnt['documented']} | {cnt['vendor_states']} | "
                 f"{cnt['documented'] + cnt['vendor_states']} | {cnt['not_found']} | {cnt['not_applicable']} | "
                 f"{nn} of {cnt['not_found']} |")
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
    return cmd_scores()


# ---------------------------------------------------------------------------------------------
# Dimension scores, synthetic index and sensitivity analysis (METHOD.md, "Dimension scores and
# synthetic index"). The value table, weights and rules below are the ones written in METHOD.md.
# ---------------------------------------------------------------------------------------------

SCHEMA_VERSION = "1.0.0"
DATASET_ID = "agent-platform-benchmark-2026-11"

# status -> (lower value, upper value)
VALUE_TABLE: dict[str, tuple[F, F]] = {
    "documented": (F(1), F(1)),
    "vendor_states": (F(1, 2), F(1, 2)),
    "not_found": (F(0), F(1)),
    "not_applicable": (F(0), F(1)),
}
EVIDENCE_STATUSES = ("documented", "vendor_states")
DEFAULT_VENDOR_VALUE = F(1, 2)

# Ranking rule (METHOD.md): (a) share of overlapping pairs below this, (b) rank span at most this.
MAX_OVERLAP_SHARE = F(1, 2)
MAX_RANK_SPAN = 2  # worst rank - best rank

Bounds = tuple[F, F, F]  # lower, upper, coverage


def dimensions() -> list[dict[str, str]]:
    return sorted(read_csv(DIMENSIONS), key=lambda d: int(d["order"]))


def dimension_criteria(dims: list[dict[str, str]], crits: list[dict[str, str]]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {d["dimension_id"]: [] for d in dims}
    for c in crits:
        out[c["dimension_id"]].append(c["criterion_id"])
    return out


def validate_dimensions(dims: list[dict[str, str]], crits: list[dict[str, str]]) -> list[str]:
    errors = []
    ids = [d["dimension_id"] for d in dims]
    if len(ids) != len(set(ids)):
        errors.append("duplicate dimension id")
    for c in crits:
        if c.get("dimension_id") not in ids:
            errors.append(f"criterion {c['criterion_id']}: dimension {c.get('dimension_id')!r} unknown")
    for d in ids:
        if not any(c.get("dimension_id") == d for c in crits):
            errors.append(f"dimension {d} has no criteria")
    if sum((F(d["default_weight"]) for d in dims), F(0)) != 1:
        errors.append("default weights do not sum to 1")
    return errors


def cell_bounds(status: str, vendor_value: F = DEFAULT_VENDOR_VALUE) -> tuple[F, F]:
    if status == "vendor_states":
        return vendor_value, vendor_value
    return VALUE_TABLE[status]


def dimension_scores(status: dict[tuple[str, str], str], platform_ids: list[str],
                     dim_crits: dict[str, list[str]], vendor_value: F = DEFAULT_VENDOR_VALUE
                     ) -> dict[tuple[str, str], Bounds]:
    """Mean of criterion values per (platform, dimension), as (lower, upper, coverage)."""
    out = {}
    for p in platform_ids:
        for d, cs in dim_crits.items():
            vals = [cell_bounds(status[(p, c)], vendor_value) for c in cs]
            lo = sum((v[0] for v in vals), F(0)) / len(cs)
            hi = sum((v[1] for v in vals), F(0)) / len(cs)
            cov = F(sum(status[(p, c)] in EVIDENCE_STATUSES for c in cs), len(cs))
            out[(p, d)] = (lo, hi, cov)
    return out


def index_scores(ds: dict[tuple[str, str], Bounds], platform_ids: list[str],
                 weights: dict[str, F]) -> dict[str, Bounds]:
    """Weighted arithmetic mean of dimension lower bounds, upper bounds and coverages."""
    total = sum(weights.values(), F(0))
    out = {}
    for p in platform_ids:
        lo, hi, cov = (sum((w * ds[(p, d)][k] for d, w in weights.items()), F(0)) / total for k in range(3))
        out[p] = (lo, hi, cov)
    return out


def competition_ranks(scores: dict[str, F]) -> dict[str, int]:
    """1 + number of platforms with a strictly higher score (ties share a rank)."""
    return {p: 1 + sum(v > s for v in scores.values()) for p, s in scores.items()}


def possible_ranks(idx: dict[str, Bounds]) -> dict[str, tuple[int, int]]:
    """Best and worst rank reachable by filling unknown cells (METHOD.md)."""
    out = {}
    for p, (lo, hi, _) in idx.items():
        best = 1 + sum(idx[q][0] > hi for q in idx if q != p)
        worst = 1 + sum(idx[q][1] > lo for q in idx if q != p)
        out[p] = (best, worst)
    return out


def overlaps(a: Bounds, b: Bounds) -> bool:
    return not (a[0] > b[1] or b[0] > a[1])


def bands(idx: dict[str, Bounds]) -> dict[str, int]:
    """Interval-dominance layers: B dominates A when B's lower bound exceeds A's upper bound."""
    remaining = set(idx)
    out: dict[str, int] = {}
    band = 1
    while remaining:
        layer = {p for p in remaining if not any(idx[q][0] > idx[p][1] for q in remaining)}
        for p in layer:
            out[p] = band
        remaining -= layer
        band += 1
    return out


def scenarios(dims: list[dict[str, str]], dim_crits: dict[str, list[str]],
              crit_labels: dict[str, str]) -> list[dict]:
    """Sensitivity scenarios written in METHOD.md. The first one is the default."""
    ids = [d["dimension_id"] for d in dims]
    equal = {d: F(1, len(ids)) for d in ids}
    n_total = sum(len(v) for v in dim_crits.values())

    def tilt(heavy: str) -> dict[str, F]:
        return {d: (F(1, 2) if d == heavy else F(1, 2 * (len(ids) - 1))) for d in ids}

    base = {"vendor_value": DEFAULT_VENDOR_VALUE, "dim_crits": dim_crits, "dropped": None}
    out = [{**base, "id": "default", "kind": "default", "label": "Equal dimension weights (default)",
            "weights": equal}]
    names = {"eval_qa": "Evaluation-heavy", "prod_gov": "Governance-heavy", "voice_eu": "EU-heavy"}
    for d in ids:
        out.append({**base, "id": f"w_{d}", "kind": "weights", "label": f"{names.get(d, d)} weights",
                    "weights": tilt(d)})
    out.append({**base, "id": "w_criterion_equal", "kind": "weights", "label": "Criterion-equal weights",
                "weights": {d: F(len(dim_crits[d]), n_total) for d in ids}})
    for v in (F(0), F(1)):
        out.append({**base, "id": f"v_{v}", "kind": "value_table", "label": f"vendor_states = {v}",
                    "weights": equal, "vendor_value": v})
    for d, cs in dim_crits.items():
        for c in cs:
            reduced = {k: [x for x in v if x != c] for k, v in dim_crits.items()}
            if not reduced[d]:
                continue
            out.append({**base, "id": f"loo_{c}", "kind": "leave_one_out", "label": f"Without {crit_labels[c]}",
                        "weights": equal, "dim_crits": reduced, "dropped": c})
    return out


def compute(plats: list[dict[str, str]], crits: list[dict[str, str]], dims: list[dict[str, str]],
            rows: list[dict[str, str]]) -> dict:
    """Everything docs/scores.md and the export need, from evidence rows with n/a already applied."""
    pids = [p["platform_id"] for p in plats]
    status = {(r["platform_id"], r["criterion_id"]): r["status"] for r in rows}
    dim_crits = dimension_criteria(dims, crits)
    labels = {c["criterion_id"]: c["label"] for c in crits}
    weights = {d["dimension_id"]: F(d["default_weight"]) for d in dims}

    ds = dimension_scores(status, pids, dim_crits)
    idx = index_scores(ds, pids, weights)
    evidence_cells = {p: sum(status[(p, c["criterion_id"])] in EVIDENCE_STATUSES for c in crits) for p in pids}

    runs = []
    for sc in scenarios(dims, dim_crits, labels):
        s_idx = index_scores(dimension_scores(status, pids, sc["dim_crits"], sc["vendor_value"]), pids, sc["weights"])
        runs.append({**sc, "idx": s_idx, "bands": bands(s_idx),
                     "rank_lo": competition_ranks({p: v[0] for p, v in s_idx.items()}),
                     "rank_hi": competition_ranks({p: v[1] for p, v in s_idx.items()})})
    base = runs[0]
    for r in runs:
        r["shift_lo"] = max(abs(r["rank_lo"][p] - base["rank_lo"][p]) for p in pids)
        r["shift_hi"] = max(abs(r["rank_hi"][p] - base["rank_hi"][p]) for p in pids)

    sens = {}
    for p in pids:
        los = [r["rank_lo"][p] for r in runs]
        his = [r["rank_hi"][p] for r in runs]
        bs = [r["bands"][p] for r in runs]
        sens[p] = {"rank_lo": base["rank_lo"][p], "rank_lo_min": min(los), "rank_lo_max": max(los),
                   "rank_hi": base["rank_hi"][p], "rank_hi_min": min(his), "rank_hi_max": max(his),
                   "band_min": min(bs), "band_max": max(bs),
                   "band_changed": sum(b != base["bands"][p] for b in bs)}

    pairs = list(combinations(pids, 2))
    n_overlap = sum(overlaps(idx[a], idx[b]) for a, b in pairs)
    wide = [p for p in pids if sens[p]["rank_lo_max"] - sens[p]["rank_lo_min"] > MAX_RANK_SPAN
            or sens[p]["rank_hi_max"] - sens[p]["rank_hi_min"] > MAX_RANK_SPAN]
    rule_a = (F(n_overlap, len(pairs)) if pairs else F(0)) < MAX_OVERLAP_SHARE
    rule_b = not wide
    implicit = {c: weights[d] / len(cs) for d, cs in dim_crits.items() for c in cs}
    return {"pids": pids, "status": status, "dim_crits": dim_crits, "weights": weights, "ds": ds,
            "idx": idx, "evidence_cells": evidence_cells, "runs": runs, "sens": sens,
            "possible": possible_ranks(idx), "bands": bands(idx), "pairs": len(pairs),
            "n_overlap": n_overlap, "wide": wide, "rule_a": rule_a, "rule_b": rule_b,
            "ranking_holds": rule_a and rule_b, "implicit_weights": implicit}


def r2(x: F) -> str:
    return f"{float(x):.2f}"


def pct(x: F) -> str:
    return f"{float(x) * 100:.0f}%"


def rng(b: Bounds) -> str:
    return f"{r2(b[0])}–{r2(b[1])}"


def span(lo: int, hi: int) -> str:
    return str(lo) if lo == hi else f"{lo}–{hi}"


def median(xs: list) -> F:
    s = sorted(xs)
    k = len(s) // 2
    return F(s[k]) if len(s) % 2 else (F(s[k - 1]) + F(s[k])) / 2


def short_name(name: str, width: int = 32) -> str:
    name = name.split(" (formerly")[0]
    return name if len(name) <= width else name[: width - 1] + "…"


def bar(b: Bounds, width: int = 40) -> str:
    lo, hi = round(float(b[0]) * width), round(float(b[1]) * width)
    return "█" * lo + "░" * (hi - lo) + "·" * (width - hi)


def write_scores(plats: list[dict[str, str]], crits: list[dict[str, str]], dims: list[dict[str, str]],
                 rows: list[dict[str, str]], m: dict) -> None:
    name = {p["platform_id"]: p["name"] for p in plats}
    pinfo = {p["platform_id"]: p for p in plats}
    order = sorted(m["pids"], key=lambda p: name[p].lower())
    labels = {c["criterion_id"]: c["label"] for c in crits}
    dl = {d["dimension_id"]: d["label"] for d in dims}
    idx, ds, sens, poss, band = m["idx"], m["ds"], m["sens"], m["possible"], m["bands"]
    n = len(m["pids"])
    first, last = min(r["accessed"] for r in rows), max(r["accessed"] for r in rows)
    snap = first if first == last else f"{first} to {last}"
    narrow = [p for p in m["pids"] if pinfo[p]["search_coverage"] in ("partial", "none")]
    full = [p for p in m["pids"] if p not in narrow]
    widths = {p: idx[p][1] - idx[p][0] for p in m["pids"]}

    L: list[str] = []
    L.append("# Scores: three dimensions and a synthetic index")
    L.append("")
    L.append(f"Generated by `scripts/benchmark.py` from `data/evidence.csv`, `data/criteria.csv` and "
             f"`data/dimensions.csv`. Snapshot of public pages accessed {snap}. {n} platforms, "
             f"{len(crits)} criteria, {len(dims)} dimensions. Rules: [METHOD.md](../METHOD.md), section "
             f"\"Dimension scores and synthetic index\". Background: [evaluating-agents.md](evaluating-agents.md).")
    L.append("")
    L.append("**These scores measure what vendors publish, not what their products do.** A high score means "
             "that many capabilities are documented in public pages. A low lower bound often means that the vendor "
             "keeps its documentation behind a login, or that our search for that platform was narrower. Nothing "
             "here was tested hands-on. Evidence was collected and re-checked by LLM agents under the author's "
             "supervision (see the README).")
    L.append("")

    L.append("## How to read a score")
    L.append("")
    L.append("- Every score is a **range** between 0 and 1. The **lower bound** counts every cell without "
             "evidence as 0 (capability absent). The **upper bound** counts it as 1 (capability documented). "
             "As far as public documentation goes, the truth lies somewhere in between.")
    L.append("- **Coverage** is the share of cells with evidence (documented or vendor states). The width of a "
             "range is exactly 1 − coverage: a wide range means that little is known, not that the product is "
             "uneven.")
    L.append("- Values per cell: documented = 1; vendor states (marketing, blog or press pages only) = 0.5; "
             "not found and not applicable = 0 for the lower bound and 1 for the upper bound. A dimension score "
             "is the mean of its criteria; the index is the mean of the three dimensions (equal weights).")
    L.append("- No midpoint is published: it would amount to guessing 0.5 for every unknown cell.")
    L.append("- Rows are in alphabetical order. \"Does a ranking hold?\" below explains why there is no league "
             "table." if not m["ranking_holds"] else "- Rows are in alphabetical order.")
    L.append("")

    L.append("## Dimensions")
    L.append("")
    L.append("| Dimension | Question | Criteria | Weight of each criterion in the index |")
    L.append("|---|---|---|---|")
    for d in dims:
        cs = m["dim_crits"][d["dimension_id"]]
        w = m["implicit_weights"][cs[0]]
        L.append(f"| {d['label']} (`{d['dimension_id']}`) | {d['question']} | "
                 + ", ".join(f"`{c}`" for c in cs) + f" ({len(cs)}) | {w} ({float(w) * 100:.1f}%) |")
    L.append("")
    L.append("Equal weights for the three dimensions give unequal weights to criteria, because the dimensions "
             "have different numbers of criteria (last column).")
    L.append("")

    L.append("## Index")
    L.append("")
    L.append("| Platform | Index range | Coverage | Cells with evidence | Band | Possible rank | Public docs | Search coverage |")
    L.append("|---|---|---|---|---|---|---|---|")
    for p in order:
        b = idx[p]
        L.append(f"| {name[p]} | {rng(b)} | {pct(b[2])} | {m['evidence_cells'][p]} of {len(crits)} | "
                 f"{band[p]} | {span(*poss[p])} | {pinfo[p]['public_docs']} | {pinfo[p]['search_coverage']} |")
    L.append("")
    L.append("**Coverage** here is the equally weighted mean of the three dimension coverages; **cells with "
             "evidence** is the raw count. **Possible rank**: the best and the worst rank the platform could "
             "take with default weights, if its unknown cells were all documented and everyone else's all "
             "absent, or the reverse. **Band**: see \"Does a ranking hold?\".")
    L.append("")
    L.append("Index ranges on a 0–1 scale (█ lower bound, ░ unknown, · above the upper bound):")
    L.append("")
    L.append("```")
    pad = max(len(short_name(name[p])) for p in order)
    L.append(" " * pad + "  0" + " " * 38 + "1")
    for p in order:
        L.append(f"{short_name(name[p]):<{pad}}  {bar(idx[p])}  {rng(idx[p])}")
    L.append("```")
    L.append("")

    L.append("## Dimension scores")
    L.append("")
    L.append("Each cell: range, then coverage in brackets.")
    L.append("")
    L.append("| Platform | " + " | ".join(dl[d["dimension_id"]] for d in dims) + " |")
    L.append("|---|" + "---|" * len(dims))
    for p in order:
        L.append(f"| {name[p]} | " + " | ".join(
            f"{rng(ds[(p, d['dimension_id'])])} ({pct(ds[(p, d['dimension_id'])][2])})" for d in dims) + " |")
    L.append("")
    for d in dims:
        did = d["dimension_id"]
        cov = [ds[(p, did)][2] for p in m["pids"]]
        L.append(f"- **{d['label']}**: coverage from {pct(min(cov))} to {pct(max(cov))}, median "
                 f"{pct(median(cov))}; {sum(c == 1 for c in cov)} of {n} platforms have evidence in every cell "
                 f"of this dimension.")
    L.append("")

    L.append("## Does a ranking hold?")
    L.append("")
    L.append("The rule was written in METHOD.md before any score was computed. A ranked list is published "
             "only if (a) fewer than half of all platform pairs have overlapping index ranges, and (b) every "
             "platform's rank moves by at most 2 positions across the sensitivity scenarios, at both bounds.")
    L.append("")
    L.append(f"- (a) {m['n_overlap']} of {m['pairs']} platform pairs ({pct(F(m['n_overlap'], m['pairs']))}) "
             f"have overlapping index ranges: **{'met' if m['rule_a'] else 'not met'}**.")
    L.append(f"- (b) {len(m['wide'])} of {n} platforms have a rank range wider than 3 positions at one bound "
             f"or both: **{'met' if m['rule_b'] else 'not met'}**.")
    L.append("")
    if m["ranking_holds"]:
        L.append("Both conditions hold, so a ranking by lower bound is shown below.")
        L.append("")
        L.append("| Rank (lower bound) | Platform | Index range |")
        L.append("|---|---|---|")
        for p in sorted(m["pids"], key=lambda p: (sens[p]["rank_lo"], name[p].lower())):
            L.append(f"| {sens[p]['rank_lo']} | {name[p]} | {rng(idx[p])} |")
    else:
        L.append("**A league table would be misleading, so none is shown.** Platforms are grouped into bands "
                 "instead, by interval dominance on the default index: platform B dominates platform A when B's "
                 "lower bound is above A's upper bound. Band 1 holds the platforms that no platform dominates; "
                 "band 2 those dominated only by band-1 platforms; and so on. Within a band, platforms are "
                 "listed alphabetically and are not ordered.")
        L.append("")
        L.append("A band says which platforms the public evidence can separate. It is not a quality grade: a "
                 "platform can be in band 1 because its range is wide (much is unknown), not because much is "
                 "documented.")
        L.append("")
        L.append("| Band | Platforms (index range) |")
        L.append("|---|---|")
        for b in sorted(set(band.values())):
            members = sorted((p for p in m["pids"] if band[p] == b), key=lambda p: name[p].lower())
            L.append(f"| {b} | " + "; ".join(f"{name[p]} ({rng(idx[p])})" for p in members) + " |")
        L.append("")
        band1 = [q for q in m["pids"] if band[q] == 1]
        odd = []
        for p in sorted((q for q in m["pids"] if band[q] > 1), key=lambda q: name[q].lower()):
            less = sorted((q for q in band1 if idx[q][2] < idx[p][2]), key=lambda q: (idx[q][2], name[q].lower()))
            if less:
                odd.append(f"{name[p]} (band {band[p]}, coverage {pct(idx[p][2])}) has higher coverage than "
                           f"{len(less)} band-1 platform(s), the lowest being {name[less[0]]} "
                           f"({pct(idx[less[0]][2])})")
        if odd:
            L.append("**Read bands with care.** " + "; ".join(odd) + ". A vendor-states cell counts 0.5 at both "
                     "bounds, so it caps the upper bound, while an unknown cell keeps the range open up to 1. A "
                     "platform with more unknown cells can therefore escape domination that a better-covered "
                     "platform with a few vendor-states cells does not.")
            L.append("")
        gated = [q for q in m["pids"] if pinfo[q]["public_docs"] in ("no", "partial")]
        last_band = max(band.values())
        in_last = [q for q in m["pids"] if band[q] == last_band]
        L.append(f"The {len(gated)} platform(s) whose product documentation is fully or partly behind a login "
                 f"({', '.join(sorted(name[q] for q in gated))}): bands "
                 f"{', '.join(str(band[q]) for q in sorted(gated, key=lambda q: name[q]))}. Band {last_band} holds "
                 f"{len(in_last)} platform(s), {sum(q in gated for q in in_last)} of them with gated documentation.")
    L.append("")
    line = (f"Width of the index range: from {r2(min(widths.values()))} to {r2(max(widths.values()))}. Median "
            f"width {r2(median([widths[p] for p in narrow]))} for the {len(narrow)} platforms with `partial` or "
            f"`none` search coverage")
    if full:
        line += f", {r2(median([widths[p] for p in full]))} for the {len(full)} with `full` coverage"
    L.append(line + ".")
    L.append("")

    L.append("## Sensitivity analysis")
    L.append("")
    runs = m["runs"]
    kinds = Counter(r["kind"] for r in runs)
    L.append(f"{len(runs)} scenarios, each scored at the lower and at the upper bound: the default, "
             f"{kinds['weights']} alternative weightings, {kinds['value_table']} alternative values for "
             f"`vendor_states`, and {kinds['leave_one_out']} leave-one-criterion-out runs.")
    L.append("")
    L.append("| Scenario | Weights (eval_qa / prod_gov / voice_eu) | vendor_states value | Largest rank shift of any platform vs default, lower bound | Same, upper bound |")
    L.append("|---|---|---|---|---|")
    for r in runs:
        if r["kind"] == "leave_one_out":
            continue
        w = " / ".join(str(r["weights"][d["dimension_id"]]) for d in dims)
        L.append(f"| {r['label']} | {w} | {r['vendor_value']} | {r['shift_lo']} | {r['shift_hi']} |")
    loo = [r for r in runs if r["kind"] == "leave_one_out"]
    L.append(f"| Leave one criterion out ({len(loo)} runs) | 1/3 each | 1/2 | "
             f"{max(r['shift_lo'] for r in loo)} (largest over the runs) | {max(r['shift_hi'] for r in loo)} "
             f"(largest over the runs) |")
    L.append("")
    L.append(f"Rank range per platform across all {len(runs)} scenarios. Competition ranks out of {n}: tied "
             f"platforms share the better rank.")
    L.append("")
    L.append("| Platform | Default rank, lower bound | Range across scenarios, lower bound | Default rank, upper bound | Range across scenarios, upper bound | Default band | Band range across scenarios | Scenarios with a different band |")
    L.append("|---|---|---|---|---|---|---|---|")
    for p in order:
        s = sens[p]
        L.append(f"| {name[p]} | {s['rank_lo']} | {span(s['rank_lo_min'], s['rank_lo_max'])} | {s['rank_hi']} | "
                 f"{span(s['rank_hi_min'], s['rank_hi_max'])} | {band[p]} | {span(s['band_min'], s['band_max'])} | "
                 f"{s['band_changed']} of {len(runs)} |")
    L.append("")
    at_ceiling = sum(idx[p][1] == 1 for p in m["pids"])
    L.append(f"Upper-bound ranks are coarse: {at_ceiling} of {n} platforms reach an upper bound of exactly 1 with "
             f"default settings and share rank 1, so a small change (for example `vendor_states` = 1) can move a "
             f"platform many places. The band columns were added after the results were first seen; they are "
             f"reported, not used to decide anything.")
    L.append("")
    base_b = runs[0]["bands"]
    moves = []
    for r in runs[1:]:
        ch = sorted((q for q in m["pids"] if r["bands"][q] != base_b[q]), key=lambda q: name[q].lower())
        if ch:
            moves.append(f"*{r['label']}* ({len(set(r['bands'].values()))} band(s) in total; "
                         + ", ".join(f"{short_name(name[q])} {base_b[q]}→{r['bands'][q]}" for q in ch) + ")")
    if moves:
        L.append(f"Scenarios that change at least one band ({len(moves)} of {len(runs) - 1}): " + "; ".join(moves) + ".")
        L.append("")
    spans_lo = [sens[p]["rank_lo_max"] - sens[p]["rank_lo_min"] for p in m["pids"]]
    spans_hi = [sens[p]["rank_hi_max"] - sens[p]["rank_hi_min"] for p in m["pids"]]
    poss_spans = [poss[p][1] - poss[p][0] for p in m["pids"]]
    L.append(f"Rank movement across scenarios (worst minus best rank): lower bound median "
             f"{median(spans_lo)}, largest {max(spans_lo)}; upper bound median {median(spans_hi)}, largest "
             f"{max(spans_hi)}. This covers weighting and value choices only. "
             + ("Missing data moves ranks more: " if median(poss_spans) > max(median(spans_lo), median(spans_hi))
                else "For comparison, ")
             + f"the \"Possible rank\" interval spans a median of {median(poss_spans)} positions (largest "
             f"{max(poss_spans)}).")
    L.append("")
    top = sorted(loo, key=lambda r: (-(r["shift_lo"] + r["shift_hi"]), r["dropped"]))[:5]
    L.append("Criteria whose removal moves ranks the most (largest shift of any platform, lower / upper bound): "
             + "; ".join(f"{labels[r['dropped']]} (`{r['dropped']}`) {r['shift_lo']} / {r['shift_hi']}" for r in top)
             + ".")
    L.append("")

    L.append("## Ways to misread these scores")
    L.append("")
    L.append("- **Documentation is not capability.** The index counts what is published. A vendor with gated "
             "docs (Sierra, Decagon, Parloa) has many vendor-states or not-found cells. That lowers its lower "
             "bound and widens its range, and says nothing about the product.")
    L.append("- **The lower bound is not \"the score\".** It assumes every unknown is absent; the upper bound "
             "assumes every unknown is documented. Neither is an estimate, and the range is not a confidence "
             "interval.")
    L.append("- **Uneven search.** Platforms with `partial` or `none` search coverage (METHOD.md, change 2) have "
             "not-found cells that rest on a narrower search, so their lower bounds may be too low.")
    v1 = next(r for r in runs if r["id"] == "v_1")
    L.append(f"- **Vendor states counts half, and the bands depend on it.** A marketing claim scores 0.5 by "
             f"convention. If claims counted as documentation (`vendor_states` = 1), the platforms would fall into "
             f"{len(set(v1['bands'].values()))} band(s) instead of {len(set(band.values()))}, and the largest "
             f"upper-bound rank shift would be {v1['shift_hi']} places. Any separation of the vendors with gated "
             f"docs from the rest depends on this convention.")
    L.append("- **Presence, not depth.** A criterion scores the same whether the feature is basic or extensive, "
             "generally available or in preview, voice-only or omnichannel. Recorded values are not scored.")
    L.append("- **Suites are scored as a whole.** For Microsoft, Google, Amazon, Salesforce and Genesys, evidence "
             "can come from several products, including QA products that may cover human agents only.")
    L.append("- **Salesforce owns two scored platforms** (Salesforce Agentforce and Fin). They are scored "
             "separately.")
    L.append("- **Compensation.** The index is a weighted mean: a high score in one dimension offsets a low one in "
             "another. Read the dimension scores, not only the index.")
    L.append("- **Bands are not grades.** A band groups platforms that the evidence cannot separate; a wide range "
             "can put a platform in band 1.")
    L.append("- **Commercial transparency is in the governance dimension.** `pricing_model` and `deploy_model` "
             "score whether a billing unit and a deployment model are published, not whether they are favourable.")
    L.append("- **Snapshot.** Pages change. The access date of every cell is in `data/evidence.csv`.")
    L.append("")
    L.append("Machine-readable version: `data/export/platforms.json` (schema: `data/export/platforms.schema.json`).")
    L.append("")
    SCORES.write_text("\n".join(L), encoding="utf-8")


def f4(x: F) -> float:
    return round(float(x), 4)


def build_export(plats: list[dict[str, str]], crits: list[dict[str, str]], dims: list[dict[str, str]],
                 rows: list[dict[str, str]], m: dict) -> dict:
    """The JSON export described in data/export/platforms.schema.json. Deterministic: no build timestamp."""
    first, last = min(r["accessed"] for r in rows), max(r["accessed"] for r in rows)
    crit_dim = {c["criterion_id"]: c["dimension_id"] for c in crits}
    out: dict = {
        "schema_version": SCHEMA_VERSION,
        "id": DATASET_ID,
        "title": "Agent platform benchmark: what public docs say",
        "snapshot": {"accessed_from": first, "accessed_to": last},
        "licence": {"data": "CC-BY-4.0", "code": "MIT"},
        "disclaimer": ("Scores measure vendor-published documentation, not product capability. not_found means "
                       "unknown, not absent. Every score is a range: the lower bound counts unknown cells as 0, "
                       "the upper bound as 1. Nothing was tested hands-on."),
        "llm_assisted": True,
        "documentation": {"method": "METHOD.md", "scores": "docs/scores.md",
                          "schema": "data/export/platforms.schema.json"},
        "value_table": [{"id": s, "status": s, "lower": f4(lo), "upper": f4(hi)} for s, (lo, hi) in VALUE_TABLE.items()],
        "dimensions": [{"id": d["dimension_id"], "order": int(d["order"]), "label": d["label"],
                        "question": d["question"], "default_weight": f4(F(d["default_weight"])),
                        "criterion_ids": m["dim_crits"][d["dimension_id"]]} for d in dims],
        "criteria": [{"id": c["criterion_id"], "label": c["label"], "short": c["short"], "group": c["group"],
                      "dimension_id": c["dimension_id"], "has_value": c["has_value"] == "yes",
                      "index_weight": f4(m["implicit_weights"][c["criterion_id"]])} for c in crits],
        "platforms": [],
        "evidence": [],
        "dimension_scores": [],
        "index_scores": [],
        "scenarios": [],
        "summary": {
            "platform_count": len(m["pids"]), "criterion_count": len(crits), "cell_count": len(rows),
            "overlapping_pairs": m["n_overlap"], "platform_pairs": m["pairs"],
            "rule_a_met": m["rule_a"], "rule_b_met": m["rule_b"], "ranking_published": m["ranking_holds"],
        },
    }
    for p in sorted(plats, key=lambda p: p["platform_id"]):
        out["platforms"].append({
            "id": p["platform_id"], "name": p["name"], "vendor": p["vendor"],
            "products_covered": p["products_covered"], "docs_root": p["docs_root"] or None,
            "trust_url": p["trust_url"] or None, "pricing_url": p["pricing_url"] or None,
            "public_docs": p["public_docs"], "search_coverage": p["search_coverage"],
            "inclusion_signal": p["signal"], "inclusion_signal_url": p["signal_url"],
        })
    for r in sorted(rows, key=lambda r: (r["platform_id"], r["criterion_id"])):
        lo, hi = cell_bounds(r["status"])
        out["evidence"].append({
            "id": f"{r['platform_id']}:{r['criterion_id']}", "platform_id": r["platform_id"],
            "criterion_id": r["criterion_id"], "dimension_id": crit_dim[r["criterion_id"]],
            "status": r["status"], "value": r["value"] or None, "source_type": r["source_type"] or None,
            "url": r["url"] or None, "accessed": r["accessed"], "note": r["note"],
            "score_lower": f4(lo), "score_upper": f4(hi),
        })
    status = m["status"]
    for p in sorted(m["pids"]):
        for d in dims:
            did = d["dimension_id"]
            lo, hi, cov = m["ds"][(p, did)]
            cnt = Counter(status[(p, c)] for c in m["dim_crits"][did])
            out["dimension_scores"].append({
                "id": f"{p}:{did}", "platform_id": p, "dimension_id": did,
                "lower": f4(lo), "upper": f4(hi), "coverage": f4(cov), "n_criteria": len(m["dim_crits"][did]),
                "n_documented": cnt["documented"], "n_vendor_states": cnt["vendor_states"],
                "n_not_found": cnt["not_found"], "n_not_applicable": cnt["not_applicable"],
            })
        lo, hi, cov = m["idx"][p]
        s = m["sens"][p]
        out["index_scores"].append({
            "id": f"{p}:index", "platform_id": p, "lower": f4(lo), "upper": f4(hi), "coverage": f4(cov),
            "cells_with_evidence": m["evidence_cells"][p], "cells_total": len(crits),
            "band": m["bands"][p], "possible_rank_best": m["possible"][p][0],
            "possible_rank_worst": m["possible"][p][1],
            "rank_lower_default": s["rank_lo"], "rank_lower_min": s["rank_lo_min"], "rank_lower_max": s["rank_lo_max"],
            "rank_upper_default": s["rank_hi"], "rank_upper_min": s["rank_hi_min"], "rank_upper_max": s["rank_hi_max"],
            "band_min": s["band_min"], "band_max": s["band_max"],
        })
    for r in m["runs"]:
        out["scenarios"].append({
            "id": r["id"], "kind": r["kind"], "label": r["label"],
            "weights": {d: f4(w) for d, w in r["weights"].items()}, "vendor_states_value": f4(r["vendor_value"]),
            "dropped_criterion_id": r["dropped"], "max_rank_shift_lower": r["shift_lo"],
            "max_rank_shift_upper": r["shift_hi"],
        })
    return out


def load_scored():
    """Included platforms, criteria, dimensions and evidence rows with n/a applied; None if invalid."""
    plats, crits, dims = included_platforms(), criteria(), dimensions()
    rows = apply_na(read_csv(EVIDENCE))
    errors = validate(rows, [p["platform_id"] for p in plats], [c["criterion_id"] for c in crits])
    errors += validate_dimensions(dims, crits)
    if errors:
        print("\n".join(errors))
        return None
    return plats, crits, dims, rows


def cmd_scores() -> int:
    loaded = load_scored()
    if loaded is None:
        return 1
    plats, crits, dims, rows = loaded
    m = compute(plats, crits, dims, rows)
    write_scores(plats, crits, dims, rows, m)
    EXPORT.parent.mkdir(parents=True, exist_ok=True)
    EXPORT.write_text(json.dumps(build_export(plats, crits, dims, rows, m), ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8")
    print(f"wrote {SCORES.relative_to(ROOT)} and {EXPORT.relative_to(ROOT)}")
    return 0


def main(argv: list[str]) -> int:
    cmds = {"check": cmd_check, "sample": cmd_sample, "scores": cmd_scores, "build": cmd_build}
    if len(argv) != 2 or argv[1] not in cmds:
        print(__doc__)
        return 2
    return cmds[argv[1]]()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
