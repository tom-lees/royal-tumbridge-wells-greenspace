"""Works out which 5km DEFRA/OS grid tiles a study-area circle touches."""

import math

from raster_index.os_grid import bng_to_5km_tile, wgs84_to_bng

DEFRA_TILE_SIZE_M = 5000  # DEFRA/OS National Grid raster tile size — distinct
# from config.TILE_SIZE, which is our own Web Mercator output tiling scheme.


def _closest_point_on_tile(tile_left, tile_bottom, tile_size, x, y):
    clamped_x = min(max(x, tile_left), tile_left + tile_size)
    clamped_y = min(max(y, tile_bottom), tile_bottom + tile_size)
    return clamped_x, clamped_y


def list_required_tiles(center_lat, center_lon, radius_m, tile_size=DEFRA_TILE_SIZE_M):
    """
    Returns the sorted list of 5km tile references (e.g. 'TQ53ne') whose
    square overlaps a circle of radius_m around (center_lat, center_lon).
    """
    center_e, center_n = wgs84_to_bng(center_lat, center_lon)

    min_e = math.floor((center_e - radius_m) / tile_size) * tile_size
    max_e = math.ceil((center_e + radius_m) / tile_size) * tile_size
    min_n = math.floor((center_n - radius_m) / tile_size) * tile_size
    max_n = math.ceil((center_n + radius_m) / tile_size) * tile_size

    tiles = set()
    e = min_e
    while e < max_e:
        n = min_n
        while n < max_n:
            closest_x, closest_y = _closest_point_on_tile(e, n, tile_size, center_e, center_n)
            if math.hypot(closest_x - center_e, closest_y - center_n) <= radius_m:
                tiles.add(bng_to_5km_tile(e + 1, n + 1))  # +1m nudges inside the tile, away from the boundary
            n += tile_size
        e += tile_size

    return sorted(tiles)
