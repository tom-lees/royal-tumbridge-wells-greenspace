"""Visual check: creates footprint tiles, then plots which grid tiles ended
up populated (cyan) vs empty (red outline), plus a spot-check of one
populated tile's buildings.
Run from pre-processing/: python -m checks.check_grid_coverage
"""

import json
import os
import time

import geopandas as gpd
import matplotlib.patches as patches
import matplotlib.pyplot as plt

from config import FOOTPRINT_DIRS, GRID_PATH, TILES_DIR
from footprints.create_tiles import create_tiles

COVERAGE_OUTPUT_PATH = "output/testing/tiles.png"
SAMPLE_OUTPUT_PATH = "output/testing/sample_tile.png"


def main():
    with open(GRID_PATH) as f:
        grid = json.load(f)
    print(f"Grid has {len(grid['tiles'])} tiles")

    print("\n--- Creating tiles ---")
    start = time.time()
    populated = create_tiles(grid, FOOTPRINT_DIRS, output_dir=TILES_DIR)
    print(f"Done in {time.time() - start:.1f}s")
    print(f"Populated tiles: {len(populated)}")

    print("\n--- Generating visual check ---")
    fig, ax = plt.subplots(figsize=(12, 10))
    ax.set_facecolor("black")
    fig.patch.set_facecolor("black")
    ts = grid["tile_size"]
    for tile in grid["tiles"]:
        color = "cyan" if tile["name"] in populated else "none"
        ax.add_patch(
            patches.Rectangle(
                (tile["x"], tile["y"]), ts, ts,
                linewidth=0.5, edgecolor="red", facecolor=color, alpha=0.3,
            )
        )
    ax.autoscale()
    ax.set_title(f"Populated tiles: {len(populated)} (cyan) vs empty (red outline)", color="white")
    ax.tick_params(colors="white")
    os.makedirs(os.path.dirname(COVERAGE_OUTPUT_PATH), exist_ok=True)
    plt.savefig(COVERAGE_OUTPUT_PATH, dpi=150, bbox_inches="tight")
    print(f"Saved {COVERAGE_OUTPUT_PATH}")

    if populated:
        sample_tile = populated[len(populated) // 2]
        print(f"\n--- Spot check: {sample_tile} ---")
        gdf = gpd.read_file(f"{TILES_DIR}/{sample_tile}.gpkg", layer="buildings")
        print(f"Buildings in tile: {len(gdf)}")
        print(f"CRS: {gdf.crs}")
        fig2, ax2 = plt.subplots(figsize=(10, 10))
        ax2.set_facecolor("black")
        fig2.patch.set_facecolor("black")
        gdf.plot(ax=ax2, facecolor="none", edgecolor="white", linewidth=0.5)
        ax2.set_title(f"{sample_tile} — {len(gdf)} buildings", color="white")
        ax2.tick_params(colors="white")
        plt.savefig(SAMPLE_OUTPUT_PATH, dpi=150, bbox_inches="tight")
        print(f"Saved {SAMPLE_OUTPUT_PATH}")


if __name__ == "__main__":
    main()
