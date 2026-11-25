"""Millimetre recipes for the external tool models. Rotations are XYZ degrees."""
from copy import deepcopy
from math import cos, pi, sin, sqrt


def cylinder(**kwargs):
    diameter = kwargs.get("diameter_mm", 10)
    end_diameter = kwargs.get("end_diameter_mm", diameter)
    length = kwargs.get("length_mm", 10)
    position = kwargs.get("pos", [0, 0, 0])
    rotation = kwargs.get("rot", [-90, 0, 0])
    facets = kwargs.get("facets", 64)
    return {
        "shape": "cylinder",
        "r": diameter / 2,
        "r2": end_diameter / 2,
        "h": length,
        "pos": position,
        "rot": rotation,
        "facets": facets,
    }


def stepped_body(**kwargs):
    diameters = kwargs["diameters_mm"]
    lengths = kwargs["lengths_mm"]
    end_diameters = kwargs.get("end_diameters_mm", diameters)
    sections = []
    start = 0
    for diameter, end_diameter, length in zip(diameters, end_diameters, lengths, strict=True):
        sections.append(cylinder(
            diameter_mm=diameter,
            end_diameter_mm=end_diameter,
            length_mm=length,
            pos=[0, start, 0],
        ))
        start += length
    return sections


def wera(**kwargs):
    shaft = kwargs.get("shaft_diameter_mm", 3)
    blade = kwargs.get("shaft_length_mm", 60)
    handle = kwargs.get("handle_length_mm", 97)
    grip = kwargs.get("handle_diameter_mm", 18)
    flats = kwargs.get("across_flats_mm", 2)
    tip_length = kwargs.get("tip_length_mm", 5)
    # Fractions of the 97 mm handle allow the grip profile to be edited independently.
    options = {
        "diameters_mm": [2 * flats / sqrt(3), shaft, 9, grip, 12, 12, grip],
        "end_diameters_mm": [2 * flats / sqrt(3), shaft, grip, 12, 12, grip, grip],
        "lengths_mm": [tip_length, blade - tip_length, handle * .16, handle * .25,
                       handle * .39, handle * .12, handle * .08],
    }
    sections = stepped_body(**options)
    sections[0]["facets"] = 6
    return sections


def hex_key(**kwargs):
    flats = kwargs.get("across_flats_mm", 2)
    long_arm = kwargs.get("long_arm_mm", 51)
    short_arm = kwargs.get("short_arm_mm", 18)
    radius = flats / sqrt(3)
    elbow = long_arm - flats / 2
    return [
        cylinder(
            diameter_mm=2 * radius,
            length_mm=elbow,
            facets=6,
        ),
        cylinder(
            diameter_mm=2 * radius,
            length_mm=short_arm - radius,
            pos=[0, elbow, 0],
            rot=[0, 90, 0],
            facets=6,
        ),
    ]


def outline(points, **kwargs):
    depth = kwargs.get("depth_mm", 3)
    bottom = kwargs.get("bottom_mm", 0)
    return {
        "shape": "polygon",
        "points": points,
        "h": depth,
        "pos": [0, 0, bottom],
        "rot": [0, 0, 0],
    }


def caliper(**kwargs):
    length = kwargs.get("overall_length_mm", 233)
    width = kwargs.get("beam_width_mm", 16)
    jaw = kwargs.get("outside_jaw_mm", 40)
    half = width / 2
    return [
        outline([[-half, 0], [half, 0], [half, length], [-half, length]], depth_mm=3),
        outline([[-half-jaw, 0], [half, 0], [half+16.5, 13], [half, 8],
                 [-half, 8], [-half-jaw, 3]], depth_mm=3),
        outline([[-half-jaw, 3], [-half, 6], [half, 6], [half+16.5, 13],
                 [half, 16], [-half, 16], [-half-jaw+6, 8]], depth_mm=3),
        outline([[-16, 12], [16, 12], [16, 65], [-16, 65]], depth_mm=13),
        outline([[-10, 19], [10, 19], [10, 53], [-10, 53]], bottom_mm=13, depth_mm=1),
    ]


def combination_spanner(**kwargs):
    """Ring end at Y=0, open jaw at +Y. All three pieces share the midplane."""
    flats = kwargs["across_flats_mm"]
    length = kwargs["length_mm"]
    ring_width = kwargs["ring_width_mm"]
    jaw_width = kwargs["jaw_width_mm"]
    ring_depth = kwargs["ring_thickness_mm"]
    jaw_depth = kwargs["jaw_thickness_mm"]
    shank_width = kwargs.get("shank_width_mm", flats * 0.85)
    ring_radius = ring_width / 2
    hole_radius = flats / sqrt(3)
    jaw = jaw_width / 2
    half = shank_width / 2
    # The polygon hole has a true across-flats opening. The ring is seated first.
    ring = {
        "name": "Ring end",
        "material": "bright steel",
        "shape": "polygon",
        "points": [
            [ring_radius * cos(i*pi/32), ring_radius * (1 + sin(i*pi/32))]
            for i in range(64)
        ],
        "holes": [[
            [hole_radius * cos(-i*pi/3), ring_radius + hole_radius * sin(-i*pi/3)]
            for i in range(6)
        ]],
        "h": ring_depth,
        "pos": [0, 0, -ring_depth / 2],
        "rot": [0, 0, 0],
    }
    shank_depth = jaw_depth * 0.8
    shank = {
        "name": "Shank",
        "material": "ground steel",
        "shape": "polygon",
        "points": [
            [-half, ring_width * 0.91], [half, ring_width * 0.91],
            [half * 0.88, length * 0.53], [half, length - jaw * 1.7],
            [-half, length - jaw * 1.7], [-half * 0.88, length * 0.53],
        ],
        "h": shank_depth,
        "pos": [0, 0, -shank_depth / 2],
        "rot": [0, 0, 0],
    }
    open_end = {
        "name": "Open jaw",
        "material": "bright steel",
        "shape": "polygon",
        "points": [
            [-half, -jaw * 1.85], [half, -jaw * 1.85],
            [jaw * 0.84, -jaw * 1.47], [jaw, -jaw * 0.95],
            [jaw * 0.94, -jaw * 0.38], [flats / 2, 0],
            [flats / 2, -jaw * 0.86], [0, -jaw * 1.12],
            [-flats / 2, -jaw * 0.86], [-flats / 2, 0],
            [-jaw * 0.94, -jaw * 0.38], [-jaw, -jaw * 0.95],
            [-jaw * 0.84, -jaw * 1.47],
        ],
        "h": jaw_depth,
        "pos": [0, length, -jaw_depth / 2],
        "rot": [0, 0, 0],
    }
    return [ring, shank, open_end]


def double_ended_bit(**kwargs):
    length = kwargs.get("length_mm", 60)
    flats = kwargs.get("across_flats_mm", 6.35)
    tip_length = kwargs.get("tip_length_mm", 8)
    tip_diameter = kwargs.get("tip_diameter_mm", 3.2)
    diameter = 2 * flats / sqrt(3)
    sections = [
        {
            "name": "Lower tip",
            "material": "ground steel",
            "diameter_mm": tip_diameter,
            "end_diameter_mm": diameter,
            "length_mm": tip_length,
            "pos": [0, 0, 0],
        },
        {
            "name": "Hexagonal shank",
            "material": "bright steel",
            "diameter_mm": diameter,
            "length_mm": length - 2 * tip_length,
            "pos": [0, tip_length, 0],
        },
        {
            "name": "Upper tip",
            "material": "ground steel",
            "diameter_mm": diameter,
            "end_diameter_mm": tip_diameter,
            "length_mm": tip_length,
            "pos": [0, length - tip_length, 0],
        },
    ]
    result = []
    for section in sections:
        name = section.pop("name")
        material = section.pop("material")
        geometry = cylinder(facets=6, **section)
        geometry["name"] = name
        geometry["material"] = material
        result.append(geometry)
    return result


def long_driver_bit(**kwargs):
    length = kwargs.get("length_mm", 89)
    flats = kwargs.get("across_flats_mm", 6.35)
    tip_length = kwargs.get("tip_length_mm", 8)
    tip_diameter = kwargs.get("tip_diameter_mm", 3.2)
    diameter = 2 * flats / sqrt(3)
    sections = [
        {
            "name": "Hexagonal shank",
            "material": "bright steel",
            "diameter_mm": diameter,
            "length_mm": length - tip_length,
            "pos": [0, 0, 0],
        },
        {
            "name": "Phillips tip",
            "material": "ground steel",
            "diameter_mm": diameter,
            "end_diameter_mm": tip_diameter,
            "length_mm": tip_length,
            "pos": [0, length - tip_length, 0],
        },
    ]
    result = []
    for section in sections:
        name = section.pop("name")
        material = section.pop("material")
        geometry = cylinder(facets=6, **section)
        geometry["name"] = name
        geometry["material"] = material
        result.append(geometry)
    return result


def coloured_disc(**kwargs):
    diameter = kwargs.get("diameter_mm", 67)
    depth = kwargs.get("depth_mm", 24)
    kind = kwargs.get("kind", "olfa_can")
    label_depth = kwargs.get("label_depth_mm", 0.4)
    base_options = {
        "diameter_mm": diameter,
        "length_mm": depth - label_depth if kind == "olfa_can" else depth,
        "rot": [0, 0, 0],
    }
    body = cylinder(**base_options)
    body["name"] = "Body"
    body["material"] = "yellow" if kind == "olfa_can" else "charcoal"
    if kind != "olfa_can":
        return [body]
    label_options = {
        "diameter_mm": diameter - 3,
        "length_mm": label_depth,
        "pos": [0, 0, depth - label_depth],
        "rot": [0, 0, 0],
    }
    face = cylinder(**label_options)
    face["name"] = "Red face"
    face["material"] = "red vinyl"
    return [body, face]


def tape_measure(**kwargs):
    width = kwargs.get("width_mm", 69)
    height = kwargs.get("height_mm", 72)
    depth = kwargs.get("depth_mm", 40)
    corner = kwargs.get("corner_mm", 12)
    face_depth = kwargs.get("face_depth_mm", 0.6)
    half = width / 2
    body = {
        "name": "Yellow case",
        "material": "yellow",
        "shape": "polygon",
        "points": [
            [-half + corner, 0], [half - corner, 0],
            [half, corner], [half, height - corner],
            [half - corner, height], [-half + corner, height],
            [-half, height - corner], [-half, corner],
        ],
        "h": depth - face_depth,
        "pos": [0, 0, 0],
        "rot": [0, 0, 0],
    }
    panel = {
        "name": "Dark front panel",
        "material": "charcoal",
        "shape": "polygon",
        "points": [
            [-half + 9, 10], [half - 9, 10],
            [half - 5, 17], [half - 5, height - 16],
            [half - 15, height - 7], [-half + 15, height - 7],
            [-half + 5, height - 16], [-half + 5, 17],
        ],
        "h": face_depth,
        "pos": [0, 0, depth - face_depth],
        "rot": [0, 0, 0],
    }
    return [body, panel]


def open_spanner(**kwargs):
    flats = kwargs.get("across_flats_mm", 7)
    length = kwargs.get("length_mm", 80)
    width = kwargs.get("head_width_mm", 15)
    thickness = kwargs.get("thickness_mm", 2.7)
    shank_width = kwargs.get("shank_width_mm", 6)
    half = width / 2
    shank = shank_width / 2
    opening = flats / 2
    neck = width * 1.25
    # Both jaws are shown square to the body as an editable simplified outline.
    points = [
        [-half, 0], [-opening, 0], [-opening, half],
        [opening, half], [opening, 0], [half, 0],
        [half, width * 0.55], [shank, neck],
        [shank, length - neck], [half, length - width * 0.55],
        [half, length], [opening, length], [opening, length - half],
        [-opening, length - half], [-opening, length], [-half, length],
        [-half, length - width * 0.55], [-shank, length - neck],
        [-shank, neck], [-half, width * 0.55],
    ]
    return [{
        "name": "Open spanner",
        "material": "bright steel",
        "shape": "polygon",
        "points": points,
        "h": thickness,
        "pos": [0, 0, -thickness / 2],
        "rot": [0, 0, 0],
    }]


def pritt_stick(**kwargs):
    diameter = kwargs.get("diameter_mm", 26)
    length = kwargs.get("length_mm", 95)
    base_length = kwargs.get("base_length_mm", 6)
    cap_length = kwargs.get("cap_length_mm", 28)
    sections = [
        {
            "name": "Twist base",
            "material": "charcoal",
            "diameter_mm": diameter * 0.94,
            "length_mm": base_length,
            "pos": [0, 0, 0],
        },
        {
            "name": "Glue stick body",
            "material": "red vinyl",
            "diameter_mm": diameter * 0.96,
            "length_mm": length - base_length - cap_length,
            "pos": [0, base_length, 0],
        },
        {
            "name": "Closed cap",
            "material": "red vinyl",
            "diameter_mm": diameter,
            "length_mm": cap_length,
            "pos": [0, length - cap_length, 0],
        },
    ]
    result = []
    for section in sections:
        name = section.pop("name")
        material = section.pop("material")
        geometry = cylinder(**section)
        geometry["name"] = name
        geometry["material"] = material
        result.append(geometry)
    return result


def model_segments(**kwargs):
    kind = kwargs.get("model_kind", "holder_envelope")
    parameters = kwargs.get("parameters", {})
    profile = kwargs.get("holder_profile", [])
    if kind == "photo_reference":
        from working_photo_tools import photo_segments
        return photo_segments(**parameters)
    if kind == "holder_envelope":
        return deepcopy(profile)
    if kind in ("olfa_can", "timer_disc"):
        return coloured_disc(kind=kind, **parameters)
    if kind == "disc":
        return [cylinder(
            diameter_mm=parameters["diameter_mm"],
            length_mm=parameters["depth_mm"],
            rot=[0, 0, 0],
        )]
    if kind == "marker":
        diameter = parameters["diameter_mm"]
        length = parameters["length_mm"]
        return stepped_body(
            diameters_mm=[diameter * .78, diameter * .86, diameter, diameter],
            end_diameters_mm=[diameter * .86, diameter * .86, diameter, diameter * .92],
            lengths_mm=[length * .04, length * .68, length * .24, length * .04],
        )
    builders = {
        "pritt_stick": pritt_stick,
        "open_spanner": open_spanner,
        "tape_measure": tape_measure,
        "double_ended_bit": double_ended_bit,
        "long_driver_bit": long_driver_bit,
        "combination_spanner": combination_spanner,
        "caliper": caliper,
        "hex_key": hex_key,
        "stepped_body": stepped_body,
        "wera": wera,
    }
    return builders[kind](**parameters)

