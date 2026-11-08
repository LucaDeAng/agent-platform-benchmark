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


# --- dimensions, scores, index, sensitivity, export ---------------------------------------------

import json
from fractions import Fraction as F


def real_model():
    plats, crits, dims, rows = bm.load_scored()
    return plats, crits, dims, rows, bm.compute(plats, crits, dims, rows)


def synthetic(statuses):
    """statuses: {platform: [status of c1, status of c2]}; two dimensions with one criterion each."""
    plats = [{"platform_id": p} for p in statuses]
    crits = [{"criterion_id": "c1", "label": "C1", "dimension_id": "d1"},
             {"criterion_id": "c2", "label": "C2", "dimension_id": "d2"}]
    dims = [{"dimension_id": "d1", "order": "1", "default_weight": "1/2"},
            {"dimension_id": "d2", "order": "2", "default_weight": "1/2"}]
    rows = [row(p, c, s) for p, ss in statuses.items() for c, s in zip(("c1", "c2"), ss)]
    return plats, crits, dims, rows


def test_every_criterion_maps_to_exactly_one_dimension():
    crits, dims = bm.criteria(), bm.dimensions()
    assert bm.validate_dimensions(dims, crits) == []
    mapped = [c for cs in bm.dimension_criteria(dims, crits).values() for c in cs]
    assert sorted(mapped) == sorted(c["criterion_id"] for c in crits) and len(mapped) == 24


def test_value_table_matches_method():
    assert bm.cell_bounds("documented") == (1, 1)
    assert bm.cell_bounds("vendor_states") == (F(1, 2), F(1, 2))
    assert bm.cell_bounds("not_found") == (0, 1)
    assert bm.cell_bounds("not_applicable") == (0, 1)
    assert bm.cell_bounds("vendor_states", F(0)) == (0, 0)


def test_not_found_is_a_range_not_a_zero():
    plats, crits, dims, rows = synthetic({"x": ["not_found", "not_found"]})
    m = bm.compute(plats, crits, dims, rows)
    assert m["ds"][("x", "d1")] == (0, 1, 0)
    assert m["idx"]["x"] == (0, 1, 0)


def test_index_is_weighted_mean_of_dimensions():
    plats, crits, dims, rows = synthetic({"x": ["documented", "vendor_states"]})
    ds = bm.dimension_scores({("x", "c1"): "documented", ("x", "c2"): "vendor_states"}, ["x"],
                             bm.dimension_criteria(dims, crits))
    idx = bm.index_scores(ds, ["x"], {"d1": F(3, 4), "d2": F(1, 4)})
    assert idx["x"] == (F(7, 8), F(7, 8), 1)


def test_range_width_equals_one_minus_coverage_on_real_data():
    *_, m = real_model()
    for lo, hi, cov in list(m["ds"].values()) + list(m["idx"].values()):
        assert 0 <= lo <= hi <= 1
        assert hi - lo == 1 - cov


def test_competition_ranks_share_ties():
    assert bm.competition_ranks({"a": F(1), "b": F(1), "c": F(1, 2)}) == {"a": 1, "b": 1, "c": 3}


def test_possible_ranks_and_bands():
    idx = {"a": (F(9, 10), F(1), 0), "b": (F(1, 2), F(8, 10), 0), "c": (F(0), F(1), 0)}
    assert bm.possible_ranks(idx) == {"a": (1, 2), "b": (2, 3), "c": (1, 3)}
    assert bm.bands(idx) == {"a": 1, "c": 1, "b": 2}


def test_ranking_rule_holds_only_without_overlap():
    separated = bm.compute(*synthetic({"a": ["documented", "documented"], "b": ["documented", "vendor_states"],
                                       "c": ["vendor_states", "vendor_states"]}))
    assert separated["n_overlap"] == 0 and separated["ranking_holds"]
    unknown = bm.compute(*synthetic({"a": ["documented", "documented"], "b": ["documented", "vendor_states"],
                                     "c": ["not_found", "not_found"]}))
    assert unknown["n_overlap"] == 2 and not unknown["rule_a"] and not unknown["ranking_holds"]


def test_sensitivity_scenarios_are_the_ones_in_method():
    *_, m = real_model()
    kinds = [r["kind"] for r in m["runs"]]
    assert kinds[0] == "default"
    assert kinds.count("weights") == 4 and kinds.count("value_table") == 2 and kinds.count("leave_one_out") == 24


def check_record(record, spec, where):
    assert set(record) == set(spec["required"]) == set(spec["properties"]), where


def test_export_follows_schema_and_keys():
    plats, crits, dims, rows, m = real_model()
    data = json.loads(json.dumps(bm.build_export(plats, crits, dims, rows, m)))
    schema = json.loads((bm.EXPORT.parent / "platforms.schema.json").read_text(encoding="utf-8"))
    check_record(data, schema, "top level")
    ids = {}
    for key in ("value_table", "dimensions", "criteria", "platforms", "evidence", "dimension_scores",
                "index_scores", "scenarios"):
        spec = schema["properties"][key]["items"]
        for rec in data[key]:
            check_record(rec, spec, key)
        ids[key] = [r["id"] for r in data[key]]
        assert len(ids[key]) == len(set(ids[key])), key
    assert len(data["evidence"]) == 17 * 24
    for rec in data["evidence"] + data["dimension_scores"] + data["index_scores"]:
        assert rec["platform_id"] in ids["platforms"]
    for rec in data["evidence"]:
        assert rec["criterion_id"] in ids["criteria"] and rec["dimension_id"] in ids["dimensions"]
        assert (rec["url"] is None) == (rec["status"] in ("not_found", "not_applicable"))


def test_committed_export_is_current():
    plats, crits, dims, rows, m = real_model()
    expected = json.loads(json.dumps(bm.build_export(plats, crits, dims, rows, m)))
    assert json.loads(bm.EXPORT.read_text(encoding="utf-8")) == expected
