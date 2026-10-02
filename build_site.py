#!/usr/bin/env python3
"""Build the GitHub Pages site: gzip raw/*.xyz and generate index.json.

Runs automatically in CI (.github/workflows/publish.yml) — contributors only
commit .xyz files to raw/. Optional metadata sidecar raw/<stem>.json:

    { "name": "Display Name", "description": "...", "method": "DFT" }

raw/md/ holds systems for the interactive MD server instead: a structure in
any format ASE reads (.xyz/.extxyz, .traj, .cif, .vasp/POSCAR, .pdb), whose
sidecar may add an "md" block with the server's settings for it, e.g.

    { "name": "CO on Cu(111)", "method": "MACE-MP",
      "md": { "calculator": "mace-mp", "temperature": 300, "fix_below": 9.0 } }

Constraints travel in the structure itself (extxyz move_mask, .traj, POSCAR
selective dynamics) or come from "fix" / "fix_below" in the md block.

Defaults: name = file stem, empty description/method, date = the file's last
git commit date (stable, so device caches are only invalidated when the data
actually changes). Gzip runs with mtime=0 for byte-identical rebuilds.
"""

import gzip
import json
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "raw"
SITE = ROOT / "_site"


def git_date(path: Path) -> str:
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", str(path)],
            capture_output=True, text=True, cwd=ROOT, check=True,
        ).stdout.strip()
        if out:
            return out
    except Exception:
        pass
    return date.today().isoformat()


def safe_name(name: str) -> str:
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in name)


# Structure formats the MD server can read (via ase.io.read).
MD_SUFFIXES = {".xyz", ".extxyz", ".traj", ".cif", ".vasp", ".pdb"}
MD_NAMES = {"POSCAR", "CONTCAR"}


def is_md_structure(path: Path) -> bool:
    return path.is_file() and (path.suffix.lower() in MD_SUFFIXES or path.name in MD_NAMES)


def build_dataset(xyz: Path, category: str, items: list) -> None:
    meta = {}
    sidecar = xyz.with_suffix(".json") if xyz.suffix else xyz.with_name(xyz.name + ".json")
    if sidecar.exists():
        meta = json.loads(sidecar.read_text())

    name = meta.get("name", xyz.stem)
    out_dir = SITE / "content" / category
    out_dir.mkdir(parents=True, exist_ok=True)
    # Keep the structure's own extension (the MD server picks the ASE
    # reader from it); grids are always .xyz.
    extension = (xyz.suffix.lower() or ".vasp") if category == "md" else ".xyz"
    gz_path = out_dir / (safe_name(name) + extension + ".gz")
    with open(xyz, "rb") as src, open(gz_path, "wb") as out_file:
        with gzip.GzipFile(fileobj=out_file, mode="wb", compresslevel=9, mtime=0) as dst:
            shutil.copyfileobj(src, dst)

    item = {
        "name": name,
        "description": meta.get("description", ""),
        "date": git_date(xyz),
        "size": gz_path.stat().st_size,
        "url": f"content/{category}/{gz_path.name}",
        "method": meta.get("method", ""),
        "category": category,
    }
    if category == "md":
        item["format"] = extension.lstrip(".")
        item["md"] = meta.get("md", {})
    items.append(item)
    print(f"[{category}] {xyz.name} -> {gz_path.name} ({gz_path.stat().st_size / 1e6:.1f} MB)")


def main() -> None:
    items = []

    # Category subfolders (raw/pes, raw/stm, ...) set the entry category.
    for category_dir in sorted(d for d in RAW.iterdir() if d.is_dir()):
        if category_dir.name == "md":
            files = sorted(f for f in category_dir.iterdir() if is_md_structure(f))
        else:
            files = sorted(category_dir.glob("*.xyz"))
        for path in files:
            build_dataset(path, category_dir.name, items)

    # Files directly in raw/ default to the PES category.
    for xyz in sorted(RAW.glob("*.xyz")):
        build_dataset(xyz, "pes", items)

    (SITE / "index.json").write_text(json.dumps({"items": items}, indent=2) + "\n")
    print(f"index.json: {len(items)} dataset(s)")

    if not items:
        print("warning: no .xyz files found in raw/", file=sys.stderr)


if __name__ == "__main__":
    main()
