"""Indexes the DEFRA DSM/DTM tile pairs available on disk, so later stages can
look up which elevation rasters cover a given area without re-scanning the
filesystem or re-opening every GeoTIFF."""

import json
import os

import rasterio
from pyproj import Transformer
from rasterio.warp import transform_bounds


def build_raster_index(dsm_dir, dtm_dir, output_path="data/raster_index.json"):
    """
    Matches DSM/DTM tiff pairs by filename and records each tile's bounds in
    BNG (native), WGS84, and Web Mercator. Writes and returns the index.
    """
    to_mercator = Transformer.from_crs("EPSG:27700", "EPSG:3857", always_xy=True)

    dsm_tiles = set(f.replace(".tif", "") for f in os.listdir(dsm_dir) if f.endswith(".tif"))
    dtm_tiles = set(f.replace(".tif", "") for f in os.listdir(dtm_dir) if f.endswith(".tif"))
    matched = sorted(dsm_tiles & dtm_tiles)

    index = {}
    for tile in matched:
        dsm_path = f"{dsm_dir}/{tile}.tif"
        with rasterio.open(dsm_path) as src:
            bng_bounds = src.bounds
            wgs84_bounds = transform_bounds(src.crs, "EPSG:4326", *bng_bounds)
            merc_left, merc_bottom = to_mercator.transform(bng_bounds.left, bng_bounds.bottom)
            merc_right, merc_top = to_mercator.transform(bng_bounds.right, bng_bounds.top)

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


def load_raster_index(path="data/raster_index.json"):
    with open(path) as f:
        return json.load(f)
