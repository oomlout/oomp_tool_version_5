"""Build the editable OpenSCAD source and its catalogue exchange meshes."""
import json

import manifold3d as manifold
import numpy as np
import trimesh

from tool_catalogue import records, write_file
from working_photo_tools import MATERIALS, bevel_panel, expand_sleeve, expand_stroke


def expanded_sections(segments):
    for section in segments:
        if section["shape"] == "sleeve":
            yield expand_sleeve(**section)
        elif section["shape"] == "stroke":
            yield expand_stroke(**section)
        elif "bevel_mm" in section:
            yield bevel_panel(**section)
        else:
            yield section


def solids(**kwargs):
    segments = kwargs["segments"]
    facets = kwargs.get("facets", 64)
    result = []
    for section in expanded_sections(segments):
        if section["shape"] == "cylinder":
            solid = manifold.Manifold.cylinder(
                section["h"], section["r"], section.get("r2", section["r"]),
                section.get("facets", facets),
            )
        elif section["shape"] == "polygon":
            contours = [section["points"], *section.get("holes", [])]
            polygon = manifold.CrossSection(contours, manifold.FillRule.EvenOdd)
            solid = polygon.extrude(section["h"])
        elif section["shape"] == "polyhedron":
            geometry = manifold.Mesh(
                vert_properties=np.asarray(section["vertices"], dtype=np.float32),
                tri_verts=np.asarray(section["faces"], dtype=np.uint32),
            )
            solid = manifold.Manifold(geometry)
            if solid.status() != manifold.Error.NoError:
                raise ValueError(f"Invalid polyhedron: {section['name']}")
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
    for section in expanded_sections(segments):
        position = json.dumps(section["pos"])
        rotation = json.dumps(section["rot"])
        if "material" in section:
            rgb, _, _ = MATERIALS[section["material"]]
            lines.append(f'    // {section["name"]}')
            lines.append(f'    color({[round(channel / 255, 4) for channel in rgb]})')
        lines.append(f"    translate({position}) rotate({rotation})")
        if section["shape"] == "cylinder":
            radius = section["r"]
            end = section.get("r2", radius)
            count = section.get("facets", facets)
            lines.append(f'        cylinder(h={section["h"]}, r1={radius}, r2={end}, $fn={count});')
        elif section["shape"] == "polygon":
            points = list(section["points"])
            paths = [list(range(len(points)))]
            for hole in section.get("holes", []):
                paths.append(list(range(len(points), len(points) + len(hole))))
                points.extend(hole)
            paths_arg = f", paths={json.dumps(paths)}" if len(paths) > 1 else ""
            lines.append(f'        linear_extrude(height={section["h"]}) polygon(points={json.dumps(points)}{paths_arg});')
        elif section["shape"] == "polyhedron":
            # OpenSCAD uses clockwise faces as seen from outside.
            faces = [triangle[::-1] for triangle in section["faces"]]
            lines.append(f'        polyhedron(points={json.dumps(section["vertices"])}, faces={json.dumps(faces)}, convexity=10);')
        else:
            raise ValueError(f"Unknown model primitive {section['shape']}")
    return "\n".join([*lines, "}", ""])


def coloured_scene(**kwargs):
    segments = kwargs["segments"]
    transform = kwargs["transform"]
    scene = trimesh.Scene()
    for section, piece in zip(segments, solids(**kwargs), strict=True):
        geometry = piece.to_mesh()
        mesh = trimesh.Trimesh(vertices=geometry.vert_properties[:, :3], faces=geometry.tri_verts)
        material = section["material"]
        rgb, metallic, roughness = MATERIALS[material]
        # The swatches are sRGB. glTF base-colour factors are linear.
        swatch = np.asarray(rgb, dtype=float) / 255
        linear = np.where(swatch <= 0.04045, swatch / 12.92, ((swatch + .055) / 1.055) ** 2.4)
        mesh.visual = trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(
            name=material,
            baseColorFactor=[*np.rint(linear * 255).astype(int), 255],
            metallicFactor=metallic,
            roughnessFactor=roughness,
        ))
        mesh.apply_transform(transform)
        scene.add_geometry(mesh, node_name=section["name"], geom_name=section["name"])
    return scene


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
            if part["model_kind"] == "photo_reference":
                exchange = coloured_scene(transform=transform, **options)
            else:
                mesh.apply_transform(transform)
                exchange = mesh
            write_file(directory / "working.glb", exchange.export(file_type="glb"))

