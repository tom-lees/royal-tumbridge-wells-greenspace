"""Turns building footprints + heights into cuboid meshes for the viewer."""

import trimesh
from shapely.geometry import Polygon


def extrude_buildings(footprints, tile_cx, tile_cy):
    """
    Extrudes each building footprint into a cuboid mesh using its 'height'
    and 'base_elev' columns. Footprints must be in EPSG:3857 (Mercator
    metres). Vertices are offset from a fixed tile centre (tile_cx, tile_cy)
    so tile meshes stay near the origin, then remapped to Three.js' Y-up
    axis convention.
    """
    meshes = []
    for idx, row in footprints.iterrows():
        try:
            geom = row.geometry
            if geom.geom_type == "MultiPolygon":
                geom = max(geom.geoms, key=lambda g: g.area)

            coords = [(c[0] - tile_cx, c[1] - tile_cy) for c in geom.exterior.coords]
            mesh = trimesh.creation.extrude_polygon(Polygon(coords), height=row["height"])
            mesh.apply_translation([0, 0, row.get("base_elev", 0.0) or 0.0])
            meshes.append(mesh)
        except Exception as e:
            print(f"    Failed on building {idx}: {e}")

    buildings = trimesh.util.concatenate(meshes)
    return _remap_to_threejs_up(buildings)


def _remap_to_threejs_up(mesh):
    """Swaps Y/Z so the mesh matches Three.js' Y-up axis convention."""
    original_vertices = mesh.vertices
    vertices = original_vertices.copy()
    vertices[:, 1] = original_vertices[:, 2].copy()
    vertices[:, 2] = -original_vertices[:, 1].copy()
    return trimesh.Trimesh(vertices=vertices, faces=mesh.faces)
