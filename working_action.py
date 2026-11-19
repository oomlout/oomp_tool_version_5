"""Generate the per-tool pages, taxonomy navigation and holder-to-tool index."""
from collections import defaultdict
from pathlib import Path

from tool_catalogue import ROOT, cli_options, read_yaml, records, write_file


START = "<!-- oomp-tools:start -->"
END = "<!-- oomp-tools:end -->"


def update_page(path, lines):
    block = "\n".join([START, *lines, END]) + "\n"
    original = path.read_text(encoding="utf-8") if path.exists() else ""
    if START in original and END in original:
        head, rest = original.split(START, 1)
        _, tail = rest.split(END, 1)
        content = head + block.rstrip("\n") + tail
    elif START in original or END in original:
        raise ValueError(f"Incomplete generated section in {path}")
    else:
        content = original.rstrip() + ("\n\n" if original.strip() else "") + block
    write_file(path, content)


def model_label(part):
    if part["model_kind"] == "holder_envelope":
        return "Holder clearance profile"
    return "External tool reference"


def part_page(**kwargs):
    folder = kwargs["folder"]
    part = kwargs["part"]
    title = part["title"]
    lines = [f"# {title}", "", f'`{part["oomp_id"]}`', "", f'**{model_label(part)}.** {part["model_note"]}']
    if part.get("note"):
        lines.extend(["", part["note"]])
    files = (
        ("Dimension drawing", "working.svg"),
        ("Holder clearance drawing", "holder_profile.svg"),
        ("OpenSCAD", "three_d_model/working.scad"),
        ("STL · mm", "three_d_model/working.stl"),
        ("glTF · metres", "three_d_model/working.glb"),
        ("OOMP record", "working.yaml"),
    )
    links = [f"[{label}]({filename})" for label, filename in files if (folder / filename).is_file()]
    lines.extend(["", " · ".join(links)])
    if (folder / "working.svg").exists():
        lines.extend(["", f"![Orthographic drawing of {title}](working.svg)"])
    if part["sources"] or part["distributors"]:
        lines.extend(["", "## Sourcing and documentation", ""])
    for source in part["sources"]:
        local = source.get("part_file", source.get("file"))
        links = [f'[{source["title"]}]({source["url"]})']
        if local:
            links.append(f"[Local copy]({local})")
        lines.append(f'- {source["supports"]} {" · ".join(links)}')
    for supplier in part["distributors"]:
        lines.append(f'- Archived distributor reference [{supplier["name"]} {supplier["part_number"]}]({supplier["url"]}).')
    for source in part["sources"]:
        photo = source.get("part_image", source.get("image", source.get("part_file", "")))
        if photo.endswith(".jpg"):
            lines.extend(["", f'![{source["title"]} product image]({photo})'])
    lines.extend(["", "## Holder layouts", "", "| Layout | Places for this tool |", "| --- | ---: |"])
    for holder in part["holders"]:
        identifier = holder["id"]
        name = identifier.removeprefix("oobb_part_holder_tool_").replace("_", " ")
        lines.append(f'| [{name}](../../HOLDERS.md#{identifier}) | {holder["quantity"]} |')
    example = next((holder for holder in part["holders"] if "mixed_tools" not in holder["id"]), part["holders"][0])
    identifier = example["id"]
    picture = f"../../source_file/tool_references/holders/{identifier}.jpg"
    lines.extend(["", f"![Source holder CAD preview]({picture})", "",
                  f'Holder preview from [OOBB part holder v5](../../HOLDERS.md#{identifier}).'])
    update_page(folder / "README.md", lines)


def indexes(**kwargs):
    root = Path(kwargs.get("root", ROOT))
    manifest = (root / "parts_source/catalogue.txt").read_text(encoding="utf-8").splitlines()
    families = defaultdict(list)
    holders = defaultdict(list)
    published = 0
    for identifier in manifest:
        folder = root / "parts" / identifier
        if not (folder / "README.md").exists():
            continue
        part = read_yaml(folder / "working.yaml")
        published += 1
        families[(part["classification"], part["type"])].append(part)
        for holder in part["holders"]:
            holders[holder["id"]].append((part, holder["quantity"]))
    nav = root / "navigation_oomp"
    nav_page = ["# Tool taxonomy", ""]
    classes = defaultdict(list)
    for (classification, family), tools in sorted(families.items()):
        classes[classification].append(family)
        lines = [f'# {family.replace("_", " ").title()}', "", "| Tool | Geometry |", "| --- | --- |"]
        for part in tools:
            lines.append(f'| [{part["title"]}](../../../parts/{part["oomp_id"]}/README.md) | {model_label(part)} |')
        update_page(nav / classification / family / "README.md", lines)
    for classification, groups in classes.items():
        lines = [f"# {classification.title()}", ""]
        nav_page.extend([f"## [{classification.title()}]({classification}/README.md)", ""])
        for family in groups:
            label = family.replace("_", " ").title()
            count = len(families[classification, family])
            lines.append(f"- [{label}]({family}/README.md) ({count})")
            nav_page.append(f"- [{label}]({classification}/{family}/README.md) ({count})")
        nav_page.append("")
        update_page(nav / classification / "README.md", lines)
    update_page(nav / "README.md", nav_page)
    lines = [
        "# Tools by holder", "",
        f"{len(holders)} layouts from the OOBB part holder v5 catalogue. Each entry gives the number of places for each tool. The source checkout stores the original README and print files under `parts/<holder ID>/`.", "",
        "[Holder inventory](../oomlout_oobb_part_holder_tool_version_5/TOOLS.md) · [Local source snapshot](source_file/tool_references/holder_v5.yaml)", "",
        "| Holder and source preview | Tools and quantities |", "| --- | --- |",
    ]
    for identifier in sorted(holders):
        label = identifier.removeprefix("oobb_part_holder_tool_").replace("_", " ")
        links = [f'[{part["title"]}](parts/{part["oomp_id"]}/README.md) × {quantity}'
                 for part, quantity in holders[identifier]]
        lines.append(f'| <a id="{identifier}"></a>[{label}](source_file/tool_references/holders/{identifier}.jpg) · [holder files](../oomlout_oobb_part_holder_tool_version_5/parts/{identifier}/README.md) | {"<br>".join(links)} |')
    update_page(root / "HOLDERS.md", lines)
    lines = ["# OOMP tool catalogue", "",
             "Workshop tools and stationery used by OOBB part holder v5. Each part page includes a dimension drawing, editable OpenSCAD, exchange models and the layouts that use it.",
             "", "[Build and edit the catalogue](BUILD.md) · [Source files](source_file/tool_references/)", "",
             "## Catalogue", "",
             f"{published} tool records cover {len(holders)} holder layouts. Browse by [OOMP taxonomy](navigation_oomp/README.md) or [holder layout](HOLDERS.md).",
             "", "| Tool | Geometry |", "| --- | --- |"]
    for group in sorted(families):
        for part in families[group]:
            lines.append(f'| [{part["title"]}](parts/{part["oomp_id"]}/README.md) | {model_label(part)} |')
    update_page(root / "README.md", lines)


def main(**kwargs):
    for folder, part in records(**kwargs):
        part_page(folder=folder, part=part)
    indexes(**kwargs)


if __name__ == "__main__":
    main(**cli_options())

