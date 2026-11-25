"""Declare tools, resolve holder membership and write the parts_source stage."""
from contextlib import chdir
from copy import deepcopy
from pathlib import Path

from filelock import FileLock
from oomp_populate_helper import build_oomp_id, write_extras

from tool_catalogue import ROOT, cli_options, matches, read_yaml, write_file
from working_tool_declarations import get_tools
from working_tool_geometry import model_segments


HEX_KEYS = [
    "hex_key_1_5", "hex_key_2", "hex_key_2_5", "hex_key_3", "hex_key_4", "hex_key_5",
]


def holder_members(**kwargs):
    profile = kwargs["profile"]
    count = kwargs.get("count", 1)
    layered = kwargs.get("layered", False)
    row_count = kwargs.get("row_count", 1)
    if profile == "four_spanners":
        return {
            "tool_wrench_m13": 1,
            "tool_wrench_m10": 1,
            "tool_wrench_m8": 1,
            "tool_wrench_m7": 1,
        }
    if profile == "tool_knife_utility_17_mm_blade":
        return {
            "tool_knife_utility_17_mm_blade": 1,
            "tool_knife_exacto_17mm_black": 1,
        }
    if profile == "basic_bench_stand":
        return {
            "tool_side_cutters_generic_110_mm_red": 1,
            "tool_pliers_needlenose_generic_130_mm_blue": 1,
            "tool_wire_strippers_generic_120_red": 1,
            "tool_screwdriver_hex_m1d5_wera_60_mm": 1,
            "tool_screwdriver_hex_m2_wera_60_mm": 1,
            "tool_screwdriver_hex_m2d5_wera_60_mm": 1,
            "tool_screwdriver_multi_quikpik_200_mm_knife": 1,
            "tool_wrench_m7": 1,
            "tool_wrench_m8": 1,
            "tool_wrench_m10": 2,
            "tool_knife_exacto_17mm_black": 1,
            "tool_marker_sharpie": 1,
            "hex_key_1_5": 1,
            "hex_key_2": 1,
            "hex_key_2_5": 1,
            "hex_key_3": 1,
            "hex_key_4": 1,
        }
    if profile.startswith("tool_screwdriver_hex_key_set_small"):
        return dict.fromkeys(HEX_KEYS, 1)
    if profile == "tool_tdpb_glue_stick_prit_medium_knife":
        return {
            "tool_tdpb_glue_stick_prit_medium": 1,
            "tool_knife_exacto_17mm_black": 1,
        }
    if profile == "tool_screwdriver_multi_quikpik_200_mm_knife":
        return {
            "tool_screwdriver_multi_quikpik_200_mm_knife": 1,
            "tool_knife_exacto_17mm_black": 1,
        }
    if layered:
        count += count - 1
    elif row_count > 1:
        count = row_count * count - row_count // 2
    return {
        profile: count,
    }


def single_profile(**kwargs):
    key = kwargs["key"]
    profiles = kwargs["profiles"]
    if key in HEX_KEYS:
        segments = [profiles["tool_screwdriver_hex_key_set_small"][HEX_KEYS.index(key)]]
    elif key == "tool_knife_exacto_17mm_black" and key not in profiles:
        segments = profiles["tool_knife_utility_17_mm_blade"]
    elif key == "tool_screwdriver_multi_quikpik_200_mm_knife":
        segments = profiles[key][1:]  # First cutter belongs to the companion knife.
    else:
        segments = profiles[key]
    origin = segments[0]["pos"]
    result = deepcopy(segments)
    for section in result:
        section["pos"] = [value - offset for value, offset in zip(section["pos"], origin)]
    return result


def make_record(**kwargs):
    tool = deepcopy(kwargs["tool"])
    legacy = kwargs.get("legacy", {})
    holders = kwargs["holders"]
    profiles = kwargs["profiles"]
    levels = {
        1: "classification",
        2: "type",
        3: "size",
        4: "color",
        5: "description_main",
        6: "description_extra",
        14: "manufacturer",
        15: "part_number",
    }
    key = tool["key"]
    for level, field in levels.items():
        tool[field] = tool.get(field, legacy.get(field, ""))
        tool[f"taxonomy_{level}"] = tool[field]
    identifier = build_oomp_id(tool)
    if tool.get("legacy_id", identifier) != identifier:
        raise ValueError(f"Legacy identity changed for {identifier}")
    tool["oomp_id"] = identifier
    tool["name"] = identifier
    tool["name_space"] = identifier.replace("_", " ")
    tool["name_proper"] = tool["title"]
    tool["name_upper"] = tool["title"].upper()
    tool["holders"] = holders
    tool["model_kind"] = tool.get("model_kind", "holder_envelope")
    tool.setdefault("model_note", "Geometry follows the holder clearance profile. Its dimensions describe the pocket used in the source design. Physical tool dimensions and fit have yet to be measured.")
    tool["holder_profile"] = single_profile(key=key, profiles=profiles)
    tool["oobb_type"] = "tool_reference"
    tool["oobb_details"] = {
        "oobb_type": "tool_reference",
        "run_scad": True,
        "run_solidcraft": False,
        "units": "mm",
        "segments": model_segments(**tool),
    }
    tool["svg_details"] = {
        "svg_name": "tool_reference",
        "units": "mm",
    }
    sources = tool.setdefault("sources", [])
    if key in ("picquic_teeny_turner", "sharpie_style_13mm", "quarter_inch"):
        sources.append({
            "title": "OOBB vertical holder recipe",
            "url": "https://github.com/oomlout/oomlout_oobb_part_tool_holder_vertical/blob/93a962a09e0c275c3cfa62187182ac3203bde1b2/scad.py",
            "supports": "Original vertical holder tool selection and pocket dimensions.",
        })
    else:
        sources.append({
            "title": "OOBB v4 tool shapes",
            "url": "https://github.com/oomlout/oomlout_oobb_version_4/blob/41f5386997faef4473c959dfb8c929864d7bf697/oobb_get_items_base_old.py",
            "supports": "Upstream tool naming and clearance geometry used in the holder migration.",
        })
    if legacy:
        sources.append({
            "title": "Archived OOMP part",
            "url": legacy["link_main"],
            "supports": "Legacy taxonomy, identity and archived sourcing fields.",
        })
    if legacy.get("drawing"):
        sources.append({
            "title": "Archived OOMP outline",
            "url": legacy["link_main"].replace("/tree/", "/blob/") + "/drawing.cdr",
            "file": legacy["drawing"],
            "supports": "Original CorelDRAW reference drawing.",
        })
    # Keep descriptive originals in source_file and standard filenames in parts.
    for source in sources:
        filename = source.get("file", "")
        if filename.endswith(".pdf"):
            source.setdefault("part_file", "datasheet.pdf")
        elif filename.endswith(".cdr"):
            source.setdefault("part_file", "drawing.cdr")
        elif filename.endswith(".jpg"):
            source.setdefault("part_file", "image.jpg")
        if source.get("image"):
            source.setdefault("part_image", "image.jpg")
    tool["distributors"] = []
    if legacy.get("link_distributor_amazon"):
        tool["distributors"].append({
            "name": "Amazon UK",
            "part_number": legacy["part_number_distributor_amazon"],
            "url": legacy["link_distributor_amazon"],
            "source": "Archived OOMP record",
        })
    return tool


def main(**kwargs):
    root = Path(kwargs.get("root", ROOT)).resolve()
    reference_root = Path(kwargs.get("reference_root", root / "source_file" / "tool_references"))
    tools = get_tools(**kwargs)
    snapshot = read_yaml(reference_root / "holder_v5.yaml")
    legacy = read_yaml(reference_root / "legacy.yaml")
    memberships = {tool["key"]: [] for tool in tools}
    if len(memberships) != len(tools):
        raise ValueError("Duplicate declaration key")
    for holder_id, layout in snapshot["layouts"].items():
        for key, quantity in holder_members(**layout).items():
            memberships[key].append({
                "id": holder_id,
                "layout": layout["layout"],
                "quantity": quantity,
                "source_id": layout["source_id"],
            })
    identifiers = set()
    extras = []
    for tool in tools:
        key = tool["key"]
        if not memberships[key]:
            raise ValueError(f"No holder for {key}")
        record = make_record(
            tool=tool,
            legacy=legacy[tool["legacy_id"]] if "legacy_id" in tool else {},
            holders=memberships[key],
            profiles=snapshot["profiles"],
        )
        identifier = record["oomp_id"]
        if identifier in identifiers:
            raise ValueError(f"Duplicate OOMP ID {identifier}")
        identifiers.add(identifier)
        if matches(identifier, **kwargs):
            extras.append(record)
    if not extras:
        raise ValueError(f"No tool matches {kwargs.get('filter')!r}")
    import working_oomp_populate_extra_detail
    working_oomp_populate_extra_detail.main(extras=extras)
    # The shared OOMP writer resolves parts_source relative to the working directory.
    (root / "build").mkdir(exist_ok=True)
    with FileLock(root / "build" / "populate.lock"), chdir(root):
        write_extras(extras)
        write_file(root / "parts_source" / "catalogue.txt", "\n".join(sorted(identifiers)) + "\n")
    return len(extras)


if __name__ == "__main__":
    main(**cli_options())
