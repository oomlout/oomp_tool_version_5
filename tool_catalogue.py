"""Shared paths and file operations for the tool catalogue."""
import argparse
import os
import tempfile
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parent


def write_file(path, content):
    data = content.encode("utf-8") if isinstance(content, str) else content
    if path.is_file() and path.read_bytes() == data:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as output:
        temporary = Path(output.name)
        try:
            output.write(data)
        except BaseException:
            output.close()
            temporary.unlink(missing_ok=True)
            raise
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def read_yaml(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def write_yaml(path, data):
    write_file(path, yaml.safe_dump(data, allow_unicode=True, sort_keys=False))


def matches(identifier, **kwargs):
    selected = kwargs.get("filter", "")
    if isinstance(selected, str):
        return selected in identifier
    return any(item in identifier for item in selected)


def records(**kwargs):
    root = Path(kwargs.get("root", ROOT))
    stage = kwargs.get("stage", "parts")
    manifest = root / "parts_source" / "catalogue.txt"
    identifiers = manifest.read_text(encoding="utf-8").splitlines()
    selected = [identifier for identifier in identifiers if matches(identifier, **kwargs)]
    if not selected:
        raise ValueError(f"No tool matches {kwargs.get('filter')!r}")
    for identifier in selected:
        folder = root / stage / identifier
        yield folder, read_yaml(folder / "working.yaml")


def cli_options():
    parser = argparse.ArgumentParser(description="Build the OOMP tool catalogue")
    parser.add_argument("--filter", default="", help="Substring of a tool's OOMP ID")
    parser.add_argument("--render-blender", action="store_true", help="Render supported studio models after building their meshes")
    return vars(parser.parse_args())

