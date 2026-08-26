"""Samples building roof height (above ground) from an nDSM raster."""

import numpy as np
from rasterio.io import MemoryFile
from rasterio.mask import mask
from shapely.geometry import mapping

from config import MIN_BUILDING_HEIGHT, ROOF_HEIGHT_PERCENTILE


def sample_roof_heights(footprints, ndsm_data, min_height=MIN_BUILDING_HEIGHT, percentile=ROOF_HEIGHT_PERCENTILE):
    """
    Samples nDSM height for each building footprint via zonal percentile —
    the percentile is used instead of the max so a single noisy pixel
    (aerial/chimney) doesn't blow up the building height.
    Reprojects footprints to match the nDSM CRS before sampling.
    Returns footprints with a 'height' column; buildings with no valid
    pixels (e.g. entirely nodata) are dropped.
    """
    ndsm = ndsm_data["ndsm"]
    transform = ndsm_data["transform"]
    crs = ndsm_data["crs"]

    footprints = footprints.to_crs(crs)

    with MemoryFile() as memfile:
        with memfile.open(
            driver="GTiff",
            height=ndsm.shape[0],
            width=ndsm.shape[1],
            count=1,
            dtype=ndsm.dtype,
            crs=crs,
            transform=transform,
        ) as dataset:
            dataset.write(ndsm, 1)

            heights = []
            for row in footprints.itertuples():
                try:
                    out_image, _ = mask(dataset, [mapping(row.geometry)], crop=True, nodata=np.nan)
                    pixels = out_image[0]
                    pixels = pixels[~np.isnan(pixels)]
                    pixels = pixels[pixels >= min_height]
                    heights.append(float(np.percentile(pixels, percentile)) if len(pixels) else None)
                except Exception:
                    heights.append(None)

    footprints = footprints.copy()
    footprints["height"] = heights
    return footprints[footprints["height"].notna()]
