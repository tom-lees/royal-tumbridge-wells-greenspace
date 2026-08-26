"""Processes a small hand-picked set of output-grid tiles into GLBs, for
testing the pipeline and the viewer without running the full county-wide
grid. Writes GLBs into output/test/, copies them into the viewer's public
folder, and writes model/public/tiles/manifest.json with each tile's
position relative to ORIGIN_TILE.

Grow TEST_TILES as more DEFRA tile pairs become available. Run from
pre-processing/: python -m checks.build_test_tiles
"""

import json
import os
import shutil

from config import DSM_DIR, DTM_DIR, FOOTPRINT_DIRS, TILE_SIZE
from footprints.load_footprints import load_tile_footprints
from mesh.build_tile_mesh import build_tile_mesh
from mesh.export_glb import export_glb
from raster_index.build_raster_index import build_raster_index

# Our own Mercator output-grid tiles around the station (centre + immediate
# neighbours). ORIGIN_TILE is the viewer's (0, 0) — every other tile's
# manifest offset is relative to it.
ORIGIN_TILE = (25000, 6640000)  # centre tile, covers DEFRA tile TQ53ne
TEST_TILES = [
    ORIGIN_TILE,
    (25000, 6645000),  # N, covers TQ53ne + TQ54se
]

OUTPUT_DIR = "output/test"
VIEWER_TILES_DIR = "../model/public/tiles"
MANIFEST_PATH = f"{VIEWER_TILES_DIR}/manifest.json"


def process_test_tile(tile_x, tile_y, raster_index):
    tile_name = f"{tile_x}_{tile_y}"
    footprints = load_tile_footprints(tile_x, tile_y, FOOTPRINT_DIRS)
    if footprints is None:
        print(f"  No footprints found for {tile_name}")
        return None
    print(f"  {len(footprints)} buildings in tile")

    buildings, footprints = build_tile_mesh(footprints, tile_x, tile_y, raster_index)
    if buildings is None:
        print("  No buildings resolved a height, skipping")
        return None

    glb_path = f"{OUTPUT_DIR}/{tile_name}.glb"
    export_glb(buildings, glb_path)
    return glb_path


def main():
    print("--- Building raster index (whatever's in data/dsm and data/dtm) ---")
    raster_index = build_raster_index(DSM_DIR, DTM_DIR)
    print(f"{len(raster_index)} raster tile(s) indexed: {list(raster_index)}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(VIEWER_TILES_DIR, exist_ok=True)

    origin_cx = ORIGIN_TILE[0] + TILE_SIZE / 2
    origin_cy = ORIGIN_TILE[1] + TILE_SIZE / 2

    manifest = []
    for tile_x, tile_y in TEST_TILES:
        tile_name = f"{tile_x}_{tile_y}"
        print(f"\n--- {tile_name} ---")
        glb_path = process_test_tile(tile_x, tile_y, raster_index)
        if glb_path is None:
            continue

        shutil.copy(glb_path, f"{VIEWER_TILES_DIR}/{tile_name}.glb")

        # The mesh's Z axis is the negated Mercator Y (see
        # mesh/extrude_buildings._remap_to_threejs_up), so offsetZ flips sign.
        tile_cx, tile_cy = tile_x + TILE_SIZE / 2, tile_y + TILE_SIZE / 2
        manifest.append(
            {
                "name": tile_name,
                "file": f"tiles/{tile_name}.glb",
                "offsetX": tile_cx - origin_cx,
                "offsetZ": -(tile_cy - origin_cy),
            }
        )

    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"\nWrote manifest with {len(manifest)} tile(s) to {MANIFEST_PATH}")


if __name__ == "__main__":
    main()
