"""Combines roof height and ground elevation sampling across every DEFRA
raster that intersects a tile, since a tile (or a building within it) can
straddle more than one DSM/DTM raster."""

import numpy as np
from shapely.geometry import box

from elevation.calc_ndsm import calc_ndsm
from elevation.sample_ground_elevation import sample_ground_elevation
from elevation.sample_roof_heights import sample_roof_heights


def collect_tile_heights(footprints, rasters):
    """
    Samples height and base elevation for every building across all rasters
    that intersect the tile, averaging where a building spans more than one.
    footprints must be in Web Mercator (EPSG:3857); rasters is the list of
    (name, raster_index_entry) pairs from find_rasters_for_tile.
    Returns footprints (Mercator) with 'height' and 'base_elev' columns;
    buildings that never resolved a height are dropped.
    """
    footprints_wgs84 = footprints.to_crs(epsg=4326)

    heights_by_building = {idx: [] for idx in footprints.index}
    base_elevs_by_building = {idx: [] for idx in footprints.index}

    for raster_name, raster in rasters:
        print(f"\n  Processing raster {raster_name}...")
        ndsm_data = calc_ndsm(raster["dsm"], raster["dtm"])
        print(f"    nDSM range: {np.nanmin(ndsm_data['ndsm']):.2f}m - {np.nanmax(ndsm_data['ndsm']):.2f}m")

        raster_box_wgs84 = box(
            raster["bounds_wgs84"]["left"],
            raster["bounds_wgs84"]["bottom"],
            raster["bounds_wgs84"]["right"],
            raster["bounds_wgs84"]["top"],
        )
        subset = footprints_wgs84[footprints_wgs84.geometry.intersects(raster_box_wgs84)].copy()
        print(f"    {len(subset)} buildings intersect this raster")
        if len(subset) == 0:
            continue

        sampled = sample_roof_heights(subset, ndsm_data)
        print(f"    {len(sampled)} buildings got height data")
        for idx, row in sampled.iterrows():
            if row["height"] is not None and not np.isnan(row["height"]):
                heights_by_building[idx].append(row["height"])

        for idx, elevation in sample_ground_elevation(subset, ndsm_data).items():
            base_elevs_by_building[idx].append(elevation)

    final_heights = {}
    final_base_elevs = {}
    for idx in footprints.index:
        heights = heights_by_building[idx]
        if heights:
            final_heights[idx] = np.mean(heights)
            elevs = base_elevs_by_building[idx]
            final_base_elevs[idx] = np.mean(elevs) if elevs else 0.0

    footprints = footprints.copy()
    footprints["height"] = [final_heights.get(idx) for idx in footprints.index]
    footprints["base_elev"] = [final_base_elevs.get(idx, 0.0) for idx in footprints.index]

    return footprints[footprints["height"].notna()]
