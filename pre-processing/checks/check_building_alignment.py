"""Visual check: uses Nelson's Column as a known landmark to verify tile
alignment, then checks that adjacent tiles' buildings line up at the seam.
Run from pre-processing/: python -m checks.check_building_alignment
"""

import math
import os

import geopandas as gpd
import matplotlib.pyplot as plt
from pyproj import Transformer

from config import TILE_SIZE, TILES_DIR

NELSON_LON, NELSON_LAT = -0.1279308, 51.5077567

ALIGNMENT_OUTPUT_PATH = "output/testing/nelsons_column_check.png"
ADJACENT_OUTPUT_PATH = "output/testing/adjacent_tiles.png"
ADJACENT_TOUCHING_OUTPUT_PATH = "output/testing/adjacent_tiles_touching.png"


def _load_tile(tile_name):
    path = f"{TILES_DIR}/{tile_name}.gpkg"
    if not os.path.exists(path):
        return None
    return gpd.read_file(path, layer="buildings")


def main():
    print("--- Nelson's Column alignment check ---")
    to_mercator = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
    nelson_x, nelson_y = to_mercator.transform(NELSON_LON, NELSON_LAT)
    print(f"Nelson's Column Mercator: {nelson_x:.1f}, {nelson_y:.1f}")

    tile_x = math.floor(nelson_x / TILE_SIZE) * TILE_SIZE
    tile_y = math.floor(nelson_y / TILE_SIZE) * TILE_SIZE
    tile_name = f"{tile_x}_{tile_y}"
    print(f"Should be in tile: {tile_name}")

    os.makedirs(os.path.dirname(ALIGNMENT_OUTPUT_PATH), exist_ok=True)

    gdf = _load_tile(tile_name)
    if gdf is not None:
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.set_facecolor("black")
        fig.patch.set_facecolor("black")
        gdf.plot(ax=ax, facecolor="none", edgecolor="white", linewidth=0.5)
        ax.plot(nelson_x, nelson_y, "r+", markersize=20, markeredgewidth=2, label="Nelson's Column")
        ax.legend(facecolor="black", labelcolor="white")
        ax.set_title("Nelson's Column check — zoomed", color="white")
        ax.tick_params(colors="white")
        ax.set_xlim(nelson_x - 100, nelson_x + 100)
        ax.set_ylim(nelson_y - 100, nelson_y + 100)
        plt.savefig(ALIGNMENT_OUTPUT_PATH, dpi=150, bbox_inches="tight")
        print(f"Saved {ALIGNMENT_OUTPUT_PATH}")
    else:
        print(f"Tile {tile_name} not yet generated")

    print("\n--- Adjacent tile check ---")
    tile_north = tile_name
    tile_south = f"{tile_x}_{tile_y - TILE_SIZE}"

    fig2, axes = plt.subplots(1, 2, figsize=(30, 15))
    fig2.patch.set_facecolor("black")
    for ax, name in zip(axes, [tile_north, tile_south]):
        ax.set_facecolor("black")
        ax.set_title(name, color="white")
        gdf = _load_tile(name)
        if gdf is not None:
            gdf.plot(ax=ax, facecolor="none", edgecolor="white", linewidth=0.3)
            print(f"{name}: {len(gdf)} buildings")
        else:
            print(f"{name}: not generated")
        ax.tick_params(colors="white")
    plt.tight_layout(pad=3.0)
    plt.savefig(ADJACENT_OUTPUT_PATH, dpi=300, bbox_inches="tight")
    print(f"Saved {ADJACENT_OUTPUT_PATH}")

    print("\n--- Adjacent tiles touching check ---")
    fig3, ax3 = plt.subplots(figsize=(15, 15))
    ax3.set_facecolor("black")
    fig3.patch.set_facecolor("black")
    for name in [tile_north, tile_south]:
        gdf = _load_tile(name)
        if gdf is not None:
            gdf.plot(ax=ax3, facecolor="none", edgecolor="white", linewidth=0.3)
    ax3.set_title("Adjacent tiles touching", color="white")
    ax3.tick_params(colors="white")
    plt.savefig(ADJACENT_TOUCHING_OUTPUT_PATH, dpi=300, bbox_inches="tight")
    print(f"Saved {ADJACENT_TOUCHING_OUTPUT_PATH}")


if __name__ == "__main__":
    main()
