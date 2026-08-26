# TODO

A living list of things to come back to — not just active tasks, but things
that are *done* now but will silently go stale later (data snapshots, etc).
Check dates against today before assuming something's still current.

## Recurring: data refresh

- **OSM building footprints** (Geofabrik county extracts, `pre-processing/data/footprints/`)
  — these are undated "latest" snapshots, so the copy in this repo is frozen at
  whatever day it was downloaded. OSM itself updates continuously. Re-download
  yearly, or before any run where up-to-date buildings matter.
  See `pre-processing/data/footprints/SOURCES.md` for the county list, sources,
  and per-county download dates.

- **DEFRA LIDAR Composite DSM/DTM** (`pre-processing/data/dsm/`, `data/dtm/`)
  — DEFRA reissues the composite periodically as more survey coverage becomes
  available (no fixed schedule). Worth checking environment.data.gov.uk/survey
  for a newer composite every year or two, or if a specific area looks off.

## Pipeline setup (in progress)

- [x] OSM footprints for all 5 counties (Kent, East Sussex, Surrey, West
      Sussex, Greater London) — uploaded and verified complete.
- [x] Study radius reduced from 50km to 25km to cut DSM/DTM data volume
      (355 -> 99 DEFRA tiles); Essex dropped since it's now outside the
      radius. `pre-processing/data/required_dsm_tiles.txt` reflects the
      current 99-tile list.
- [x] DSM/DTM tiles downloaded to a local PC via `download_dsm_dtm.py`;
      surplus tiles from the old 50km radius cleaned up with
      `cleanup_out_of_radius_tiles.py`.
- [ ] Upload the full 99-tile DSM/DTM set into the Codespace (only a handful
      of tiles near the station are in place so far, for viewer testing).
- [ ] Run `main.py` end to end for the full 25km area once the tiles above are
      in place; sanity-check with the `checks/` scripts before trusting the
      output.

## Model viewer (in progress)

- [x] Scaffolded a React Three Fiber + Vite viewer in `model/`, reading
      GLBs + `public/tiles/manifest.json` (tile name, file, offset) written
      by `checks/build_test_tiles.py`.
- [ ] Swap the default `OrbitControls` for Google Maps-style touch controls
      (pan/pinch-zoom/rotate).
- [ ] Apply real styling once a reference Three.js project is shared.

## Later (explicitly deferred)

- [ ] Add non-building features to the model. `SOURCES.md` documents the other
      OSM layers already sitting in each county's shapefile zip (roads,
      landuse, natural, water, etc.) for when this comes up.
