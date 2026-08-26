"""OS National Grid (British National Grid, EPSG:27700) reference encoding.

Standard algorithm (letters, then digit pair, then optional 5km quadrant
suffix) — validated against two published worked examples: Ben Nevis
(216600, 771200) -> NN166712, and Glastonbury Tor (351219, 138616) ->
ST5121938616.
"""

from pyproj import Transformer

_GRID_CHARS = "ABCDEFGHJKLMNOPQRSTUVWXYZ"  # no 'I'

_WGS84_TO_BNG = Transformer.from_crs("EPSG:4326", "EPSG:27700", always_xy=True)


def wgs84_to_bng(lat, lon):
    """WGS84 (lat, lon) -> BNG (easting, northing) in metres."""
    easting, northing = _WGS84_TO_BNG.transform(lon, lat)
    return easting, northing


def bng_to_grid_letters(easting, northing):
    """BNG easting/northing -> the two-letter 100km grid square, e.g. 'TQ'."""
    e100k = int(easting // 100000)
    n100k = int(northing // 100000)
    l1 = (19 - n100k) - (19 - n100k) % 5 + (e100k + 10) // 5
    l2 = (19 - n100k) * 5 % 25 + e100k % 5
    return _GRID_CHARS[l1] + _GRID_CHARS[l2]


def bng_to_grid_ref(easting, northing, figures=10):
    """BNG easting/northing -> a standard grid reference, e.g. 'TQ584392' (6-figure)."""
    letters = bng_to_grid_letters(easting, northing)
    e = str(int(easting % 100000)).zfill(5)[: figures // 2]
    n = str(int(northing % 100000)).zfill(5)[: figures // 2]
    return f"{letters}{e}{n}"


def bng_to_5km_tile(easting, northing):
    """
    BNG easting/northing -> the 5km DEFRA/OS tile reference for that point,
    e.g. 'TQ53ne' (letters + 10km-square digits + NE/NW/SE/SW quadrant).
    """
    letters = bng_to_grid_letters(easting, northing)
    e10 = int(easting % 100000) // 10000
    n10 = int(northing % 100000) // 10000
    sub_e = int(easting % 10000)
    sub_n = int(northing % 10000)
    ns = "n" if sub_n >= 5000 else "s"
    ew = "e" if sub_e >= 5000 else "w"
    return f"{letters}{e10}{n10}{ns}{ew}"
