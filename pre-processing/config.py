"""Shared constants for the buildings pipeline. Edit paths/thresholds here, not in the pipeline modules."""

# Output/render tile grid size, in Web Mercator metres. Distinct from DEFRA's own
# BNG-aligned 5km raster tiles (see raster_index) — this is our own tiling scheme
# for splitting footprints/GLBs into loadable chunks for the viewer.
TILE_SIZE = 5000

DSM_DIR = "data/dsm"  # first-return DSM: used now, for building height
DSM_LAST_RETURN_DIR = "data/dsm_last_return"  # not used yet — reserved for flora/vegetation features
DTM_DIR = "data/dtm"

# Geofabrik county extracts, one per county the STUDY_RADIUS_M circle reaches
# into (see data/footprints/SOURCES.md for how this list was derived and what
# else is in each shapefile zip). Each expected to contain
# gis_osm_buildings_a_free_1.shp.
FOOTPRINT_DIRS = [
    "data/footprints/kent",
    "data/footprints/east-sussex",
    "data/footprints/greater-london",
    "data/footprints/surrey",
    "data/footprints/west-sussex",
]

# Study area: a circle centred on Royal Tunbridge Wells rail station, Kent.
# Coordinate is the Google Maps pin for the station (WGS84, decimal degrees).
STUDY_AREA_NAME = "Royal Tunbridge Wells"
STUDY_CENTER_LAT = 51.130222
STUDY_CENTER_LON = 0.263046
STUDY_RADIUS_M = 25_000  # 25km radius, 50km diameter

RASTER_INDEX_PATH = "data/raster_index.json"
GRID_PATH = "data/grid.json"

TILES_DIR = "output/tiles"
TILE_INDEX_PATH = "output/index.json"

# (output_dir, minimum footprint area in m^2) per level of detail
LOD_LEVELS = [
    ("output/high", 100),
    ("output/mid", 500),
    ("output/low", 1000),
]

# Roof height sampling (see elevation/sample_roof_heights.py)
MIN_BUILDING_HEIGHT = 2.5
ROOF_HEIGHT_PERCENTILE = 95
