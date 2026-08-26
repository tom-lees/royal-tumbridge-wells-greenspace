"""Visual check: plots DEFRA raster tile bounds (cyan) against the output
Mercator grid (red), to sanity-check they line up.
Run from pre-processing/: python -m checks.check_raster_grid
"""

import os

import matplotlib.patches as patches
import matplotlib.pyplot as plt

from config import DSM_DIR, DTM_DIR, FOOTPRINT_DIRS, GRID_PATH, RASTER_INDEX_PATH
from coverage_grid.build_coverage_grid import build_coverage_grid
from raster_index.build_raster_index import build_raster_index

OUTPUT_PATH = "output/testing/raster_index.png"


def main():
    print("--- Building raster index ---")
    index = build_raster_index(DSM_DIR, DTM_DIR, output_path=RASTER_INDEX_PATH)
    print(f"Indexed {len(index)} raster tile pairs")

    sample = list(index.values())[0]
    print("\nSample tile:")
    print(f"  BNG:      {sample['bounds_bng']}")
    print(f"  WGS84:    {sample['bounds_wgs84']}")
    print(f"  Mercator: {sample['bounds_mercator']}")

    print("\n--- Building coverage grid ---")
    grid = build_coverage_grid(FOOTPRINT_DIRS, output_path=GRID_PATH)
    print(f"Grid bounds (Mercator): {grid['bounds_mercator']}")
    print(f"Total tiles in grid: {len(grid['tiles'])}")

    fig, ax = plt.subplots(figsize=(12, 10))
    ax.set_facecolor("black")
    fig.patch.set_facecolor("black")

    for tile_name, tile in index.items():
        b = tile["bounds_mercator"]
        w, h = b["right"] - b["left"], b["top"] - b["bottom"]
        ax.add_patch(
            patches.Rectangle(
                (b["left"], b["bottom"]), w, h,
                linewidth=0.3, edgecolor="cyan", facecolor="none", alpha=0.5,
            )
        )

    ts = grid["tile_size"]
    for tile in grid["tiles"]:
        ax.add_patch(
            patches.Rectangle(
                (tile["x"], tile["y"]), ts, ts,
                linewidth=0.8, edgecolor="red", facecolor="none", alpha=0.3,
            )
        )

    ax.autoscale()
    ax.set_title("Raster tiles (cyan) vs Mercator grid (red)", color="white")
    ax.tick_params(colors="white")

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    plt.savefig(OUTPUT_PATH, dpi=150, bbox_inches="tight")
    print(f"\nSaved {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
