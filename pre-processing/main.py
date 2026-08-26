"""
Buildings pipeline entry point. Run from the pre-processing/ directory:

    python main.py

Stages, in order:
  1. Index the DEFRA DSM/DTM raster tiles on disk (raster_index)
  2. Build the output tile grid covering the footprint datasets (coverage_grid)
  3. Split the footprint datasets into per-tile GeoPackages (footprints)
  4. For each populated tile and each level of detail: sample heights and
     export a GLB (tiles)
  5. Build the summary index.json the viewer reads (tiles)
"""

import os
import time

from config import (
    DSM_DIR,
    DTM_DIR,
    FOOTPRINT_DIRS,
    GRID_PATH,
    LOD_LEVELS,
    RASTER_INDEX_PATH,
    TILE_INDEX_PATH,
    TILES_DIR,
)
from coverage_grid.build_coverage_grid import build_coverage_grid
from footprints.create_tiles import create_tiles
from raster_index.build_raster_index import build_raster_index, load_raster_index
from tiles.build_tile_index import build_tile_index
from tiles.process_tile import process_tile


def main():
    print("--- Building raster index ---")
    build_raster_index(DSM_DIR, DTM_DIR, output_path=RASTER_INDEX_PATH)

    print("\n--- Building coverage grid ---")
    grid = build_coverage_grid(FOOTPRINT_DIRS, output_path=GRID_PATH)

    print("\n--- Creating footprint tiles ---")
    populated = create_tiles(grid, FOOTPRINT_DIRS, output_dir=TILES_DIR)
    print(f"Populated tiles: {len(populated)}")

    raster_index = load_raster_index(RASTER_INDEX_PATH)
    for output_dir, _ in LOD_LEVELS:
        os.makedirs(output_dir, exist_ok=True)

    for tile_name in populated:
        for output_dir, area_filter in LOD_LEVELS:
            glb_path = f"{output_dir}/{tile_name}.glb"
            if os.path.exists(glb_path):
                print(f"Skipping {tile_name} {output_dir} (already exists)")
                continue
            print(f"\n--- Processing tile: {tile_name} ({output_dir}) ---")
            start = time.time()
            count = process_tile(tile_name, raster_index, output_dir=output_dir, area_filter=area_filter)
            print(f"Completed in {time.time() - start:.1f}s — {count} buildings exported")

    print("\n--- Building tile index ---")
    build_tile_index(LOD_LEVELS[0][0], TILE_INDEX_PATH)


if __name__ == "__main__":
    main()
