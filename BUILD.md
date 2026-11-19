# Building the OOMP tool catalogue

Run `python working.py` from this checkout. To rebuild one tool, use an OOMP ID substring, for example `python working.py --filter teeny_turner`. The source snapshot and original documents are included, so ordinary builds work offline.

## Setup

Use Python 3.11 or later. Install the packages in [requirements.txt](requirements.txt) and put the sibling `oomlout_oomp_version_5` checkout on `PYTHONPATH` for `oomp` and `oomp_populate_helper`. Run the following commands in PowerShell from this folder.

```powershell
python -m pip install -r requirements.txt
$env:PYTHONPATH = "$(Resolve-Path ../oomlout_oomp_version_5);$env:PYTHONPATH"
python working.py
```

## Build order

| Stage | Input and output |
| --- | --- |
| `working_oomp_populate.py` | Combines editable tool declarations, holder membership, legacy identities and geometry recipes into `parts_source/<id>/working.yaml`. The active IDs are in `parts_source/catalogue.txt`. |
| `working_oomp.py` | Resolves each ID with OOMP, applies local overrides, and writes canonical YAML and source documents under `parts/<id>/`. |
| `working_scad.py` | Reads canonical geometry and writes `three_d_model/working.scad`, `working.stl` and `working.glb`. STL and OpenSCAD use millimetres with Z up. glTF uses metres with Y up. |
| `working_svg.py` | Draws plan, side and end views in `working.svg`. Tools with an independent external model also get a `holder_profile.svg` drawing of the source pocket. |
| `working_action.py` | Builds part pages, the catalogue, taxonomy navigation and the reverse holder index. |

Each stage accepts the same `--filter` option. The global indexes include every active tool with a built part page. `python action_make_scad_no_stl.py` writes the editable CAD source without exporting meshes. OpenSCAD can be used separately to inspect or render a source file. The standard build uses Manifold for mesh generation.

## Editing a tool

Edit the multiline dictionaries in [working_tool_declarations.py](working_tool_declarations.py). Each declaration names a source profile and either specifies the OOMP identity fields or selects a legacy identity. Add dimensions under `parameters`, explain what they describe under `model_note`, and list the documents that support them under `sources`. The shape builders and their defaults live in [working_tool_geometry.py](working_tool_geometry.py).

[Populate](working_oomp_populate.py) assigns tool quantities per layout. The paired glue-stick holder takes one glue stick and one craft knife. The two layered bit holders each have 15 places. The mixed stand accepts two M10 wrenches and the first five sizes of the six-key metric set. Each of these shares a tool record with the single-tool layouts. The two 13 × 137 mm marker records retain the branded and generic identities used by their source projects.

For local changes to a canonical part, create `parts/<id>/working_manual.yaml`. For example, an updated `model_note` or a measured value under `parameters` survives the next build. Change identifiers in the declarations. Handwritten text placed outside the generated comments in a README also survives regeneration.

## Taxonomy and sourcing

Levels 1–6 hold classification, type, size, colour, main description and extra description, in that order. Levels 7–13 are available for future refinements. Levels 14 and 15 hold manufacturer and part number. Joining non-empty levels yields the canonical ID. Existing OOMP records keep their original identifiers, including the `stationery` classification and legacy manufacturer number formatting. Blank manufacturer and part-number fields mean the source did not identify them. Archived distributor references retain their original identifiers and URLs.

The local [holder snapshot](source_file/tool_references/holder_v5.yaml) contains each layout's source ID and the original clearance primitives. [Legacy OOMP evidence](source_file/tool_references/legacy.yaml) records the identity, archived supplier fields and available CorelDRAW outlines. Wera and Mitutoyo PDFs, the OLFA photograph and the Wera datasheet product images are in [tool references](source_file/tool_references/), with source URLs on the relevant tool pages. Each holder thumbnail comes from that layout's `3dpr_presentation.png`. Links labelled “holder files” open the original part page when the holder checkout sits beside this repository.

To refresh the two local snapshots and holder previews, run `python import_tool_references.py` with the holder v5 and messy OOMP checkouts beside this repository. Then run the full build. Manufacturer documents can be refreshed from the URLs in the tool declarations. For the inherited layout and group definitions, see the [v4 tool recipes](https://github.com/oomlout/oomlout_oobb_version_4/blob/41f5386997faef4473c959dfb8c929864d7bf697/oobb_get_items_base_old.py), [v4 mixed and combined holder recipes](https://github.com/oomlout/oomlout_oobb_version_4/blob/41f5386997faef4473c959dfb8c929864d7bf697/oobb_get_items_oobb_old.py) and [vertical holder recipes](https://github.com/oomlout/oomlout_oobb_part_tool_holder_vertical/blob/93a962a09e0c275c3cfa62187182ac3203bde1b2/scad.py).

