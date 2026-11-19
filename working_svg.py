"""Draw orthographic views from the same millimetre recipe as the 3D files."""
from html import escape

import numpy as np

from tool_catalogue import cli_options, records, write_file
from tool_model import solids


def project(pieces, **kwargs):
    rotation = kwargs.get("rotation", [0, 0, -90])
    contours = []
    for piece in pieces:
        contours.append(piece.rotate(rotation).project().to_polygons())
    points = np.concatenate([ring for group in contours for ring in group])
    return contours, points.min(axis=0), points.max(axis=0)


def view_panel(view, **kwargs):
    label = kwargs.get("label", "Plan")
    box = kwargs.get("box", (28, 124, 610, 158))
    x, y, width, height = box
    contours, low, high = view
    extent = high - low
    centre = (low + high) / 2
    scale = kwargs.get("scale") or min((width-76) / extent[0], (height-86) / extent[1])
    origin = np.array([x+width/2, y+height/2])
    paths = [
        f'<text x="{x+14}" y="{y+23}" class="label">{label}</text>',
        f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="4" class="panel"/>',
    ]
    for rings in contours:
        outlines = []
        for contour in rings:
            display = (contour-centre) * [scale, -scale] + origin
            outlines.append(" ".join(f"{px:.3f},{py:.3f}" for px, py in display))
        if len(outlines) == 1:
            paths.append(f'<polygon points="{outlines[0]}" class="object"/>')
        elif outlines:
            path = " ".join(f"M {outline} Z" for outline in outlines)
            paths.append(f'<path d="{path}" fill-rule="evenodd" class="object"/>')
    left = origin[0] - extent[0] * scale / 2
    right = origin[0] + extent[0] * scale / 2
    baseline = y + height - 16
    paths.extend([
        f'<path d="M{left:g} {baseline-4}v8 m0 -4 H{right:g} m0 -4 v8" class="dim"/>',
        f'<text x="{origin[0]:g}" y="{baseline-5}" class="measure">{extent[0]:g} mm</text>',
    ])
    return "\n".join(paths)


def drawing(**kwargs):
    part = kwargs["part"]
    segments = kwargs.get("segments", part["oobb_details"]["segments"])
    kind = kwargs.get("label", "External tool reference")
    pieces = solids(segments=segments)
    plan = project(pieces, rotation=[0, 0, -90])  # Y across the page, X vertical.
    side = project([p.rotate([0, 0, -90]) for p in pieces], rotation=[90, 0, 0])
    end = project(pieces, rotation=[90, 0, 0])
    plan_width, plan_height = plan[2] - plan[1]
    side_height = side[2][1] - side[1][1]
    scale = min(524 / plan_width, 112 / plan_height, 90 / side_height)
    plan_panel = view_panel(plan, label="Plan  ·  Y × X", box=(26, 98, 610, 190), scale=scale)
    side_panel = view_panel(side, label="Side  ·  Y × Z", box=(26, 300, 610, 170), scale=scale)
    end_panel = view_panel(end, label="End  ·  X × Z", box=(648, 98, 286, 190))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="960" height="494" viewBox="0 0 960 494" role="img">
<title>{escape(part["title"])} — {kind}</title>
<desc>Orthographic drawing in millimetres. Plan and side share a scale. The end view is enlarged independently.</desc>
<style>
text {{font-family:Arial,sans-serif;fill:#173735}}
.title {{font-size:25px;font-weight:600}}
.label {{font-size:14px;font-weight:600}}
.detail {{font-size:17px}}
.panel {{stroke:#ccdad6;fill:none}}
.object {{stroke:#164f50;stroke-width:1.35;fill:#a7d4c8;fill-opacity:.84;stroke-linejoin:round}}
.dim {{fill:none;stroke:#587674;stroke-width:1}}
.measure {{font-size:12px;text-anchor:middle;paint-order:stroke;stroke:white;stroke-width:4}}
</style>
<rect width="960" height="494" fill="white"/>
<text x="26" y="39" class="title">{escape(part["title"])}</text>
<text x="27" y="69" class="detail">{kind} · millimetres</text>
{plan_panel}
{side_panel}
{end_panel}
<text x="664" y="337" class="label">Overall model dimensions</text>
<text x="664" y="373" class="detail">X   {plan_height:g} mm</text>
<text x="664" y="404" class="detail">Y   {plan_width:g} mm</text>
<text x="664" y="435" class="detail">Z   {side_height:g} mm</text>
</svg>
'''


def main(**kwargs):
    for folder, part in records(**kwargs):
        if part["model_kind"] == "holder_envelope":
            write_file(folder / "working.svg", drawing(part=part, label="Holder clearance profile"))
        else:
            write_file(folder / "working.svg", drawing(part=part))
            pocket = drawing(part=part, segments=part["holder_profile"], label="Holder clearance profile")
            write_file(folder / "holder_profile.svg", pocket)
            if part["model_kind"] == "photo_reference":
                from working_photo_measurements import publish
                publish(folder=folder, part=part)


if __name__ == "__main__":
    main(**cli_options())

