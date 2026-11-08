import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("benchmark", ROOT / "scripts" / "benchmark.py")
bm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bm)


def row(p, c, status, url="", source=""):
    return {"platform_id": p, "criterion_id": c, "status": status, "value": "", "source_type": source,
            "url": url, "accessed": "2026-11-08", "note": "n"}


def test_dataset_is_valid():
    plats = [p["platform_id"] for p in bm.included_platforms()]
    crits = [c["criterion_id"] for c in bm.criteria()]
    assert bm.validate(bm.read_csv(bm.EVIDENCE), plats, crits) == []


def test_every_included_platform_has_a_signal_url():
    for p in bm.included_platforms():
        assert p["signal"] and p["signal_url"].startswith("http"), p["platform_id"]


def test_documented_requires_doc_source_and_url():
    errs = bm.validate([row("x", "ch_voice", "documented", "https://a", "marketing")], ["x"], ["ch_voice"])
    assert any("documented needs" in e for e in errs)
    errs = bm.validate([row("x", "ch_voice", "vendor_states", "", "blog")], ["x"], ["ch_voice"])
    assert any("missing url" in e for e in errs)


def test_not_found_cannot_carry_url():
    errs = bm.validate([row("x", "ch_voice", "not_found", "https://a")], ["x"], ["ch_voice"])
    assert any("must not carry" in e for e in errs)


def test_missing_cell_is_reported():
    errs = bm.validate([row("x", "ch_voice", "not_found")], ["x"], ["ch_voice", "ch_chat"])
    assert "missing cell (x, ch_chat)" in errs


def test_na_rule_only_when_parent_not_found():
    rows = [row("x", "ch_voice", "not_found"), row("x", "tel_byoc", "not_found"),
            row("y", "ch_voice", "documented", "https://a", "docs"), row("y", "tel_byoc", "not_found")]
    out = {(r["platform_id"], r["criterion_id"]): r["status"] for r in bm.apply_na(rows)}
    assert out[("x", "tel_byoc")] == "not_applicable"
    assert out[("y", "tel_byoc")] == "not_found"
