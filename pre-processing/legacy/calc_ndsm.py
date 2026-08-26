import rasterio
import numpy as np


def calc_ndsm(dsm_path, dtm_path):
    """
    Calculates nDSM (DSM minus DTM) = height above ground.
    Returns data in native BNG CRS.
    """
    with rasterio.open(dsm_path) as dsm_src:
        dsm = dsm_src.read(1).astype(float)
        nodata = dsm_src.nodata
        meta = dsm_src.meta
        transform = dsm_src.transform
        crs = dsm_src.crs

    with rasterio.open(dtm_path) as dtm_src:
        dtm = dtm_src.read(1).astype(float)

    # Mask nodata
    if nodata is not None:
        dsm[dsm == nodata] = np.nan
        dtm[dtm == nodata] = np.nan

    ndsm = dsm - dtm
    ndsm = np.clip(ndsm, 0, None)

    return {"ndsm": ndsm, "dtm": dtm, "transform": transform, "crs": crs, "meta": meta}


if __name__ == "__main__":
    import json
    import math
    import matplotlib.pyplot as plt
    from pyproj import Transformer
    from shapely.geometry import box

    print("--- Testing calc_ndsm ---")

    with open("data/raster_index.json") as f:
        raster_index = json.load(f)

    # Test with TQ3080
    raster = raster_index["TQ3080"]
    result = calc_ndsm(raster["dsm"], raster["dtm"])

    print(f"nDSM shape: {result['ndsm'].shape}")
    print(f"nDSM min: {np.nanmin(result['ndsm']):.2f}m  max: {np.nanmax(result['ndsm']):.2f}m")
    print(f"DTM min: {np.nanmin(result['dtm']):.2f}m  max: {np.nanmax(result['dtm']):.2f}m")
    print(f"CRS: {result['crs']}")

    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    fig.patch.set_facecolor('black')
    for ax, data, title in zip(axes, [result['ndsm'], result['dtm']], ['nDSM', 'DTM']):
        ax.set_facecolor('black')
        im = ax.imshow(data, cmap='viridis')
        ax.set_title(title, color='white')
        plt.colorbar(im, ax=ax)
    plt.savefig("output/testing/calc_ndsm.png", dpi=150, bbox_inches='tight')
    print("Saved output/testing/calc_ndsm.png")
    print("Done!")
