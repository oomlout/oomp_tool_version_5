"""Materialize populated tools and their original documents as canonical OOMP parts."""
from copy import deepcopy
from pathlib import Path

import oomp

from working_tool_geometry import model_segments
from tool_catalogue import ROOT, cli_options, read_yaml, records, write_file, write_yaml


def merge(**kwargs):
    result = deepcopy(kwargs.get("original", {}))
    updates = kwargs.get("updates", {})
    for key, value in updates.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = merge(original=result[key], updates=value)
        else:
            result[key] = deepcopy(value)
    return result


def main(**kwargs):
    root = Path(kwargs.get("root", ROOT))
    reference_root = Path(kwargs.get("reference_root", root / "source_file" / "tool_references"))
    options = {
        **kwargs,
        "stage": "parts_source",
    }
    count = 0
    for source_path, source in records(**options):
        folder = root / "parts" / source_path.name
        manual_file = folder / "working_manual.yaml"
        manual = (read_yaml(manual_file) or {}) if manual_file.exists() else {}
        for field in manual:
            if field in ("id", "directory", "oomp_id", "key", "legacy_id", "classification",
                         "type", "size", "color", "description_main", "description_extra",
                         "manufacturer", "part_number") or field.startswith("taxonomy_"):
                raise ValueError(f"Edit identity field {field} in populate: {source_path.name}")
        part = merge(original=source, updates=manual)
        model_fields = {"model_kind", "parameters", "holder_profile"}
        if model_fields.intersection(manual) and "segments" not in manual.get("oobb_details", {}):
            part["oobb_details"]["segments"] = model_segments(**part)
        result = oomp.add_part(**part, make_files=False)
        if result["id"] != source_path.name:
            raise ValueError(f"OOMP ID differs from source directory {source_path.name}")
        for field in ("id", "directory", "md5", "md5_6", "md5_6_alpha"):
            part[field] = result[field]
        documents = {}
        for evidence in part["sources"]:
            for field in ("file", "image"):
                filename = evidence.get(field)
                if filename:
                    destination = evidence.get(f"part_{field}", filename)
                    if documents.setdefault(destination, filename) != filename:
                        raise ValueError(f"Two sources claim {destination} for {source_path.name}")
        for destination, filename in documents.items():
            write_file(folder / destination, (reference_root / filename).read_bytes())
        write_yaml(folder / "working.yaml", part)
        count += 1
    return count


load_parts = main


if __name__ == "__main__":
    main(**cli_options())

