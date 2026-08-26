"""
Removes downloaded DSM/DTM tiles that are no longer needed after shrinking
STUDY_RADIUS_M (e.g. 50km -> 25km) — anything on disk whose tile reference
isn't in data/required_dsm_tiles.txt is surplus.

Deliberately standalone and dependency-free (stdlib only), same as
download_dsm_dtm.py, so it can run anywhere Python 3 is installed — e.g.
directly against C:\\Users\\...\\Downloads\\DATA on your PC, not just in the
Codespace. Resolves data/dsm, data/dtm, data/dsm_last_return, and
data/required_dsm_tiles.txt *next to this script*, not your current working
directory.

DRY RUN BY DEFAULT: lists what would be deleted and how much space it would
free, but doesn't touch anything. Pass --delete to actually remove the files.

Usage:
    python3 cleanup_out_of_radius_tiles.py            # dry run
    python3 cleanup_out_of_radius_tiles.py --delete   # actually delete
    python3 cleanup_out_of_radius_tiles.py --delete path/to/required_dsm_tiles.txt
"""

import os
import sys

# Same product -> directory mapping as download_dsm_dtm.py.
PRODUCT_DIRS = [
    "data/dsm",
    "data/dtm",
    "data/dsm_last_return",
]


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))

    args = sys.argv[1:]
    delete = "--delete" in args
    positional = [a for a in args if a != "--delete"]
    tiles_path = positional[0] if positional else os.path.join(script_dir, "data/required_dsm_tiles.txt")

    with open(tiles_path) as f:
        required_tiles = {line.strip() for line in f if line.strip()}
    print(f"{len(required_tiles)} tiles required at the current study radius\n")

    surplus = []
    for relative_dir in PRODUCT_DIRS:
        directory = os.path.join(script_dir, relative_dir)
        if not os.path.isdir(directory):
            continue
        for filename in sorted(os.listdir(directory)):
            if not filename.endswith(".tif"):
                continue
            tile = filename[: -len(".tif")]
            if tile not in required_tiles:
                path = os.path.join(directory, filename)
                surplus.append((path, os.path.getsize(path)))

    if not surplus:
        print("Nothing to clean up — every downloaded tile is still within the study radius.")
        return

    total_bytes = sum(size for _, size in surplus)
    verb = "Deleting" if delete else "Would delete (dry run — pass --delete to actually remove)"
    print(f"{verb} {len(surplus)} file(s), freeing {total_bytes / 1024 / 1024 / 1024:.2f} GB:\n")
    for path, size in surplus:
        print(f"  {path} ({size / 1024 / 1024:.1f} MB)")
        if delete:
            os.remove(path)

    if not delete:
        print("\nRe-run with --delete to actually remove these files.")


if __name__ == "__main__":
    main()
