"""Coordinate conversion for a single output tile."""

from pyproj import Transformer

from config import TILE_SIZE


def get_tile_bounds_wgs84(tile_x, tile_y, tile_size=TILE_SIZE):
    """Converts a Mercator tile's bounds to WGS84, for bbox-filtered shapefile reads."""
    to_wgs84 = Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True)
    left, bottom = to_wgs84.transform(tile_x, tile_y)
    right, top = to_wgs84.transform(tile_x + tile_size, tile_y + tile_size)
    return left, bottom, right, top
