import os
import json
import geopandas as gpd
import pandas as pd
from shapely.geometry import box
from pyproj import Transformer
import numpy as np
import math

FOOTPRINT_DIRS = [
    "data/footprints/berkshire",
    "data/footprints/buckinghamshire",
    "data/footprints/essex",
    "data/footprints/greater-london",
    "data/footprints/hertfordshire",
    "data/footprints/surrey",
]

TILE_SIZE = 5000  # Web Mercator metres


def get_tile_bounds_wgs84(tile_x, tile_y, tile_size=TILE_SIZE):
    """Convert Mercator tile bounds to WGS84 for bbox query."""
    to_wgs84 = Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True)
    left, bottom = to_wgs84.transform(tile_x, tile_y)
    right, top = to_wgs84.transform(tile_x + tile_size, tile_y + tile_size)
    return left, bottom, right, top


def load_tile_footprints(tile_x, tile_y, footprint_dirs, area_filter=100):
    """
    Loads buildings for a single tile from all county shapefiles.
    Filters by centroid within tile bounds in Mercator.
    Returns GeoDataFrame in Mercator (EPSG:3857) or None if empty.
    """
    left, bottom, right, top = get_tile_bounds_wgs84(tile_x, tile_y)
    tile_box = box(tile_x, tile_y, tile_x + TILE_SIZE, tile_y + TILE_SIZE)

    gdfs = []
    for county_dir in footprint_dirs:
        shp = f"{county_dir}/gis_osm_buildings_a_free_1.shp"
        if not os.path.exists(shp):
            continue
        try:
            gdf = gpd.read_file(shp, bbox=(left, bottom, right, top))
            if len(gdf) == 0:
                continue
            gdfs.append(gdf)
        except Exception as e:
            print(f"Error reading {shp}: {e}")
            continue

    if not gdfs:
        return None

    combined = pd.concat(gdfs, ignore_index=True)
    combined = gpd.GeoDataFrame(combined, crs="EPSG:4326")
    combined = combined.to_crs(epsg=3857)
    combined = combined[combined.geometry.area > area_filter]

    if len(combined) == 0:
        return None

    centroids = combined.geometry.centroid
    inside = centroids.within(tile_box)
    combined = combined[inside]

    if len(combined) == 0:
        return None

    combined = combined.drop_duplicates(subset=["osm_id"])

    return combined


def create_tiles(grid, footprint_dirs, output_dir="output/tiles"):
    """
    Creates a tile gpkg file for each grid tile that contains buildings.
    Returns list of populated tile names.
    """
    os.makedirs(output_dir, exist_ok=True)

    populated = []
    tiles = grid["tiles"]
    total = len(tiles)

    for i, tile in enumerate(tiles):
        if i % 50 == 0:
            print(f"Progress: {i}/{total} tiles processed, {len(populated)} populated")

        tile_x = tile["x"]
        tile_y = tile["y"]
        tile_name = tile["name"]

        output_path = f"{output_dir}/{tile_name}.gpkg"
        if os.path.exists(output_path):
            populated.append(tile_name)
            continue

        footprints = load_tile_footprints(tile_x, tile_y, footprint_dirs)
        if footprints is None:
            continue

        footprints.to_file(output_path, driver="GPKG", layer="buildings")
        populated.append(tile_name)

    return populated


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    import time

    print("--- Loading grid ---")
    with open("data/grid.json") as f:
        grid = json.load(f)
    print(f"Grid has {len(grid['tiles'])} tiles")

    print("\n--- Creating tiles ---")
    start = time.time()
    populated = create_tiles(grid, FOOTPRINT_DIRS)
    elapsed = time.time() - start
    print(f"Done in {elapsed:.1f}s")
    print(f"Populated tiles: {len(populated)}")

    # Visual check — plot populated vs empty tiles
    print("\n--- Generating visual check ---")
    fig, ax = plt.subplots(figsize=(12, 10))
    ax.set_facecolor("black")
    fig.patch.set_facecolor("black")
    ts = grid["tile_size"]
    for tile in grid["tiles"]:
        color = "cyan" if tile["name"] in populated else "none"
        rect = patches.Rectangle(
            (tile["x"], tile["y"]),
            ts,
            ts,
            linewidth=0.5,
            edgecolor="red",
            facecolor=color,
            alpha=0.3,
        )
        ax.add_patch(rect)
    ax.autoscale()
    ax.set_title(
        f"Populated tiles: {len(populated)} (cyan) vs empty (red outline)",
        color="white",
    )
    ax.tick_params(colors="white")
    os.makedirs("output/testing", exist_ok=True)
    plt.savefig("output/testing/tiles.png", dpi=150, bbox_inches="tight")
    print("Saved output/testing/tiles.png")

    # Spot check — plot a sample tile's buildings
    if populated:
        sample_tile = populated[len(populated) // 2]
        print(f"\n--- Spot check: {sample_tile} ---")
        gdf = gpd.read_file(f"output/tiles/{sample_tile}.gpkg", layer="buildings")
        print(f"Buildings in tile: {len(gdf)}")
        print(f"CRS: {gdf.crs}")
        fig2, ax2 = plt.subplots(figsize=(10, 10))
        ax2.set_facecolor("black")
        fig2.patch.set_facecolor("black")
        gdf.plot(ax=ax2, facecolor="none", edgecolor="white", linewidth=0.5)
        ax2.set_title(f"{sample_tile} — {len(gdf)} buildings", color="white")
        ax2.tick_params(colors="white")
        plt.savefig("output/testing/sample_tile.png", dpi=150, bbox_inches="tight")
        print("Saved output/testing/sample_tile.png")

    # Nelson's Column alignment check
    print("\n--- Nelson's Column alignment check ---")
    to_mercator = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
    nelson_lon, nelson_lat = -0.1279308, 51.5077567
    nelson_x, nelson_y = to_mercator.transform(nelson_lon, nelson_lat)
    print(f"Nelson's Column Mercator: {nelson_x:.1f}, {nelson_y:.1f}")
    tile_x = math.floor(nelson_x / TILE_SIZE) * TILE_SIZE
    tile_y = math.floor(nelson_y / TILE_SIZE) * TILE_SIZE
    tile_name = f"{tile_x}_{tile_y}"
    print(f"Should be in tile: {tile_name}")

    if os.path.exists(f"output/tiles/{tile_name}.gpkg"):
        gdf = gpd.read_file(f"output/tiles/{tile_name}.gpkg", layer="buildings")
        fig3, ax3 = plt.subplots(figsize=(10, 10))
        ax3.set_facecolor("black")
        fig3.patch.set_facecolor("black")
        gdf.plot(ax=ax3, facecolor="none", edgecolor="white", linewidth=0.5)
        ax3.plot(
            nelson_x,
            nelson_y,
            "r+",
            markersize=20,
            markeredgewidth=2,
            label="Nelson's Column",
        )
        ax3.legend(facecolor="black", labelcolor="white")
        ax3.set_title(f"Nelson's Column check — zoomed", color="white")
        ax3.tick_params(colors="white")
        ax3.set_xlim(nelson_x - 100, nelson_x + 100)
        ax3.set_ylim(nelson_y - 100, nelson_y + 100)
        plt.savefig(
            "output/testing/nelsons_column_check.png", dpi=150, bbox_inches="tight"
        )
        print("Saved output/testing/nelsons_column_check.png")
    else:
        print(f"Tile {tile_name} not yet generated")

    # Adjacent tile check — Nelson's Column tile and tile to the south
    print("\n--- Adjacent tile check ---")
    tile_south = f"{tile_x}_{tile_y - TILE_SIZE}"
    tile_north = f"{tile_x}_{tile_y}"

    fig4, axes = plt.subplots(1, 2, figsize=(30, 15))
    fig4.patch.set_facecolor("black")
    for ax, name in zip(axes, [tile_north, tile_south]):
        ax.set_facecolor("black")
        ax.set_title(name, color="white")
        path = f"output/tiles/{name}.gpkg"
        if os.path.exists(path):
            gdf = gpd.read_file(path, layer="buildings")
            gdf.plot(ax=ax, facecolor="none", edgecolor="white", linewidth=0.3)
            print(f"{name}: {len(gdf)} buildings")
        else:
            print(f"{name}: not generated")
        ax.tick_params(colors="white")
    plt.tight_layout(pad=3.0)
    plt.savefig("output/testing/adjacent_tiles.png", dpi=300, bbox_inches="tight")
    print("Saved output/testing/adjacent_tiles.png")

    # Adjacent tiles touching — as they would appear on the map
    print("\n--- Adjacent tiles touching check ---")
    fig5, ax5 = plt.subplots(figsize=(15, 15))
    ax5.set_facecolor("black")
    fig5.patch.set_facecolor("black")

    for name in [tile_north, tile_south]:
        path = f"output/tiles/{name}.gpkg"
        if os.path.exists(path):
            gdf = gpd.read_file(path, layer="buildings")
            gdf.plot(ax=ax5, facecolor="none", edgecolor="white", linewidth=0.3)

    ax5.set_title("Adjacent tiles touching", color="white")
    ax5.tick_params(colors="white")
    plt.savefig(
        "output/testing/adjacent_tiles_touching.png", dpi=300, bbox_inches="tight"
    )
    print("Saved output/testing/adjacent_tiles_touching.png")

    print("\nDone!")
