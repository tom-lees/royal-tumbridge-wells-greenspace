import os
import json
import numpy as np
import geopandas as gpd
import pandas as pd
from shapely.geometry import box
from pyproj import Transformer
import trimesh

from calc_ndsm import calc_ndsm
from sample_heights import sample_heights

TILE_SIZE = 5000


def create_empty_glb(output_path):
    mesh = trimesh.creation.box(extents=[0.001, 0.001, 0.001])
    scene = trimesh.Scene()
    scene.add_geometry(mesh)
    glb_data = scene.export(file_type="glb")
    with open(output_path, "wb") as f:
        f.write(glb_data)


def load_raster_index(path="data/raster_index.json"):
    with open(path) as f:
        return json.load(f)


def find_rasters_for_tile(tile_x, tile_y, raster_index):
    """
    Finds all rasters whose bounds intersect this tile.
    """
    tile_box = box(tile_x, tile_y, tile_x + TILE_SIZE, tile_y + TILE_SIZE)
    matches = []
    for name, raster in raster_index.items():
        b = raster["bounds_mercator"]
        raster_box = box(b["left"], b["bottom"], b["right"], b["top"])
        if tile_box.intersects(raster_box):
            matches.append((name, raster))
    return matches


def extrude_buildings_with_base(footprints, ndsm_data, tile_cx, tile_cy):
    """
    Extrudes buildings using pre-calculated height and base_elev columns.
    Footprints are in EPSG:3857 (Mercator metres).
    Vertices are offset from the fixed tile centre (tile_cx, tile_cy).
    """
    from shapely.geometry import Polygon

    meshes = []

    for idx, row in footprints.iterrows():
        try:
            height = row["height"]
            base_elev = row.get("base_elev", 0.0) or 0.0
            geom = row.geometry

            if geom.geom_type == "MultiPolygon":
                geom = max(geom.geoms, key=lambda g: g.area)

            # Offset from fixed tile centre
            coords = [(c[0] - tile_cx, c[1] - tile_cy) for c in geom.exterior.coords]
            poly = Polygon(coords)
            mesh = trimesh.creation.extrude_polygon(poly, height=height)
            mesh.apply_translation([0, 0, base_elev])
            meshes.append(mesh)

        except Exception as e:
            print(f"    Failed on building {idx}: {e}")
            continue

    buildings = trimesh.util.concatenate(meshes)

    # Remap Y/Z axes for Three.js (Y-up)
    vertices = buildings.vertices.copy()
    vertices[:, 1] = buildings.vertices[:, 2].copy()
    vertices[:, 2] = -buildings.vertices[:, 1].copy()
    buildings = trimesh.Trimesh(vertices=vertices, faces=buildings.faces)

    return buildings


def process_tile(tile_name, raster_index, output_dir="output/high", area_filter=100):
    """
    Processes a single tile — samples heights per building, extrudes, exports GLB.
    """
    gpkg_path = f"output/tiles/{tile_name}.gpkg"
    if not os.path.exists(gpkg_path):
        print(f"  No footprints found for {tile_name}")
        return 0

    footprints = gpd.read_file(gpkg_path, layer="buildings")
    print(f"  {len(footprints)} buildings loaded (CRS: {footprints.crs})")

    # Apply area filter for LOD
    footprints = footprints[footprints.geometry.area > area_filter]
    print(f"  {len(footprints)} buildings after area filter ({area_filter}m²)")

    # Tile bounds and fixed centre from tile name
    tile_x, tile_y = map(int, tile_name.split("_"))
    tile_cx = tile_x + TILE_SIZE / 2
    tile_cy = tile_y + TILE_SIZE / 2
    print(f"  Tile centre: ({tile_cx}, {tile_cy})")

    tile_bounds = {
        "left": tile_x,
        "bottom": tile_y,
        "right": tile_x + TILE_SIZE,
        "top": tile_y + TILE_SIZE,
    }

    # Find all rasters that intersect this tile
    rasters = find_rasters_for_tile(tile_x, tile_y, raster_index)
    print(f"  Found {len(rasters)} rasters: {[r[0] for r in rasters]}")

    # Convert footprints to WGS84 for height sampling
    footprints_wgs84 = footprints.to_crs(epsg=4326)

    # Store heights per building per raster
    heights_by_building = {idx: [] for idx in footprints.index}
    base_elevs_by_building = {idx: [] for idx in footprints.index}

    for raster_name, raster in rasters:
        print(f"\n  Processing raster {raster_name}...")

        ndsm_data = calc_ndsm(raster["dsm"], raster["dtm"])
        print(
            f"    nDSM range: {np.nanmin(ndsm_data['ndsm']):.2f}m - {np.nanmax(ndsm_data['ndsm']):.2f}m"
        )

        raster_box_wgs84 = box(
            raster["bounds_wgs84"]["left"],
            raster["bounds_wgs84"]["bottom"],
            raster["bounds_wgs84"]["right"],
            raster["bounds_wgs84"]["top"],
        )
        intersects = footprints_wgs84.geometry.intersects(raster_box_wgs84)
        subset = footprints_wgs84[intersects].copy()
        print(f"    {len(subset)} buildings intersect this raster")

        if len(subset) == 0:
            continue

        sampled = sample_heights(subset, ndsm_data)
        print(f"    {len(sampled)} buildings got height data")

        for idx, row in sampled.iterrows():
            if row["height"] is not None and not np.isnan(row["height"]):
                heights_by_building[idx].append(row["height"])

        to_bng = Transformer.from_crs("EPSG:4326", "EPSG:27700", always_xy=True)
        for idx, row in subset.iterrows():
            centroid = row.geometry.centroid  # WGS84
            bng_x, bng_y = to_bng.transform(centroid.x, centroid.y)  # convert to BNG
            col = int((bng_x - ndsm_data["transform"].c) / ndsm_data["transform"].a)
            row_idx = int((bng_y - ndsm_data["transform"].f) / ndsm_data["transform"].e)
            dtm_rows, dtm_cols = ndsm_data["dtm"].shape
            if 0 <= row_idx < dtm_rows and 0 <= col < dtm_cols:
                base_elev = float(ndsm_data["dtm"][row_idx, col])
                if not np.isnan(base_elev):
                    base_elevs_by_building[idx].append(base_elev)

    # Average heights across rasters
    final_heights = {}
    final_base_elevs = {}
    for idx in footprints.index:
        h = heights_by_building[idx]
        b = base_elevs_by_building[idx]
        if h:
            final_heights[idx] = np.mean(h)
            final_base_elevs[idx] = np.mean(b) if b else 0.0

    footprints["height"] = [final_heights.get(idx) for idx in footprints.index]
    footprints["base_elev"] = [
        final_base_elevs.get(idx, 0.0) for idx in footprints.index
    ]
    footprints = footprints[footprints["height"].notna()]

    stats_ok = len(footprints)
    stats_dropped = len(heights_by_building) - stats_ok
    print(f"\n  Buildings with heights: {stats_ok}")
    print(f"  Buildings dropped (no height): {stats_dropped}")
    print(
        f"  Height range: {footprints['height'].min():.2f}m - {footprints['height'].max():.2f}m"
    )

    if len(footprints) == 0:
        print(f"  No buildings — writing empty GLB")
        create_empty_glb(f"{output_dir}/{tile_name}.glb")
        return 0

    # Extrude using fixed tile centre
    print(f"  Extruding {len(footprints)} buildings...")
    buildings = extrude_buildings_with_base(footprints, None, tile_cx, tile_cy)

    # Export GLB
    os.makedirs(output_dir, exist_ok=True)
    glb_path = f"{output_dir}/{tile_name}.glb"
    scene = trimesh.Scene()
    buildings.visual.face_colors = [255, 255, 255, 191]
    scene.add_geometry(buildings, node_name="buildings")
    glb_data = scene.export(file_type="glb")
    with open(glb_path, "wb") as f:
        f.write(glb_data)
    print(f"  Saved {glb_path} ({len(glb_data) / 1024 / 1024:.2f} MB)")

    return stats_ok


def build_index(output_dir="output/high", index_path="output/index.json"):
    """
    Scans output/high for GLB files and builds index.json from filenames.
    """
    tiles = []
    for f in sorted(os.listdir(output_dir)):
        if not f.endswith(".glb"):
            continue
        tile_name = f.replace(".glb", "")
        x, y = map(int, tile_name.split("_"))
        tiles.append(
            {
                "tile": tile_name,
                "centre_x": x + TILE_SIZE / 2,
                "centre_y": y + TILE_SIZE / 2,
            }
        )

    with open(index_path, "w") as f:
        json.dump(tiles, f, indent=2)
    print(f"Built index.json with {len(tiles)} tiles")


if __name__ == "__main__":
    import time

    print("--- Loading raster index ---")
    raster_index = load_raster_index()
    print(f"Loaded {len(raster_index)} raster entries")

    os.makedirs("output/high", exist_ok=True)
    os.makedirs("output/mid", exist_ok=True)
    os.makedirs("output/low", exist_ok=True)

    # Central London — 4 columns x 5 rows = 20 tiles
    # tiles = [
    #     f"{x}_{y}"
    #     for x in [-35000, -30000, -25000, -20000, -15000, -10000, -5000, 0]
    #     for y in [6700000, 6705000, 6710000, 6715000, 6720000, 6725000, 6730000]
    # ]

    tiles = [
        f"{x}_{y}"
        for x in range(-115000, 45000, 5000)
        for y in range(6660000, 6770000, 5000)
    ]

    print(f"Total tiles to process: {len(tiles)}")

    for tile_name in tiles:
        for output_dir, area_filter in [
            ("output/high", 100),
            ("output/mid", 500),
            ("output/low", 1000),
        ]:
            glb_path = f"{output_dir}/{tile_name}.glb"
            if os.path.exists(glb_path):
                print(f"Skipping {tile_name} {output_dir} (already exists)")
                continue
            print(f"\n--- Processing tile: {tile_name} ({output_dir}) ---")
            start = time.time()
            count = process_tile(
                tile_name, raster_index, output_dir=output_dir, area_filter=area_filter
            )
            elapsed = time.time() - start
            print(f"Completed in {elapsed:.1f}s — {count} buildings exported")

    print("\n--- Building index ---")
    build_index()
