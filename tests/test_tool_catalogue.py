"""Regressions for composite holders, archive identities and editable models."""
from pathlib import Path

import pytest
import trimesh
import yaml

import working
import working_oomp
from tool_catalogue import ROOT, read_yaml
from working_oomp_populate import holder_members


def test_compound_holder_membership():
    stand = holder_members(profile="basic_bench_stand")
    assert stand["tool_wrench_m10"] == 2
    assert "hex_key_4" in stand
    assert "hex_key_5" not in stand
    for profile in ("tool_screwdriver_hex_key_set_small", "tool_screwdriver_hex_key_set_small_reverse"):
        assert len(holder_members(profile=profile)) == 6
    for profile in ("tool_tdpb_glue_stick_prit_medium_knife", "tool_screwdriver_multi_quikpik_200_mm_knife"):
        assert holder_members(profile=profile)["tool_knife_exacto_17mm_black"] == 1
    assert holder_members(profile="quarter_inch", count=8, layered=True)["quarter_inch"] == 15


def test_filtered_build_and_manual_changes(tmp_path):
    options = {
        "root": tmp_path,
        "reference_root": ROOT / "source_file/tool_references",
        "filter": "teeny_turner",
    }
    working.main(**options)
    folders = list((tmp_path / "parts").iterdir())
    assert len(folders) == 1
    part = folders[0]
    record = read_yaml(part / "working.yaml")
    assert record["id"] == record["legacy_id"] == part.name
    assert (part / "drawing.cdr").is_file()
    assert (part / "holder_profile.svg").is_file()
    assert "teeny_turner" in (tmp_path / "HOLDERS.md").read_text(encoding="utf-8")
    assert len((tmp_path / "parts_source/catalogue.txt").read_text().splitlines()) > 1

    manual = {
        "parameters": {
            "lengths_mm": [17, 4, 7, 42],
        },
        "model_note": "Locally measured handle length.",
    }
    (part / "working_manual.yaml").write_text(yaml.safe_dump(manual), encoding="utf-8")
    readme = part / "README.md"
    readme.write_text("My bench notes\n\n" + readme.read_text(encoding="utf-8"), encoding="utf-8")
    working.main(**options)
    mesh = trimesh.load_mesh(part / "three_d_model/working.stl")
    assert mesh.is_volume
    assert mesh.extents.tolist() == pytest.approx([28, 70, 28])
    assert "My bench notes" in readme.read_text(encoding="utf-8")
    assert "Locally measured" in readme.read_text(encoding="utf-8")

    (part / "working_manual.yaml").write_text("taxonomy_2: wrong\n", encoding="utf-8")
    with pytest.raises(ValueError, match="identity field"):
        working_oomp.main(**options)

