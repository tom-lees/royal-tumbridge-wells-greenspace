"""Writes building meshes out to GLB files for the viewer."""

import os

import trimesh


def create_empty_glb(output_path):
    """Writes a near-invisible placeholder GLB for tiles with no buildings."""
    mesh = trimesh.creation.box(extents=[0.001, 0.001, 0.001])
    scene = trimesh.Scene()
    scene.add_geometry(mesh)
    with open(output_path, "wb") as f:
        f.write(scene.export(file_type="glb"))


def export_glb(buildings, output_path):
    """Writes a buildings mesh to GLB, with translucent white faces."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    buildings.visual.face_colors = [255, 255, 255, 191]
    scene = trimesh.Scene()
    scene.add_geometry(buildings, node_name="buildings")
    glb_data = scene.export(file_type="glb")
    with open(output_path, "wb") as f:
        f.write(glb_data)
    print(f"  Saved {output_path} ({len(glb_data) / 1024 / 1024:.2f} MB)")
