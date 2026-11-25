"""Refresh the local OOBB and legacy OOMP evidence used by populate."""
from io import BytesIO
from pathlib import Path

from PIL import Image

from tool_catalogue import ROOT, read_yaml, write_file, write_yaml
from working_tool_declarations import get_tools


def collect_holders(**kwargs):
    source = Path(kwargs.get("holder_root", ROOT.parent / "oomlout_oobb_part_holder_tool_version_5"))
    target = Path(kwargs.get("reference_root", ROOT / "source_file" / "tool_references"))
    preview_size = kwargs.get("preview_size", (720, 540))
    include_previews = kwargs.get("include_previews", True)
    profiles = {}
    layouts = {}
    manifest = source / "parts_source" / "catalogue.txt"
    for identifier in manifest.read_text(encoding="utf-8").splitlines():
        record = read_yaml(source / "parts_source" / identifier / "working.yaml")
        profile = record["profile"]
        # Match new holder taxonomy to the original OOMP tool record keys.
        profile = profile.replace("tool_spanner_", "tool_wrench_").replace("_precision_tall_60_mm", "_wera_60_mm")
        geometry = record["oobb_details"]["profile"]
        if profiles.setdefault(profile, geometry) != geometry:
            raise ValueError(f"Inconsistent profile {profile} in {identifier}")
        layouts[identifier] = {
            "profile": profile,
            "title": record["title"],
            "layout": record["layout"],
            "count": record["count"] if "count" in record else 1,
            "layered": record.get("layered", False),
            "source_id": record.get("source_id", identifier),
        }
        if "row_count" in record:
            layouts[identifier]["row_count"] = record["row_count"]
        if not include_previews:
            continue
        with Image.open(source / "parts" / identifier / "3dpr_presentation.png") as image:
            image.thumbnail(preview_size, Image.Resampling.LANCZOS)
            output = BytesIO()
            image.convert("RGB").save(output, format="JPEG", quality=83)
        write_file(target / "holders" / f"{identifier}.jpg", output.getvalue())
    snapshot = {
        "repository": source.name,
        "source_manifest": "parts_source/catalogue.txt",
        "profiles": profiles,
        "layouts": layouts,
    }
    write_yaml(target / "holder_v5.yaml", snapshot)


def collect_legacy(**kwargs):
    source = Path(kwargs.get("legacy_root", ROOT.parent / "oomlout_oomp_version_1_messy"))
    target = Path(kwargs.get("reference_root", ROOT / "source_file" / "tool_references"))
    fields = (
        "classification", "type", "size", "color", "description_main",
        "description_extra", "manufacturer", "part_number", "link_main",
        "link_buy_1", "link_distributor_amazon", "part_number_distributor_amazon",
    )
    legacy = {}
    for tool in get_tools(**kwargs):
        identifier = tool.get("legacy_id")
        if not identifier:
            continue
        directory = source / "parts" / identifier
        record = read_yaml(directory / "working.yaml")
        entry = {}
        for field in fields:
            if field in record:
                entry[field] = record[field]
        drawing = directory / "drawing.cdr"
        if drawing.exists():
            entry["drawing"] = f"{identifier}.cdr"
            write_file(target / entry["drawing"], drawing.read_bytes())
        legacy[identifier] = entry
    write_yaml(target / "legacy.yaml", legacy)


def main(**kwargs):
    collect_holders(**kwargs)
    collect_legacy(**kwargs)


if __name__ == "__main__":
    main()

