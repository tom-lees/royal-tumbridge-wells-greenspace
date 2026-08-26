"""Shared middle step of turning a tile's footprints into a mesh: find the
covering DEFRA rasters, sample heights, extrude. Used by both the full
pipeline (tiles/process_tile.py) and ad-hoc test scripts (checks/)."""

from config import TILE_SIZE
from elevation.collect_tile_heights import collect_tile_heights
from mesh.extrude_buildings import extrude_buildings
from tiles.find_rasters_for_tile import find_rasters_for_tile


def build_tile_mesh(footprints, tile_x, tile_y, raster_index):
    """
    Samples heights and extrudes a tile's footprints into a buildings mesh.
    footprints must be in Web Mercator (EPSG:3857).
    Returns (mesh, footprints_with_heights), or (None, None) if no rasters
    cover the tile or no building resolved a height.
    """
    rasters = find_rasters_for_tile(tile_x, tile_y, raster_index)
    print(f"  Found {len(rasters)} rasters: {[r[0] for r in rasters]}")
    if not rasters:
        return None, None

    footprints = collect_tile_heights(footprints, rasters)
    if len(footprints) == 0:
        return None, None
    print(f"  Height range: {footprints['height'].min():.2f}m - {footprints['height'].max():.2f}m")

    tile_cx, tile_cy = tile_x + TILE_SIZE / 2, tile_y + TILE_SIZE / 2
    mesh = extrude_buildings(footprints, tile_cx, tile_cy)
    return mesh, footprints
