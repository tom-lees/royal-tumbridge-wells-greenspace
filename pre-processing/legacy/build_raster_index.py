import os
import json
import rasterio
import geopandas as gpd
from rasterio.warp import transform_bounds
from pyproj import Transformer


def build_raster_index(dsm_dir, dtm_dir, output_path="data/raster_index.json"):
    """
    Loops all DSM/DTM tiff pairs, stores their bounds in both BNG and Web Mercator.
    Output: data/raster_index.json
    """
    to_mercator = Transformer.from_crs("EPSG:27700", "EPSG:3857", always_xy=True)

    dsm_tiles = set(
        f.replace(".tif", "") for f in os.listdir(dsm_dir) if f.endswith(".tif")
    )
    dtm_tiles = set(
        f.replace(".tif", "") for f in os.listdir(dtm_dir) if f.endswith(".tif")
    )
    matched = sorted(dsm_tiles & dtm_tiles)

    index = {}

    for tile in matched:
        dsm_path = f"{dsm_dir}/{tile}.tif"
        with rasterio.open(dsm_path) as src:
            bng_bounds = src.bounds  # native BNG
            wgs84_bounds = transform_bounds(src.crs, "EPSG:4326", *bng_bounds)
            merc_left, merc_bottom = to_mercator.transform(
                bng_bounds.left, bng_bounds.bottom
            )
            merc_right, merc_top = to_mercator.transform(
                bng_bounds.right, bng_bounds.top
            )

        index[tile] = {
            "dsm": dsm_path,
            "dtm": f"{dtm_dir}/{tile}.tif",
            "bounds_bng": {
                "left": bng_bounds.left,
                "bottom": bng_bounds.bottom,
                "right": bng_bounds.right,
                "top": bng_bounds.top,
            },
            "bounds_wgs84": {
                "left": wgs84_bounds[0],
                "bottom": wgs84_bounds[1],
                "right": wgs84_bounds[2],
                "top": wgs84_bounds[3],
            },
            "bounds_mercator": {
                "left": merc_left,
                "bottom": merc_bottom,
                "right": merc_right,
                "top": merc_top,
            },
        }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(index, f, indent=2)

    return index


def build_coverage_grid(footprint_dirs, tile_size=5000, output_path="data/grid.json"):
    """
    Unions all county shapefile extents, snaps to tile_size Web Mercator grid.
    Output: data/grid.json
    """
    to_mercator = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)

    all_bounds = []

    for county_dir in footprint_dirs:
        shp = f"{county_dir}/gis_osm_buildings_a_free_1.shp"
        if not os.path.exists(shp):
            continue
        gdf = gpd.read_file(shp)  # just need bounds, not all data
        b = gdf.total_bounds  # minx, miny, maxx, maxy in WGS84
        all_bounds.append(b)

    # Get overall extent
    import numpy as np

    all_bounds = np.array(all_bounds)
    minx = all_bounds[:, 0].min()
    miny = all_bounds[:, 1].min()
    maxx = all_bounds[:, 2].max()
    maxy = all_bounds[:, 3].max()

    # Convert to Web Mercator
    left, bottom = to_mercator.transform(minx, miny)
    right, top = to_mercator.transform(maxx, maxy)

    # Snap to tile_size grid
    import math

    grid_left = math.floor(left / tile_size) * tile_size
    grid_bottom = math.floor(bottom / tile_size) * tile_size
    grid_right = math.ceil(right / tile_size) * tile_size
    grid_top = math.ceil(top / tile_size) * tile_size

    # Generate tile origins
    tiles = []
    x = grid_left
    while x < grid_right:
        y = grid_bottom
        while y < grid_top:
            tiles.append({"x": x, "y": y, "name": f"{x}_{y}"})
            y += tile_size
        x += tile_size

    grid = {
        "tile_size": tile_size,
        "bounds_mercator": {
            "left": grid_left,
            "bottom": grid_bottom,
            "right": grid_right,
            "top": grid_top,
        },
        "tiles": tiles,
    }

    with open(output_path, "w") as f:
        json.dump(grid, f, indent=2)

    return grid


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    import numpy as np

    print("--- Building raster index ---")
    index = build_raster_index("data/dsm", "data/dtm")
    print(f"Indexed {len(index)} raster tile pairs")

    # Sample one tile to verify
    sample = list(index.values())[0]
    print(f"\nSample tile:")
    print(f"  BNG:      {sample['bounds_bng']}")
    print(f"  WGS84:    {sample['bounds_wgs84']}")
    print(f"  Mercator: {sample['bounds_mercator']}")

    print("\n--- Building coverage grid ---")
    footprint_dirs = [
        "data/footprints/berkshire",
        "data/footprints/buckinghamshire",
        "data/footprints/essex",
        "data/footprints/greater-london",
        "data/footprints/hertfordshire",
        "data/footprints/surrey",
    ]
    grid = build_coverage_grid(footprint_dirs)
    print(f"Grid bounds (Mercator): {grid['bounds_mercator']}")
    print(f"Total tiles in grid: {len(grid['tiles'])}")

    # Visual check — plot raster tiles and grid
    fig, ax = plt.subplots(figsize=(12, 10))
    ax.set_facecolor("black")
    fig.patch.set_facecolor("black")

    # Plot raster tile bounds
    for tile_name, tile in index.items():
        b = tile["bounds_mercator"]
        w = b["right"] - b["left"]
        h = b["top"] - b["bottom"]
        rect = patches.Rectangle(
            (b["left"], b["bottom"]),
            w,
            h,
            linewidth=0.3,
            edgecolor="cyan",
            facecolor="none",
            alpha=0.5,
        )
        ax.add_patch(rect)

    # Plot grid tiles
    ts = grid["tile_size"]
    for tile in grid["tiles"]:
        rect = patches.Rectangle(
            (tile["x"], tile["y"]),
            ts,
            ts,
            linewidth=0.8,
            edgecolor="red",
            facecolor="none",
            alpha=0.3,
        )
        ax.add_patch(rect)

    ax.autoscale()
    ax.set_title("Raster tiles (cyan) vs Mercator grid (red)", color="white")
    ax.tick_params(colors="white")

    os.makedirs("output/testing", exist_ok=True)
    plt.savefig("output/testing/raster_index.png", dpi=150, bbox_inches="tight")
    print("\nSaved output/testing/raster_index.png")
    print("Done!")
