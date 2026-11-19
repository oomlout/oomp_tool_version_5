"""Build the editable OpenSCAD source and its catalogue exchange meshes."""
import json

import manifold3d as manifold
import numpy as np
import trimesh

from tool_catalogue import records, write_file


def solids(**kwargs):
    segments = kwargs["segments"]
    facets = kwargs.get("facets", 64)
    result = []
    for section in segments:
        if section["shape"] == "cylinder":
            solid = manifold.Manifold.cylinder(
                section["h"], section["r"], section.get("r2", section["r"]),
                section.get("facets", facets),
            )
        elif section["shape"] == "polygon":
            polygon = manifold.CrossSection([section["points"]], manifold.FillRule.EvenOdd)
            solid = polygon.extrude(section["h"])
        else:
            raise ValueError(f"Unknown model primitive {section['shape']}")
        result.append(solid.rotate(section["rot"]).translate(section["pos"]))
    return result


def build_mesh(**kwargs):
    pieces = solids(**kwargs)
    union = manifold.Manifold.batch_boolean(pieces, manifold.OpType.Add)
    geometry = union.to_mesh()
    mesh = trimesh.Trimesh(
        vertices=geometry.vert_properties[:, :3],
        faces=geometry.tri_verts,
        process=True,
    )
    if not mesh.is_volume or len(mesh.split(only_watertight=False)) != 1:
        raise ValueError("Tool recipe must produce one closed, positive-volume solid")
    return mesh


def scad_source(**kwargs):
    segments = kwargs["segments"]
    title = kwargs.get("title", "Tool reference")
    note = kwargs.get("model_note", "")
    facets = kwargs.get("facets", 64)
    lines = [f"// {title}", f"// {note}", "// Units: mm", f"$fn = {facets};", "union() {"]
    for section in segments:
        position = json.dumps(section["pos"])
        rotation = json.dumps(section["rot"])
        lines.append(f"    translate({position}) rotate({rotation})")
        if section["shape"] == "cylinder":
            radius = section["r"]
            end = section.get("r2", radius)
            count = section.get("facets", facets)
            lines.append(f'        cylinder(h={section["h"]}, r1={radius}, r2={end}, $fn={count});')
        elif section["shape"] == "polygon":
            points = json.dumps(section["points"])
            lines.append(f'        linear_extrude(height={section["h"]}) polygon(points={points});')
        else:
            raise ValueError(f"Unknown model primitive {section['shape']}")
    return "\n".join([*lines, "}", ""])


def main(**kwargs):
    generate_stl = kwargs.get("generate_stl", kwargs.get("typ", "all") == "all")
    for folder, part in records(**kwargs):
        options = part["oobb_details"]
        if not options["run_scad"]:
            continue
        directory = folder / "three_d_model"
        source = scad_source(title=part["title"], model_note=part["model_note"], **options)
        write_file(directory / "working.scad", source)
        if generate_stl:
            mesh = build_mesh(**options)
            write_file(directory / "working.stl", mesh.export(file_type="stl"))
            # glTF uses metres with Y up. Both manufacturing formats use mm with Z up.
            transform = np.array([
                [.001, 0, 0, 0],
                [0, 0, .001, 0],
                [0, -.001, 0, 0],
                [0, 0, 0, 1],
            ])
            mesh.apply_transform(transform)
            write_file(directory / "working.glb", mesh.export(file_type="glb"))

