"""Editable landmarks in the four individual workshop photographs.

Coordinates are (image column, image row), on a 1:8 view of each original. Sleeve stations use
(column, row, apparent width in pixels). Z dimensions are independent in mm.
"""
from math import cos, dist, hypot, pi, sin

import manifold3d as manifold
import numpy as np

from working_tool_geometry import cylinder, outline


MATERIALS = {
    "red vinyl": ([175, 27, 40], 0.0, 0.34),
    "blue vinyl": ([26, 55, 156], 0.0, 0.34),
    "bright steel": ([183, 184, 180], 0.78, 0.33),
    "ground steel": ([150, 151, 147], 0.80, 0.43),
    "black oxide": ([55, 55, 58], 0.67, 0.42),
    "brass": ([197, 161, 96], 0.68, 0.36),
    "charcoal": ([47, 46, 50], 0.0, 0.47),
    "dark inset": ([27, 26, 31], 0.0, 0.55),
    "yellow": ([249, 191, 12], 0.0, 0.33),
}


def calibration(**kwargs):
    landmarks = kwargs["scale_path_px"]
    axis = kwargs["axis_px"]
    overall = kwargs["reference_length_mm"]
    origin = landmarks[0]
    scale = overall / sum(dist(a, b) for a, b in zip(landmarks, landmarks[1:]))
    dx, dy = (value / hypot(*axis) for value in axis)

    def convert(point):
        u = point[0] - origin[0]
        v = point[1] - origin[1]
        return [round((v * dx - u * dy) * scale, 4), round((u * dx + v * dy) * scale, 4)]

    return convert, scale


def sheet(**kwargs):
    convert = kwargs["convert"]
    points = kwargs["points"]
    holes = kwargs.get("holes", [])
    bottom = kwargs.get("bottom_mm", 0)
    depth = kwargs.get("depth_mm", 3)
    section = outline([convert(p) for p in points], bottom_mm=bottom, depth_mm=depth)
    if "bevel_mm" in kwargs:
        section["bevel_mm"] = kwargs["bevel_mm"]
    if holes:
        section["holes"] = [[convert(p) for p in loop] for loop in holes]
    return section


def bevel_panel(**kwargs):
    points = np.asarray(kwargs["points"], dtype=float)
    radius = kwargs["bevel_mm"]
    height = kwargs["h"]
    following = np.roll(points, -1, axis=0)
    if sum(points[:, 0] * following[:, 1] - points[:, 1] * following[:, 0]) < 0:
        points = points[::-1]
    edges = np.roll(points, -1, axis=0) - points
    normals = np.column_stack((-edges[:, 1], edges[:, 0])) / np.linalg.norm(edges, axis=1)[:, None]
    previous = np.roll(normals, 1, axis=0)
    inset = (previous + normals) / (1 + (previous * normals).sum(axis=1))[:, None]
    levels = [(radius, 0), (0.3*radius, 0.3*radius), (0, radius),
              (0, height-radius), (0.3*radius, height-0.3*radius), (radius, height)]
    count = len(points)
    vertices, faces = [], []
    for index, (offset, z) in enumerate(levels):
        ring = points + inset * offset
        vertices.extend([[round(x, 5), round(y, 5), z] for x, y in ring])
        if index == 0:
            faces.extend(manifold.triangulate([ring])[:, ::-1].tolist())
        else:
            for i in range(count):
                a = (index-1)*count + i
                b = (index-1)*count + (i+1) % count
                faces.extend([[a, b, b+count], [a, b+count, a+count]])
        if index == len(levels)-1:
            faces.extend((manifold.triangulate([ring]) + index*count).tolist())
    return {
        **kwargs,
        "shape": "polyhedron",
        "vertices": vertices,
        "faces": faces,
    }


def pin(**kwargs):
    convert = kwargs["convert"]
    centre = kwargs["centre"]
    diameter = kwargs.get("diameter_mm", 4)
    depth = kwargs.get("depth_mm", 1)
    bottom = kwargs.get("bottom_mm", 4)
    return cylinder(
        diameter_mm=diameter,
        length_mm=depth,
        pos=[*convert(centre), bottom],
        rot=[0, 0, 0],
    )


def sleeve(**kwargs):
    convert = kwargs["convert"]
    scale = kwargs["scale"]
    stations = kwargs["stations"]
    thickness = kwargs.get("thickness_mm", 10)
    centre_z = kwargs.get("centre_z_mm", thickness / 2)
    facets = kwargs.get("facets", 24)
    centres = [convert(p[:2]) for p in stations]
    return {
        "shape": "sleeve",
        "stations_mm": [[*centre, round(station[2] * scale, 4)] for centre, station in zip(centres, stations)],
        "thickness_mm": thickness,
        "centre_z_mm": centre_z,
        "facets": facets,
        "pos": [0, 0, 0],
        "rot": [0, 0, 0],
    }


def expand_sleeve(**kwargs):
    stations = kwargs["stations_mm"]
    centres = [p[:2] for p in stations]
    thickness = kwargs["thickness_mm"]
    centre_z = kwargs["centre_z_mm"]
    facets = kwargs.get("facets", 24)
    rings = []
    for index, ((x, y), station) in enumerate(zip(centres, stations)):
        before = centres[max(0, index - 1)]
        after = centres[min(len(centres) - 1, index + 1)]
        dx, dy = (b - a for a, b in zip(before, after))
        length = hypot(dx, dy)
        radius = station[2] / 2
        half_height = min(thickness / 2, radius * 1.1)
        for step in range(facets):
            angle = 2 * pi * step / facets
            width = radius * cos(angle)
            rings.append([
                round(x - dy / length * width, 4),
                round(y + dx / length * width, 4),
                round(centre_z + half_height * sin(angle), 4),
            ])
    faces = []
    for index in range(len(stations) - 1):
        for step in range(facets):
            a = index * facets + step
            b = index * facets + (step + 1) % facets
            faces.extend([[a, b, b + facets], [a, b + facets, a + facets]])
    for step in range(1, facets - 1):
        last = len(rings) - facets
        faces.extend([[0, step + 1, step], [last, last + step, last + step + 1]])
    return {
        **kwargs,
        "shape": "polyhedron",
        "vertices": rings,
        "faces": faces,
        "pos": [0, 0, 0],
        "rot": [0, 0, 0],
    }


def stroke(**kwargs):
    convert = kwargs["convert"]
    paths = kwargs.get("paths") or [kwargs["path"]]
    radius = kwargs.get("width_mm", 0.9) / 2
    depth = kwargs.get("depth_mm", 1)
    bottom = kwargs.get("bottom_mm", 4)
    tracks = [[convert(point) for point in path] for path in paths]
    return {
        "shape": "stroke",
        "paths_mm": tracks,
        "width_mm": radius * 2,
        "depth_mm": depth,
        "bottom_mm": bottom,
        "pos": [0, 0, 0],
        "rot": [0, 0, 0],
    }


def expand_stroke(**kwargs):
    tracks = kwargs["paths_mm"]
    radius = kwargs["width_mm"] / 2
    depth = kwargs["depth_mm"]
    bottom = kwargs["bottom_mm"]
    # Adjacent round-ended segments overlap even at the spring's tight bends.
    profile = manifold.CrossSection.circle(radius, 16)
    spans = []
    for centres in tracks:
        discs = [profile.translate(point) for point in centres]
        spans.extend((a + b).hull() for a, b in zip(discs, discs[1:]))
    section = manifold.CrossSection.batch_boolean(spans, manifold.OpType.Add)
    contours = sorted(section.to_polygons(), key=lambda p: abs(sum(
        a[0]*b[1] - a[1]*b[0] for a, b in zip(p, [*p[1:], p[0]])
    )), reverse=True)
    loops = [points.round(5).tolist() for points in contours]
    result = outline(loops[0], bottom_mm=bottom, depth_mm=depth)
    if len(loops) > 1:
        result["holes"] = loops[1:]
    return {
        **kwargs,
        **result,
    }


def photo_segments(**kwargs):
    key = kwargs["recipe"]
    convert, scale = calibration(**kwargs)
    sections = []

    def add(builder, name, material, **options):
        section = builder(convert=convert, scale=scale, **options)
        section["name"] = name
        section["material"] = material
        sections.append(section)

    if key == "cutters":
        add(sheet, **{
            "name": "Left jaw and right tang",
            "material": "ground steel",
            "bottom_mm": 3,
            "depth_mm": 2.7,
            "points": [
                (280.9,256.8), (273,235), (274,222), (272,206),
                (278,191), (302,160), (315,168), (307,185),
                (300,204), (296,226), (286,230), (282,236),
            ],
        })
        add(sheet, **{
            "name": "Right jaw and left tang",
            "material": "bright steel",
            "bottom_mm": 5.4,
            "depth_mm": 2.6,
            "points": [
                (297.8,255.5), (292,232), (288,228), (279,228),
                (275,224), (269,202), (261,189), (253,183),
                (261,164), (273,173), (284,184), (293,198),
                (298,211), (302,231), (301,243),
            ],
        })
        add(pin, **{
            "name": "Pivot",
            "material": "ground steel",
            "centre": (287,215),
            "diameter_mm": 7,
            "bottom_mm": 7.8,
        })
        add(sheet, **{
            "name": "Wire guard plate",
            "material": "ground steel",
            "bottom_mm": 7.8,
            "depth_mm": 0.9,
            "points": [(261,188),(275,181),(284,196),(269,203)],
        })
        add(stroke, **{
            "name": "Folded wire guard",
            "material": "bright steel",
            "bottom_mm": 5.2,
            "width_mm": 0.8,
            "path": [(267,190),(280,214),(292,230),(307,251)],
        })
        loop = [(282.7 + 4*cos(t*pi/16),155.4 + 4*sin(t*pi/16)) for t in range(16,49)]
        add(stroke, **{
            "name": "Loop spring and legs",
            "material": "bright steel",
            "bottom_mm": 5.5,
            "width_mm": 0.75,
            "path": [
                (266,180), (278.5,155.4), *loop, (283,151.5),
                (286.5,153.8), (301.5,175),
            ],
        })
        add(sleeve, **{
            "name": "Left red grip",
            "material": "red vinyl",
            "thickness_mm": 10,
            "stations": [
                (253.5,187.5,2), (253.5,184,11), (252,175,25), (250,164,31),
                (242,152,30), (231,135,27), (221,114,26), (213,91,25),
                (207.5,66,24), (205,55,22), (204,50,15), (203.5,47.3,3),
            ],
        })
        add(sleeve, **{
            "name": "Right red grip",
            "material": "red vinyl",
            "thickness_mm": 10,
            "stations": [
                (319,181.7,2), (318,178,12), (317,170,26), (317.5,157,31),
                (324,140,30), (331,123,29), (338,102,28), (344,79,27),
                (349,51,26), (350,41,22), (351,36.5,13), (352,34.7,3),
            ],
        })
    elif key == "pliers":
        add(sheet, **{
            "name": "Right long jaw and left tang",
            "material": "ground steel",
            "bottom_mm": 2.3,
            "depth_mm": 3.9,
            "points": [
                (172.7,78), (175.8,79), (174,107), (171,139),
                (167,159), (165,164), (161,170), (142,181),
                (135,204), (122,207), (118,200), (126,186),
                (129,169), (136,156), (153,150), (159,147),
                (162,142), (162,137), (157,134),
            ],
        })
        add(sheet, **{
            "name": "Left long jaw and right tang",
            "material": "bright steel",
            "bottom_mm": 5.8,
            "depth_mm": 3.3,
            "points": [
                (115,81.4), (117.2,81.2), (135.8,134.4), (132.8,138),
                (132.4,142.3), (134.5,147), (139,150), (147,151.5),
                (156,154), (162,161), (163,167), (168,172),
                (171,187), (179,201), (163,205), (154,180),
                (148,181), (140,179), (134,175), (132,165),
                (128.5,164), (125,155), (121,128),
            ],
        })
        add(pin, **{
            "name": "Pivot face",
            "material": "ground steel",
            "centre": (147.7,166.8),
            "diameter_mm": 7.8,
            "bottom_mm": 8.9,
            "depth_mm": 0.6,
        })
        coil = [(135 + i * 0.4, 190.8 + 2.4*sin(i*pi/3.8)) for i in range(61)]
        add(stroke, **{
            "name": "Coil return spring",
            "material": "black oxide",
            "bottom_mm": 5.8,
            "width_mm": 0.85,
            "depth_mm": 1.6,
            "path": [(132,191),*coil,(162,191)],
        })
        add(sleeve, **{
            "name": "Left blue grip",
            "material": "blue vinyl",
            "thickness_mm": 9.5,
            "stations": [
                (125,201.5,17), (122,206.5,23), (106,225,22), (87,248,22),
                (73,267,21), (63.5,288,21), (58,310,20), (56,330,20),
                (56,341,20), (55,346,14), (54,349.5,3),
            ],
        })
        add(sleeve, **{
            "name": "Right blue grip",
            "material": "blue vinyl",
            "thickness_mm": 9.5,
            "stations": [
                (171,201,17), (174,205,23), (191,224,22), (210,245,22),
                (225,265,22), (236,287,21), (242,308,21), (244.5,329,21),
                (245,339,20), (246,345,14), (247,348,3),
            ],
        })
    elif key == "stripper":
        add(sheet, **{
            "name": "Slotted arm with pierced jaw",
            "material": "black oxide",
            "bottom_mm": 3,
            "depth_mm": 3,
            "points": [
                (258.4,252.6), (251,248), (246,241), (245,232),
                (246.5,226), (251,219), (314,132), (320,124),
                (350,139), (340,152), (313,190), (283,225),
                (272,230), (265,241), (259.5,242), (261,246),
            ],
            "holes": [
                [(287,188),(313,151),(317,148),(321,149),(323,152),(322,156),
                    (295,193),(291,195),(287,194),(285.8,191)], [(254,225),(255,222.8),(258,222),(260,224),(259.8,227),(257,228),(254.5,227)],
            ],
        })
        add(sheet, **{
            "name": "Straight arm and hooked jaw",
            "material": "black oxide",
            "bottom_mm": 5.7,
            "depth_mm": 2.7,
            "points": [
                (217,129), (243,115), (250,126), (297,229),
                (300,238), (300,246), (296,251), (286,256),
                (282,251), (282,248), (285,245), (279,243),
                (275,228), (263,223), (259,217),
            ],
        })
        add(pin, **{
            "name": "Pivot rim",
            "material": "ground steel",
            "centre": (275.8,212.6),
            "diameter_mm": 10.2,
            "bottom_mm": 8.2,
        })
        add(pin, **{
            "name": "Pivot centre",
            "material": "black oxide",
            "centre": (275.8,212.6),
            "diameter_mm": 8.3,
            "bottom_mm": 9.0,
        })
        add(pin, **{
            "name": "Adjuster head",
            "material": "black oxide",
            "centre": (305.8,172.2),
            "diameter_mm": 8,
            "bottom_mm": 5.6,
            "depth_mm": 2.3,
        })
        add(stroke, **{
            "name": "Adjuster screw slot",
            "material": "dark inset",
            "bottom_mm": 7.7,
            "width_mm": 0.7,
            "depth_mm": 0.3,
            "path": [(300,174.6),(311.5,169.6)],
        })
        add(pin, **{
            "name": "Straight arm screw",
            "material": "bright steel",
            "centre": (233,140),
            "diameter_mm": 5.7,
            "bottom_mm": 8.2,
        })
        add(pin, **{
            "name": "Slotted arm screw",
            "material": "bright steel",
            "centre": (330,148.5),
            "diameter_mm": 5.7,
            "bottom_mm": 5.8,
        })
        add(sleeve, **{
            "name": "Left red grip",
            "material": "red vinyl",
            "thickness_mm": 11,
            "stations": [
                (231.5,124.5,30), (227,116,32), (219,100,32), (210,78,31),
                (203,57,30), (200,39,30), (199,30.5,26), (198,25,18),
                (197.5,22.5,4),
            ],
        })
        add(sleeve, **{
            "name": "Right red grip",
            "material": "red vinyl",
            "thickness_mm": 11,
            "stations": [
                (334,134.5,31), (342,122,32), (353,107,32), (365,88,31),
                (374,69,31), (380,52,30), (382,45,25), (382.5,40.3,16),
                (382.5,38.7,3),
            ],
        })
    elif key == "knife":
        add(sheet, **{
            "name": "Closed charcoal housing",
            "material": "charcoal",
            "bottom_mm": 0.4,
            "depth_mm": 10.8,
            "bevel_mm": 1.6,
            "points": [
                (97.5,72), (99,68.5), (107,62), (112,60),
                (115,60.3), (128,67), (146.8,80.5), (159.4,291),
                (155,292), (104,266), (97.5,261.6), (100,234),
                (99,171),
            ],
        })
        add(sheet, **{
            "name": "Yellow rear housing",
            "material": "yellow",
            "bottom_mm": 0,
            "depth_mm": 11.6,
            "bevel_mm": 1.5,
            "points": [
                (97.5,260.5), (113,265), (117,267), (146,281),
                (159.5,291), (163.5,354), (163,367), (161,380),
                (157,392), (151,404.5), (147,408), (143,409.5),
                (138,409), (129,405), (116,397), (108,389),
                (102.5,381), (100.5,373),
            ],
        })
        add(sheet, **{
            "name": "Dark slider bed",
            "material": "dark inset",
            "bottom_mm": 11.05,
            "depth_mm": 0.95,
            "points": [
                (117,120), (118,116), (121.5,113.5), (126,114),
                (130.5,117.5), (136,218), (142.5,280), (147.5,342),
                (147,348), (144,353), (139,357), (130,359),
                (122,356), (117,350), (114.5,343), (113.7,261),
            ],
        })
        add(sheet, **{
            "name": "Grey face inset",
            "material": "ground steel",
            "bottom_mm": 11.85,
            "depth_mm": 0.3,
            "points": [(118,120),(122,117.8),(127.6,119),(135,263),(119,262)],
        })
        add(sheet, **{
            "name": "Moulded nameplate",
            "material": "dark inset",
            "bottom_mm": 11,
            "depth_mm": 0.32,
            "points": [(118.8,75),(126.6,74.6),(128.3,109.6),(120.5,110)],
        })
        # Simple relief lettering follows the legible moulded mark on this specimen.
        letters = {
            "S": [[(1,0),(0,0),(0,.5),(1,.5),(1,1),(0,1)]],
            "T": [[(0,0),(1,0)],[(.5,0),(.5,1)]],
            "A": [[(0,1),(.45,0),(.55,0),(1,1)],[(.22,.58),(.78,.58)]],
            "N": [[(0,1),(0,0),(1,1),(1,0)]],
            "L": [[(0,0),(0,1),(1,1)]],
            "E": [[(1,0),(0,0),(0,1),(1,1)],[(0,.48),(.83,.48)]],
            "Y": [[(0,0),(.5,.5),(1,0)],[(.5,.5),(.5,1)]],
        }
        for index, letter in enumerate("STANLEY"):
            tracks = [
                [(125.5 + index*.22 - v*4.5, 77 + index*4.45 + u*3) for u, v in line]
                for line in letters[letter]
            ]
            add(stroke, **{
                "name": f"Mark {letter}",
                "material": "charcoal",
                "bottom_mm": 11.28,
                "depth_mm": 0.21,
                "width_mm": 0.32,
                "paths": tracks,
            })
        for index in range(10):
            y = 160 + index * 10.5
            x = 116.4 + index * 0.47
            for side in (0,1):
                add(pin, **{
                    "name": f"Side scallop {index+1}-{side+1}",
                    "material": "dark inset",
                    "centre": (x+side*17,y+side*1.1),
                    "diameter_mm": 2.4,
                    "bottom_mm": 10.7,
                    "depth_mm": 0.64,
                })
        add(sheet, **{
            "name": "Yellow thumb slide",
            "material": "yellow",
            "bottom_mm": 11.8,
            "depth_mm": 2.5,
            "points": [
                (124,297), (125,293), (129,291), (133,292),
                (136,295), (139,354), (137.5,357.5), (130,358.4),
                (126,357), (125,350),
            ],
        })
        for index in range(6):
            y = 302 + index * 9.3
            x = 125 + index * 0.4
            add(stroke, **{
                "name": f"Thumb slide rib {index+1}",
                "material": "yellow",
                "bottom_mm": 14.0,
                "depth_mm": 1.0,
                "width_mm": 1.0,
                "path": [(x,y),(x+10.8,y-0.45)],
            })
        for index in range(3):
            y = 368 + index * 7
            add(stroke, **{
                "name": f"Rear cap rib {index+1}",
                "material": "yellow",
                "bottom_mm": 11.4,
                "depth_mm": 1.2,
                "width_mm": 1.3,
                "path": [(125,y),(142,y+6.5)],
            })
    else:
        raise ValueError(f"Unknown photograph recipe {key}")
    return sections
