"""Lists the 5km DEFRA tile references covering the study area circle, and
writes them to a text file for reference when downloading DSM/DTM tiles.
Run from pre-processing/: python -m checks.list_required_dsm_tiles
"""

import os

from config import STUDY_AREA_NAME, STUDY_CENTER_LAT, STUDY_CENTER_LON, STUDY_RADIUS_M
from raster_index.required_tiles import list_required_tiles

OUTPUT_PATH = "data/required_dsm_tiles.txt"


def main():
    tiles = list_required_tiles(STUDY_CENTER_LAT, STUDY_CENTER_LON, STUDY_RADIUS_M)

    print(f"{STUDY_AREA_NAME}: {STUDY_RADIUS_M / 1000:.0f}km radius")
    print(f"{len(tiles)} tiles needed:\n")
    for tile in tiles:
        print(tile)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        f.write("\n".join(tiles) + "\n")
    print(f"\nSaved {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
