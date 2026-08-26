"""Splits the footprint datasets into one GeoPackage per output tile."""

import os

from footprints.load_footprints import load_tile_footprints


def create_tiles(grid, footprint_dirs, output_dir="output/tiles"):
    """
    Writes a buildings GeoPackage for each grid tile that contains footprints.
    Skips tiles that already have an output file. Returns the names of all
    populated tiles (including ones skipped because they already existed).
    """
    os.makedirs(output_dir, exist_ok=True)

    populated = []
    tiles = grid["tiles"]

    for i, tile in enumerate(tiles):
        if i % 50 == 0:
            print(f"Progress: {i}/{len(tiles)} tiles processed, {len(populated)} populated")

        output_path = f"{output_dir}/{tile['name']}.gpkg"
        if os.path.exists(output_path):
            populated.append(tile["name"])
            continue

        footprints = load_tile_footprints(tile["x"], tile["y"], footprint_dirs)
        if footprints is None:
            continue

        footprints.to_file(output_path, driver="GPKG", layer="buildings")
        populated.append(tile["name"])

    return populated
