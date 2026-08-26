"""Turns a single tile's footprints into a finished GLB: find the covering
DEFRA rasters, sample heights, extrude, export."""

import os

import geopandas as gpd

from config import TILES_DIR
from mesh.build_tile_mesh import build_tile_mesh
from mesh.export_glb import create_empty_glb, export_glb


def process_tile(tile_name, raster_index, output_dir="output/high", area_filter=100):
    """
    Samples heights, extrudes, and exports a single tile's buildings as a
    GLB. Returns the number of buildings exported.
    """
    gpkg_path = f"{TILES_DIR}/{tile_name}.gpkg"
    if not os.path.exists(gpkg_path):
        print(f"  No footprints found for {tile_name}")
        return 0

    footprints = gpd.read_file(gpkg_path, layer="buildings")
    footprints = footprints[footprints.geometry.area > area_filter]
    print(f"  {len(footprints)} buildings after area filter ({area_filter}m²)")
    if len(footprints) == 0:
        create_empty_glb(f"{output_dir}/{tile_name}.glb")
        return 0

    tile_x, tile_y = map(int, tile_name.split("_"))

    buildings, footprints = build_tile_mesh(footprints, tile_x, tile_y, raster_index)
    if buildings is None:
        print("  No buildings — writing empty GLB")
        create_empty_glb(f"{output_dir}/{tile_name}.glb")
        return 0

    export_glb(buildings, f"{output_dir}/{tile_name}.glb")
    return len(footprints)
