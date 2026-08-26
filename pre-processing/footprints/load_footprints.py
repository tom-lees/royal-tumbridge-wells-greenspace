"""Loads the OSM building footprints belonging to a single output tile."""

import os

import geopandas as gpd
import pandas as pd
from shapely.geometry import box

from config import TILE_SIZE
from footprints.tile_bounds import get_tile_bounds_wgs84


def load_tile_footprints(tile_x, tile_y, footprint_dirs, area_filter=100):
    """
    Loads buildings for a single tile from all county shapefiles.
    Filters by centroid within tile bounds in Mercator.
    Returns a GeoDataFrame in Mercator (EPSG:3857), or None if empty.
    """
    left, bottom, right, top = get_tile_bounds_wgs84(tile_x, tile_y)
    tile_box = box(tile_x, tile_y, tile_x + TILE_SIZE, tile_y + TILE_SIZE)

    gdfs = []
    for county_dir in footprint_dirs:
        shp = f"{county_dir}/gis_osm_buildings_a_free_1.shp"
        if not os.path.exists(shp):
            continue
        try:
            gdf = gpd.read_file(shp, bbox=(left, bottom, right, top))
            if len(gdf) > 0:
                gdfs.append(gdf)
        except Exception as e:
            print(f"Error reading {shp}: {e}")

    if not gdfs:
        return None

    combined = pd.concat(gdfs, ignore_index=True)
    combined = gpd.GeoDataFrame(combined, crs="EPSG:4326")
    combined = combined.to_crs(epsg=3857)
    combined = combined[combined.geometry.area > area_filter]
    if len(combined) == 0:
        return None

    inside = combined.geometry.centroid.within(tile_box)
    combined = combined[inside]
    if len(combined) == 0:
        return None

    return combined.drop_duplicates(subset=["osm_id"])
