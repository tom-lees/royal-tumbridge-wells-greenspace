"""Looks up which DEFRA rasters cover a given output tile."""

from shapely.geometry import box

from config import TILE_SIZE


def find_rasters_for_tile(tile_x, tile_y, raster_index):
    """Finds all DEFRA rasters whose bounds intersect this tile."""
    tile_box = box(tile_x, tile_y, tile_x + TILE_SIZE, tile_y + TILE_SIZE)

    matches = []
    for name, raster in raster_index.items():
        b = raster["bounds_mercator"]
        raster_box = box(b["left"], b["bottom"], b["right"], b["top"])
        if tile_box.intersects(raster_box):
            matches.append((name, raster))

    return matches
