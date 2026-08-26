"""Builds the summary index.json the viewer uses to discover available tiles."""

import json
import os

from config import TILE_SIZE


def build_tile_index(output_dir="output/high", index_path="output/index.json"):
    """Scans a GLB output directory and writes a tile-name + centre summary."""
    tiles = []
    for f in sorted(os.listdir(output_dir)):
        if not f.endswith(".glb"):
            continue
        tile_name = f.replace(".glb", "")
        x, y = map(int, tile_name.split("_"))
        tiles.append({"tile": tile_name, "centre_x": x + TILE_SIZE / 2, "centre_y": y + TILE_SIZE / 2})

    with open(index_path, "w") as f:
        json.dump(tiles, f, indent=2)
    print(f"Built index.json with {len(tiles)} tiles")
