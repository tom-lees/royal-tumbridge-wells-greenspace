import numpy as np
from rasterio.mask import mask
from shapely.geometry import mapping
import rasterio
from rasterio.io import MemoryFile


def sample_heights(footprints, ndsm_data, min_height=2.5, percentile=95):
    """
    Samples nDSM height for each building footprint.
    Reprojects footprints to match nDSM CRS before sampling.
    """
    ndsm = ndsm_data["ndsm"]
    transform = ndsm_data["transform"]
    crs = ndsm_data["crs"]
    meta = ndsm_data["meta"]

    # Reproject footprints to match raster CRS
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
                    geom = [mapping(row.geometry)]
                    out_image, _ = mask(dataset, geom, crop=True, nodata=np.nan)
                    pixels = out_image[0]
                    pixels = pixels[~np.isnan(pixels)]
                    pixels = pixels[pixels >= min_height]
                    if len(pixels) == 0:
                        heights.append(None)
                    else:
                        heights.append(float(np.percentile(pixels, percentile)))
                except Exception:
                    heights.append(None)

            footprints = footprints.copy()
            footprints["height"] = heights
            footprints = footprints[footprints["height"].notna()]

    return footprints


if __name__ == "__main__":
    import json
    from calc_ndsm import calc_ndsm
    import geopandas as gpd

    print("--- Testing sample_heights ---")

    with open("data/raster_index.json") as f:
        raster_index = json.load(f)

    raster = raster_index["TQ3080"]
    ndsm_data = calc_ndsm(raster["dsm"], raster["dtm"])
    print(f"nDSM CRS: {ndsm_data['crs']}")

    # Load a tile's footprints
    import math
    from pyproj import Transformer
    to_mercator = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
    nelson_x, nelson_y = to_mercator.transform(-0.1279308, 51.5077567)
    tile_x = math.floor(nelson_x / 5000) * 5000
    tile_y = math.floor(nelson_y / 5000) * 5000
    tile_name = f"{tile_x}_{tile_y}"

    footprints = gpd.read_file(f"output/tiles/{tile_name}.gpkg", layer="buildings")
    print(f"Footprints CRS: {footprints.crs}")
    print(f"Footprints count: {len(footprints)}")

    result = sample_heights(footprints, ndsm_data)
    print(f"Buildings with heights: {len(result)}")
    if len(result) > 0:
        print(result[["osm_id", "height"]].head(10))
