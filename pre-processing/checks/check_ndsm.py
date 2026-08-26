"""Visual check: plots the nDSM and DTM for a single sample raster tile.
Run from pre-processing/: python -m checks.check_ndsm
"""

import json
import os

import matplotlib.pyplot as plt
import numpy as np

from config import RASTER_INDEX_PATH
from elevation.calc_ndsm import calc_ndsm

SAMPLE_TILE = "TQ3080"
OUTPUT_PATH = "output/testing/calc_ndsm.png"


def main():
    with open(RASTER_INDEX_PATH) as f:
        raster_index = json.load(f)

    raster = raster_index[SAMPLE_TILE]
    result = calc_ndsm(raster["dsm"], raster["dtm"])

    print(f"nDSM shape: {result['ndsm'].shape}")
    print(f"nDSM min: {np.nanmin(result['ndsm']):.2f}m  max: {np.nanmax(result['ndsm']):.2f}m")
    print(f"DTM min: {np.nanmin(result['dtm']):.2f}m  max: {np.nanmax(result['dtm']):.2f}m")
    print(f"CRS: {result['crs']}")

    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    fig.patch.set_facecolor("black")
    for ax, data, title in zip(axes, [result["ndsm"], result["dtm"]], ["nDSM", "DTM"]):
        ax.set_facecolor("black")
        im = ax.imshow(data, cmap="viridis")
        ax.set_title(title, color="white")
        plt.colorbar(im, ax=ax)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    plt.savefig(OUTPUT_PATH, dpi=150, bbox_inches="tight")
    print(f"Saved {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
