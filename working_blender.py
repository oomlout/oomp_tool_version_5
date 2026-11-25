"""Render the coloured SCAD-derived reference meshes with Blender in background mode."""
from pathlib import Path
import shutil
import subprocess
import sys


def main(**kwargs):
    from tool_catalogue import records
    blender = kwargs.get("blender", "blender")
    folders = [folder / "three_d_model" for folder, part in records(**kwargs)
               if part["model_kind"] in ("photo_reference", "combination_spanner", "double_ended_bit", "long_driver_bit", "olfa_can", "timer_disc", "tape_measure", "open_spanner", "pritt_stick")]
    if folders:
        binary = shutil.which(blender)
        if not binary:
            raise FileNotFoundError("Install Blender or pass its executable path as blender=...")
        subprocess.run([
            binary, "--background", "--factory-startup", "--python-exit-code", "1",
            "--python", str(Path(__file__).resolve()), "--", *map(str, folders),
        ], check=True)
        overview(parts_folder=folders[0].parent.parent)


def overview(**kwargs):
    from io import BytesIO
    from PIL import Image, ImageDraw, ImageFont
    from tool_catalogue import write_file

    parts_folder = kwargs["parts_folder"]
    titles = {
        "tool_side_cutters_110_mm_length_red": "Side cutters",
        "tool_pliers_needle_nose_130_mm_length_blue": "Needle-nose pliers",
        "tool_wire_strippers_120_mm_length_red": "Adjustable wire strippers",
        "tool_knife_craft_17_mm_black_exacto_style": "STANLEY craft knife",
    }
    images = [parts_folder / part / "three_d_model/render.png" for part in titles]
    if not all(path.is_file() for path in images):
        return
    sheet = Image.new("RGB", (1200, 834), "#f2f1ef")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default(size=20)
    for index, (title, path) in enumerate(zip(titles.values(), images)):
        x, y = index % 2 * 600, index // 2 * 417
        with Image.open(path) as source:
            panel = source.convert("RGB")
        panel.thumbnail((594, 376), Image.Resampling.LANCZOS)
        sheet.paste(panel, (x + (600-panel.width)//2, y))
        draw.text((x+24, y+379), title, font=font, fill="#25282b")
    output = BytesIO()
    sheet.save(output, format="JPEG", quality=91, optimize=True)
    write_file(parts_folder / "workshop_tools_render.jpg", output.getvalue())


def render_part(**kwargs):
    import bpy
    from mathutils import Vector

    folder = Path(kwargs["folder"])
    width = kwargs.get("width", 1080)
    height = kwargs.get("height", 720)
    samples = kwargs.get("samples", 20)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.view_settings.view_transform = "Khronos PBR Neutral"
    scene.view_settings.exposure = -0.85
    scene.world = bpy.data.worlds.new("Soft studio ambient")
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.79, 0.85, 0.94, 1)
    background.inputs["Strength"].default_value = 0.32

    bpy.ops.import_scene.gltf(filepath=str(folder / "working.glb"))
    objects = [o for o in scene.objects if o.type == "MESH"]
    vertices = [o.matrix_world @ v.co for o in objects for v in o.data.vertices]
    low = Vector([min(p[i] for p in vertices) for i in range(3)])
    high = Vector([max(p[i] for p in vertices) for i in range(3)])
    centre = (low + high) / 2
    for obj in objects:
        if "grip" in obj.name.lower():
            for face in obj.data.polygons:
                face.use_smooth = True
        else:
            bevel = obj.modifiers.new(name="Edge highlight", type="BEVEL")
            bevel.width = 0.00045
            bevel.segments = 3
            bevel.limit_method = "ANGLE"
            obj.modifiers.new(name="Face normals", type="WEIGHTED_NORMAL")

    bpy.ops.mesh.primitive_plane_add(size=4, location=(centre.x, centre.y, low.z - 0.00015))
    ground = bpy.context.object
    ground.name = "Studio floor"
    surface = bpy.data.materials.new("Warm grey paper")
    surface.diffuse_color = (0.57, 0.56, 0.53, 1)
    ground.data.materials.append(surface)

    def softbox(name, offset, energy, size, colour):
        position = centre + Vector(offset)
        bpy.ops.object.light_add(type="AREA", location=position)
        lamp = bpy.context.object
        lamp.name = name
        lamp.data.energy = energy
        lamp.data.shape = "DISK"
        lamp.data.size = size
        lamp.data.color = colour
        lamp.rotation_euler = (centre - position).to_track_quat("-Z", "Y").to_euler()

    softbox("Large key", (-0.12, -0.09, 0.20), 1.8, 0.15, (1.0, 0.96, 0.90))
    softbox("Grip highlight", (0.05, 0.17, 0.12), 1.0, 0.10, (0.91, 0.94, 1.0))
    softbox("Front fill", (0.20, -0.03, 0.12), 0.5, 0.12, (1.0, 1.0, 1.0))
    bpy.ops.object.camera_add()
    camera = bpy.context.object
    scene.camera = camera
    camera.data.type = "ORTHO"
    camera.data.clip_start = 0.001
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.length_unit = "MILLIMETERS"
    views = {
        "render_top": (1e-6, 0, 1),
        "render": (0.69, -0.28, 1),
    }
    for name, direction in views.items():
        axis = Vector(direction).normalized()
        rotation = (-axis).to_track_quat("-Z", "Y")
        screen_x = rotation @ Vector((1, 0, 0))
        screen_y = rotation @ Vector((0, 1, 0))
        xs = [(p-centre).dot(screen_x) for p in vertices]
        ys = [(p-centre).dot(screen_y) for p in vertices]
        camera.data.ortho_scale = 1.18 * max(max(xs)-min(xs), (max(ys)-min(ys)) * width/height)
        camera.location = (centre + axis * 0.34 + screen_x * (min(xs)+max(xs))/2
                           + screen_y * (min(ys)+max(ys))/2)
        camera.rotation_euler = rotation.to_euler()
        scene.render.filepath = str(folder / (name + ".png"))
        bpy.ops.render.render(write_still=True)
    # The saved scene opens on the three-quarter presentation camera.
    bpy.context.preferences.filepaths.save_version = 0
    scene.render.filepath = "//render.png"
    bpy.ops.wm.save_as_mainfile(filepath=str(folder / "working.blend"), compress=True)


if __name__ == "__main__":
    if "--" in sys.argv:
        for directory in sys.argv[sys.argv.index("--") + 1:]:
            render_part(folder=directory)
    else:
        from tool_catalogue import cli_options
        main(**cli_options())

