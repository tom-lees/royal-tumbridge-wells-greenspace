"""Builds the output/render tile grid: a Web Mercator grid covering the full
extent of the footprint datasets, snapped to TILE_SIZE. This is what gets
split into per-tile GeoPackages and, later, per-tile GLBs."""

import json
import math
import os

import geopandas as gpd
import numpy as np
from pyproj import Transformer


def build_coverage_grid(footprint_dirs, tile_size=5000, output_path="data/grid.json"):
    """
    Unions the extent of every county footprint shapefile, then snaps that
    extent to a tile_size grid in Web Mercator. Writes and returns the grid.
    """
    to_mercator = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)

    all_bounds = []
    for county_dir in footprint_dirs:
        shp = f"{county_dir}/gis_osm_buildings_a_free_1.shp"
        if not os.path.exists(shp):
            continue
        gdf = gpd.read_file(shp)  # just need bounds, not all data
        all_bounds.append(gdf.total_bounds)  # minx, miny, maxx, maxy in WGS84

    all_bounds = np.array(all_bounds)
    minx, miny = all_bounds[:, 0].min(), all_bounds[:, 1].min()
    maxx, maxy = all_bounds[:, 2].max(), all_bounds[:, 3].max()

    left, bottom = to_mercator.transform(minx, miny)
    right, top = to_mercator.transform(maxx, maxy)

    grid_left = math.floor(left / tile_size) * tile_size
    grid_bottom = math.floor(bottom / tile_size) * tile_size
    grid_right = math.ceil(right / tile_size) * tile_size
    grid_top = math.ceil(top / tile_size) * tile_size

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
