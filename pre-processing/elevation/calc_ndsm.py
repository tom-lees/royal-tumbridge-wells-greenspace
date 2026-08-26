"""Computes height-above-ground (nDSM) from a DSM/DTM tile pair."""

import numpy as np
import rasterio


def calc_ndsm(dsm_path, dtm_path):
    """
    Calculates nDSM (DSM minus DTM) = height above ground.
    Returns data in the raster's native BNG CRS.
    """
    with rasterio.open(dsm_path) as dsm_src:
        dsm = dsm_src.read(1).astype(float)
        nodata = dsm_src.nodata
        meta = dsm_src.meta
        transform = dsm_src.transform
        crs = dsm_src.crs

    with rasterio.open(dtm_path) as dtm_src:
        dtm = dtm_src.read(1).astype(float)

    if nodata is not None:
        dsm[dsm == nodata] = np.nan
        dtm[dtm == nodata] = np.nan

    ndsm = np.clip(dsm - dtm, 0, None)

    return {"ndsm": ndsm, "dtm": dtm, "transform": transform, "crs": crs, "meta": meta}
