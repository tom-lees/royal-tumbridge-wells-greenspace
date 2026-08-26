"""Samples ground elevation (DTM) at each building's centroid.

Unlike sample_roof_heights, this doesn't need a zonal statistic — ground
elevation is locally flat enough under a building footprint that a single
nearest-pixel lookup at the centroid is sufficient as a base offset for the
extruded mesh.
"""

import numpy as np
from pyproj import Transformer


def sample_ground_elevation(footprints_wgs84, ndsm_data):
    """
    Looks up the DTM pixel under each building's centroid.
    footprints_wgs84 must be in WGS84; ndsm_data holds the DTM array and
    transform in its native BNG grid (see calc_ndsm).
    Returns {index: elevation} — only for buildings whose centroid resolved
    to a valid (in-bounds, non-nodata) pixel.
    """
    to_bng = Transformer.from_crs("EPSG:4326", "EPSG:27700", always_xy=True)
    transform = ndsm_data["transform"]
    dtm = ndsm_data["dtm"]
    dtm_rows, dtm_cols = dtm.shape

    elevations = {}
    for idx, row in footprints_wgs84.iterrows():
        centroid = row.geometry.centroid
        bng_x, bng_y = to_bng.transform(centroid.x, centroid.y)
        col = int((bng_x - transform.c) / transform.a)
        row_idx = int((bng_y - transform.f) / transform.e)
        if 0 <= row_idx < dtm_rows and 0 <= col < dtm_cols:
            elevation = float(dtm[row_idx, col])
            if not np.isnan(elevation):
                elevations[idx] = elevation

    return elevations
