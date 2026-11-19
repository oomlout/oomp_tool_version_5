"""Publish a scale audit and photo overlay from the canonical part recipe."""
from html import escape
from math import dist, hypot
from pathlib import Path

import manifold3d as manifold
from PIL import Image

from tool_catalogue import ROOT, write_file
from tool_model import solids
from working_photo_tools import calibration


# Landmarks use the same one-eighth image coordinates as the editable traces.
FEATURES = {
    "cutters": [
        ("Jaw tip to pivot centre", (280.9,256.8), (287,215)),
        ("Distance between the two jaw tips", (280.9,256.8), (297.8,255.5)),
        ("Pivot head diameter", (278.8,215), (295.4,215)),
        ("Left grip width near its heel", (193.5,62), (217.2,59)),
    ],
    "pliers": [
        ("Right jaw tip to pivot centre", (174,78), (147.7,166.8)),
        ("Distance between the two jaw tips", (116.5,81.2), (174,78)),
        ("Pivot face diameter", (138.5,166.8), (156.7,166.8)),
        ("Lower left grip width", (46.2,325), (66.4,325)),
    ],
    "stripper": [
        ("Right jaw tip to pivot centre", (285,256), (275.8,212.6)),
        ("Distance between the two jaw tips", (258.4,252.6), (285,256)),
        ("Angled arm slot end-to-end", (287.2,194), (322.4,149.5)),
        ("Straight arm screw head diameter", (227.2,140), (238.8,140)),
    ],
    "knife": [
        ("Charcoal body width near the nose", (98,105), (148,103)),
        ("Yellow heel width at thumb slide", (100.3,340), (163,337.2)),
        ("Visible thumb slide length", (130,291), (133,358)),
    ],
}

CHECKS = {
    "cutters": "Measure the closed overall length and the thickness across a red grip. The photo shows the folded wire guard and the loop spring on different levels.",
    "pliers": "Measure the closed overall length, pivot stack thickness and grip thickness. The close-up shows a coil return spring below the pivot.",
    "stripper": "Measure this tool closed. The candidate Anvil listing gives 130 mm and the OOMP identity says 120 mm. Choosing 120 mm would multiply every photo-derived planar dimension by 120/130, a reduction of about 7.7%. The pale heads on the fresh photo are modelled as bright metal.",
    "knife": "STANLEY is legible on the fresh photo. The exact variant still needs a model code, closed length or refill marking. The candidate exterior is 165 × 30 × 15 mm. The slot, thumb slide and heel ribs are represented as fixed exterior details.",
}


def publish(**kwargs):
    folder = Path(kwargs["folder"])
    part = kwargs["part"]
    parameters = part["parameters"]
    photo = parameters["photo"]
    source = folder / photo
    if not source.is_file():
        # An isolated output root can import the original kept with the catalogue part.
        write_file(source, (ROOT / "parts" / part["oomp_id"] / photo).read_bytes())
    with Image.open(source) as image:
        width, height = image.size
    divisor = parameters["trace_divisor"]
    _, scale = calibration(**parameters)
    path = parameters["scale_path_px"]
    reference = parameters["reference_length_mm"]
    key = parameters["recipe"]
    pieces = solids(**part["oobb_details"])
    body = manifold.Manifold.batch_boolean(pieces, manifold.OpType.Add)
    low_x, low_y, low_z, high_x, high_y, high_z = body.bounding_box()
    outline = body.project().to_polygons()
    dx, dy = parameters["axis_px"]
    norm = hypot(dx, dy)
    dx, dy = dx/norm, dy/norm
    origin_x, origin_y = path[0]

    def photo_point(x, y):
        return (origin_x + (dx*y - dy*x)/scale, origin_y + (dy*y + dx*x)/scale)

    loops = [[photo_point(x, y) for x, y in ring] for ring in outline]
    svg_path = " ".join(
        "M " + " L ".join(f"{u:.3f},{v:.3f}" for u, v in ring) + " Z" for ring in loops
    )
    all_points = [p for ring in loops for p in ring]
    xmin = min(p[0] for p in all_points)-7
    ymin = min(p[1] for p in all_points)-7
    view_width = max(p[0] for p in all_points)+7-xmin
    view_height = max(p[1] for p in all_points)+7-ymin
    anchors = " ".join(f"{u},{v}" for u, v in path)
    circles = "".join(f'<circle cx="{u}" cy="{v}" r="1.3"/>' for u, v in path)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="{xmin:.2f} {ymin:.2f} {view_width:.2f} {view_height:.2f}">
<title>{escape(part["title"])} — silhouette registration</title>
<desc>White and cyan follow the projected CAD outline. The dashed yellow line joins the scale landmarks on the original photo.</desc>
<image xlink:href="{photo}" width="{width/divisor}" height="{height/divisor}"/>
<path d="{svg_path}" fill="none" stroke="#102925" stroke-width="1.45"/>
<path d="{svg_path}" fill="none" stroke="#59ffe2" stroke-width=".75"/>
<polyline points="{anchors}" fill="none" stroke="#ffed87" stroke-dasharray="3 2" stroke-width=".75"/>
<g fill="#ffed87" stroke="#383218" stroke-width=".4">{circles}</g></svg>
'''
    write_file(folder / "photo_overlay.svg", svg)
    pixels = sum(dist(a, b) for a, b in zip(path, path[1:])) * divisor
    lines = [
        f'# {part["title"]} — photo measurements', "",
        f'[Individual workshop photograph]({photo}) · [Photo with CAD outline](photo_overlay.svg) · [Identification and catalogue sources](research_2026-11-19.md)', "",
        f'The original is {width} × {height} pixels. The assumed reference length is {reference} mm. '
        f'The yellow scale path covers {pixels:.0f} original pixels, giving approximately {scale/divisor:.4f} mm per original pixel.', "",
        'The scale path runs from the nose to the heel.' if key == 'knife' else
        'The tool is open. The scale path adds jaw-tip-to-pivot and pivot-to-opposite-grip-end distances as an approximation to its closed overall length.',
        'The first coordinate in each pair is the image column. Multiply these one-eighth working coordinates by eight to locate them in the original.', "",
        'Scale landmarks in order: ' + ' → '.join(f'({u}, {v})' for u, v in path) + '.', "",
        '| Feature on the photograph | Working coordinates | Original pixels | Approximate mm |',
        '| --- | --- | ---: | ---: |',
    ]
    for feature, a, b in FEATURES[key]:
        length = dist(a, b)
        lines.append(f'| {feature} | {a} to {b} | {length*divisor:.0f} | {length*scale:.1f} |')
    lines.extend(["", "## Model envelope", "",
        f'The pictured pose occupies **{high_y-low_y:.1f} mm along the tool × {high_x-low_x:.1f} mm across × {high_z-low_z:.1f} mm thick** in the CAD frame. '
        'The first two values depend on the scale assumption and pose. The third is an assigned model depth. A single face view supplies no independent thickness measurement.', "",
        CHECKS[key], "", '[Modelling and repeat-capture notes](../PHOTO_MODELS.md)', ""])
    write_file(folder / "measurements.md", "\n".join(lines))

