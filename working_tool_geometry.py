"""Millimetre recipes for the external tool models. Rotations are XYZ degrees."""
from copy import deepcopy
from math import sqrt


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


def model_segments(**kwargs):
    kind = kwargs.get("model_kind", "holder_envelope")
    parameters = kwargs.get("parameters", {})
    profile = kwargs.get("holder_profile", [])
    if kind == "photo_reference":
        from working_photo_tools import photo_segments
        return photo_segments(**parameters)
    if kind == "holder_envelope":
        return deepcopy(profile)
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
        "caliper": caliper,
        "hex_key": hex_key,
        "stepped_body": stepped_body,
        "wera": wera,
    }
    return builders[kind](**parameters)

