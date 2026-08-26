"""Visual check: samples roof heights for a sample tile's buildings and
prints the results.
Run from pre-processing/: python -m checks.check_roof_heights
"""

import json
import math

import geopandas as gpd
from pyproj import Transformer

from config import RASTER_INDEX_PATH, TILE_SIZE, TILES_DIR
from elevation.calc_ndsm import calc_ndsm
from elevation.sample_roof_heights import sample_roof_heights

SAMPLE_TILE_RASTER = "TQ3080"
# Nelson's Column, used as a known landmark to pick a populated sample tile
NELSON_LON, NELSON_LAT = -0.1279308, 51.5077567


def main():
    with open(RASTER_INDEX_PATH) as f:
        raster_index = json.load(f)

    raster = raster_index[SAMPLE_TILE_RASTER]
    ndsm_data = calc_ndsm(raster["dsm"], raster["dtm"])
    print(f"nDSM CRS: {ndsm_data['crs']}")

    to_mercator = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
    nelson_x, nelson_y = to_mercator.transform(NELSON_LON, NELSON_LAT)
    tile_x = math.floor(nelson_x / TILE_SIZE) * TILE_SIZE
    tile_y = math.floor(nelson_y / TILE_SIZE) * TILE_SIZE
    tile_name = f"{tile_x}_{tile_y}"

    footprints = gpd.read_file(f"{TILES_DIR}/{tile_name}.gpkg", layer="buildings")
    print(f"Footprints CRS: {footprints.crs}")
    print(f"Footprints count: {len(footprints)}")

    result = sample_roof_heights(footprints, ndsm_data)
    print(f"Buildings with heights: {len(result)}")
    if len(result) > 0:
        print(result[["osm_id", "height"]].head(10))


if __name__ == "__main__":
    main()
