# Footprint data sources

Study area: a 25km-radius circle centred on Royal Tunbridge Wells rail station
(51.130222, 0.263046) — see `STUDY_CENTER_LAT`/`STUDY_CENTER_LON`/`STUDY_RADIUS_M`
in `config.py`. (Reduced from an initial 50km radius to cut down the DSM/DTM
data volume; see [TODO.md](../../../TODO.md).)

## Counties needed

Determined by checking each Geofabrik county boundary (`.poly` file) against the
study circle. Kent contains the station; the other four are included because
the circle crosses into them (distance below is from the station to the
nearest point on that county's boundary):

| County | Folder | Distance to boundary | Downloaded | Geofabrik page |
|---|---|---|---|---|
| Kent | `kent/` | station is inside | 2026-08-24 | https://download.geofabrik.de/europe/united-kingdom/england/kent.html |
| East Sussex | `east-sussex/` | ~1 km | 2026-08-26 | https://download.geofabrik.de/europe/united-kingdom/england/east-sussex.html |
| Greater London | `greater-london/` | ~22 km | 2026-08-26 | https://download.geofabrik.de/europe/united-kingdom/england/greater-london.html |
| Surrey | `surrey/` | ~15 km | 2026-08-26 | https://download.geofabrik.de/europe/united-kingdom/england/surrey.html |
| West Sussex | `west-sussex/` | ~16 km | 2026-08-26 | https://download.geofabrik.de/europe/united-kingdom/england/west-sussex.html |

Checked but excluded: **Essex** (~36km — was needed at the original 50km
radius, dropped when the radius shrank to 25km) and **Hampshire** (~70km,
excluded from the start).

For each county, download `<county>-latest-free.shp.zip` and unzip its
contents directly into the matching folder above (same layout as `kent/`).

## What's in each shapefile zip

Geofabrik's free shapefile extracts split OSM data into layers by theme, each as
its own `.shp` (+ `.dbf`/`.shx`/`.prj`/`.cpg`). We currently only read the
buildings layer (`gis_osm_buildings_a_free_1.shp`); the rest is present in every
county folder already and is documented here for when we add non-building
features to the model.

`_a` in a filename means the polygon/area version of that layer; layers without
an area version are lines or points only.

| Filename | Geometry | Contents |
|---|---|---|
| `gis_osm_buildings_a_free_1.shp` | polygon | Building footprints — **in use now** |
| `gis_osm_landuse_a_free_1.shp` | polygon | Land use/cover areas (residential, industrial, forest, farmland, etc.) |
| `gis_osm_natural_a_free_1.shp` | polygon | Natural areas (woods, wetland, beaches, water) |
| `gis_osm_natural_free_1.shp` | point | Natural point features (peaks, trees, springs) |
| `gis_osm_places_a_free_1.shp` | polygon | Named place boundaries (city/town/suburb) |
| `gis_osm_places_free_1.shp` | point | Named place labels (city/town/village centroids) |
| `gis_osm_pofw_a_free_1.shp` | polygon | Places of worship (as areas) |
| `gis_osm_pofw_free_1.shp` | point | Places of worship (as points) |
| `gis_osm_pois_a_free_1.shp` | polygon | Points of interest (as areas) — amenities, shops, etc. |
| `gis_osm_pois_free_1.shp` | point | Points of interest (as points) |
| `gis_osm_railways_free_1.shp` | line | Railway/tram/subway lines |
| `gis_osm_roads_free_1.shp` | line | Road and path network |
| `gis_osm_traffic_a_free_1.shp` | polygon | Traffic-related areas (car parks, etc.) |
| `gis_osm_traffic_free_1.shp` | point | Traffic-related points (signals, stops) |
| `gis_osm_transport_a_free_1.shp` | polygon | Transport areas (airports, stations) |
| `gis_osm_transport_free_1.shp` | point | Transport points (bus stops, stations) |
| `gis_osm_water_a_free_1.shp` | polygon | Water bodies (lakes, reservoirs) |
| `gis_osm_waterways_free_1.shp` | line | Rivers, streams, canals |

Layer list is Geofabrik's long-standing standard "free" tier set — worth a quick
diff against the actual zip contents once downloaded, since I couldn't verify it
byte-for-byte against their PDF format spec (no PDF text extraction available in
this environment).
