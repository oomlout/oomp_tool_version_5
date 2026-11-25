"""Generate the per-tool pages, taxonomy navigation and holder-to-tool index."""
from collections import defaultdict
from pathlib import Path

from tool_catalogue import ROOT, cli_options, read_yaml, records, write_file


START = "<!-- oomp-tools:start -->"
END = "<!-- oomp-tools:end -->"
HOLDER_PROJECT = "https://github.com/oomlout/oomlout_oobb_part_holder_tool_version_5"


def holder_readme(identifier):
    return f"{HOLDER_PROJECT}/blob/main/parts/{identifier}/README.md#assembly"


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
    if part["model_kind"] == "photo_reference":
        return "Photo-based tool model"
    return "External tool reference"


def part_page(**kwargs):
    folder = kwargs["folder"]
    part = kwargs["part"]
    title = part["title"]
    family = part["type"]
    family_path = f'../../navigation_oomp/{part["classification"]}/{family}/README.md'
    lines = [f"# {title}", "", f'[Tool catalogue](../../README.md) / [{family.replace("_", " ")}]({family_path})',
             "", f'`{part["oomp_id"]}`', "", f'**{model_label(part)}.** {part["model_note"]}']
    if part.get("note"):
        lines.extend(["", part["note"]])
    if (folder / "three_d_model/render.png").is_file():
        lines.extend(["", f"![Blender render of {title}](three_d_model/render.png)"])
    files = {
        "Photograph and measurements": [
            ("Workshop photograph", part.get("parameters", {}).get("photo", "")),
            ("Measurements and assumptions", "measurements.md"),
            ("Photo with model outline", "photo_overlay.svg"),
            *[(f"Identification research ({note.stem.removeprefix('research_')})", note.name)
              for note in sorted(folder.glob("research_*.md"))],
        ],
        "Model files": [
            ("OpenSCAD", "three_d_model/working.scad"),
            ("STL · mm", "three_d_model/working.stl"),
            ("glTF · metres", "three_d_model/working.glb"),
            ("Blender scene", "three_d_model/working.blend"),
            ("OOMP record", "working.yaml"),
        ],
        "Drawings and views": [
            ("Studio render", "three_d_model/render.png"),
            ("Top render", "three_d_model/render_top.png"),
            ("Dimension drawing", "working.svg"),
            ("Holder clearance drawing", "holder_profile.svg"),
        ],
    }
    for heading, entries in files.items():
        links = [f"[{label}]({filename})" for label, filename in entries if (folder / filename).is_file()]
        if links:
            lines.extend(["", f"## {heading}", "", " · ".join(links)])
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
    guide = next((holder for holder in part["holders"] if
                  (folder.parents[1] / "source_file/tool_references/holders" / (holder["id"] + ".pdf")).is_file()), None)
    example = next((holder for holder in part["holders"] if "mixed_tools" not in holder["id"]), part["holders"][0])
    identifier = (guide or example)["id"]
    picture = f"../../source_file/tool_references/holders/{identifier}.jpg"
    preview = f"![Source holder CAD preview]({picture})"
    destination = f"../../HOLDERS.md#{identifier}"
    if guide:
        destination = holder_readme(identifier)
        preview = f"[{preview}]({destination})"
    lines.extend(["", preview, "", f'Holder preview from [OOBB part holder v5]({destination}).'])
    if guide:
        lines.extend(["", f"[Holder README and assembly instructions]({holder_readme(identifier)}) · [Print booklet (PDF)](../../source_file/tool_references/holders/{identifier}.pdf)"])
    update_page(folder / "README.md", lines)


def indexes(**kwargs):
    root = Path(kwargs.get("root", ROOT))
    manifest = (root / "parts_source/catalogue.txt").read_text(encoding="utf-8").splitlines()
    families = defaultdict(list)
    holders = defaultdict(list)
    published = 0
    rendered_tools = []
    for identifier in manifest:
        folder = root / "parts" / identifier
        if not (folder / "README.md").exists():
            continue
        part = read_yaml(folder / "working.yaml")
        published += 1
        if (folder / "three_d_model/render.png").is_file():
            rendered_tools.append(part)
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
        if (root / "source_file/tool_references/holders" / (identifier + ".pdf")).is_file():
            entry = f'[{label}]({holder_readme(identifier)}) · [Print booklet (PDF)](source_file/tool_references/holders/{identifier}.pdf)'
        else:
            entry = f'[{label}](source_file/tool_references/holders/{identifier}.jpg) · [holder files](../oomlout_oobb_part_holder_tool_version_5/parts/{identifier}/README.md)'
        lines.append(f'| <a id="{identifier}"></a>{entry} | {"<br>".join(links)} |')
    update_page(root / "HOLDERS.md", lines)
    lines = ["# OOMP tool catalogue", "",
             "Workshop tools and stationery used by OOBB part holder v5. Each part page includes a dimension drawing, editable OpenSCAD, exchange models and the layouts that use it.",
             "", "[Build and edit the catalogue](BUILD.md) · [Source files](source_file/tool_references/)"]
    if rendered_tools:
        lines.extend(["", "## Blender renders", ""])
        # Two tools per row keeps each preview large enough to inspect on GitHub.
        for start in range(0, len(rendered_tools), 2):
            headings = []
            previews = []
            for part in rendered_tools[start:start + 2]:
                directory = f'parts/{part["oomp_id"]}'
                title = part["title"]
                page = f"{directory}/README.md"
                headings.append(f"[{title}]({page})")
                previews.append(f"[![{title}]({directory}/three_d_model/render.png)]({page})")
            lines.extend(["| " + " | ".join(headings) + " |", "| " + " | ".join("---" for _ in headings) + " |",
                          "| " + " | ".join(previews) + " |", ""])
        if (root / "parts/PHOTO_MODELS.md").is_file():
            lines.append("[Photographs, dimensions and modelling notes](parts/PHOTO_MODELS.md)")
    guides = [(part, holder["id"]) for part in rendered_tools for holder in part["holders"]
              if (root / "source_file/tool_references/holders" / (holder["id"]+".pdf")).is_file()]
    if guides:
        lines.extend(["", "## Tools in their holders", "", "The illustrated booklets show the printed holders and how the tools fit into their openings.", ""])
        for part, identifier in guides:
            lines.append(f'- [{part["title"]} holder README]({holder_readme(identifier)}) · [Print booklet (PDF)](source_file/tool_references/holders/{identifier}.pdf)')
    lines.extend(["", "## Catalogue", "",
             f"{published} tool records cover {len(holders)} holder layouts. Browse by [OOMP taxonomy](navigation_oomp/README.md) or [holder layout](HOLDERS.md).",
             "", "| Tool | Geometry |", "| --- | --- |"])
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

