#!/usr/bin/env python3
"""Publish PES datasets for OpenAvatar.

Usage:
    ./publish.py my_surface.xyz --name "CCH" --description "C2H+ reaction surface" --method DFT
    ./publish.py --reindex          # only regenerate index.json from content/

Gzips the given .xyz file into content/ and regenerates index.json from the
sidecar metadata of everything in content/. Then commit and push:

    git add -A && git commit -m "Add dataset" && git push
"""

import argparse
import datetime
import gzip
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
INDEX = ROOT / "index.json"


def add_dataset(xyz_path: Path, name: str, description: str, method: str) -> None:
    if not xyz_path.exists():
        raise SystemExit(f"error: {xyz_path} does not exist")

    CONTENT.mkdir(exist_ok=True)
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
    target = CONTENT / (safe + ".xyz.gz")

    with open(xyz_path, "rb") as src, gzip.open(target, "wb", compresslevel=9) as dst:
        shutil.copyfileobj(src, dst)

    meta = {
        "name": name,
        "description": description,
        "date": datetime.date.today().isoformat(),
        "method": method,
    }
    target.with_suffix(".gz.meta").write_text(json.dumps(meta, indent=2))
    print(f"added {target.name} ({target.stat().st_size / 1e6:.1f} MB compressed)")


def reindex() -> None:
    items = []
    for gz in sorted(CONTENT.glob("*.xyz.gz")):
        meta_file = gz.with_suffix(".gz.meta")
        meta = json.loads(meta_file.read_text()) if meta_file.exists() else {}
        items.append(
            {
                "name": meta.get("name", gz.name.removesuffix(".xyz.gz")),
                "description": meta.get("description", ""),
                "date": meta.get("date", ""),
                "size": gz.stat().st_size,
                "url": f"content/{gz.name}",
                "method": meta.get("method", ""),
            }
        )

    INDEX.write_text(json.dumps({"items": items}, indent=2) + "\n")
    print(f"index.json: {len(items)} dataset(s)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("xyz", nargs="?", type=Path, help=".xyz file to publish")
    parser.add_argument("--name", help="dataset name shown in the app")
    parser.add_argument("--description", default="", help="short description")
    parser.add_argument("--method", default="", help="e.g. DFT, CCSD(T)")
    parser.add_argument("--reindex", action="store_true", help="only regenerate index.json")
    args = parser.parse_args()

    if args.xyz:
        add_dataset(args.xyz, args.name or args.xyz.stem, args.description, args.method)
    elif not args.reindex:
        parser.error("provide an .xyz file or --reindex")

    reindex()


if __name__ == "__main__":
    main()
