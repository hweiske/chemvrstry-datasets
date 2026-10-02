# CHEMVRSTRY Datasets

Public potential energy surface (PES) datasets for the
[CHEMVRSTRY](https://github.com/hweiske/chemvrstry) VR visualization app.

## Publishing a dataset — just push it

```bash
cp my_surface.xyz raw/pes/    # or raw/stm/ for STM images
git add raw/ && git commit -m "Add my_surface" && git push
```

The folder sets the dataset's category — the app's PES mode lists
`raw/pes/`, STM mode lists `raw/stm/` (files directly in `raw/` count as
PES). Both categories share the same extended-XYZ grid format.

That's everything. A GitHub Action compresses the file, regenerates the
dataset index, and deploys to GitHub Pages — the dataset appears in the app
on every device a minute or two later. Updating a dataset is the same
(commit a new version of the file); removing one is `git rm`.

Optionally add a metadata sidecar `raw/my_surface.json` for a nicer display
name:

```json
{ "name": "CO on Ni(111)", "description": "2D scan", "method": "DFT/PBE" }
```

Without it, the filename is used and description/method stay empty.

## MD systems — `raw/md/`

Structures for the interactive MD server (Dynamics mode): any format ASE
reads — `.xyz`/`.extxyz`, `.traj`, `.cif`, `.vasp`/`POSCAR`, `.pdb`. The
server lists them in the app's **MD Setup** panel; picking one loads it for
everyone connected. A sidecar `raw/md/<stem>.json` names it and can carry
the server's settings for it:

```json
{ "name": "CO on Cu(111)", "description": "bottom two layers fixed",
  "method": "MACE-MP",
  "md": { "calculator": "mace-mp", "model": "medium", "temperature": 300,
          "timestep": 0.5, "friction": 0.01, "vacuum": 4.0,
          "fix": [0, 1, 2], "fix_below": 9.0 } }
```

`calculator`: `auto` (default — MACE-OFF for organic molecules, MACE-MP for
everything else or anything periodic), `mace-off`, `mace-mp`, `emt`. Every
setting except the structure can also be changed in the app while it runs.

**Constraints are kept.** Whatever ASE reads from the file is applied in the
simulation and shown in the app (fixed atoms are drawn dark and can't be
grabbed): `move_mask` in extended XYZ (write it with
`write(f, atoms, format="extxyz", columns=["symbols", "positions", "move_mask"])`),
any constraint in `.traj`, selective dynamics in `POSCAR`. CIF and plain XYZ
carry none — use `fix` (atom indices) or `fix_below` (fix every atom whose z
is below this, in Å) in the sidecar instead.

Large trajectories are stored via **Git LFS** (`raw/*.xyz` is tracked
automatically by `.gitattributes`) — run `git lfs install` once on your
machine before your first push, and clone with LFS available to get real
files instead of pointers.

## Format

Extended XYZ with grid metadata per block (`i:`/`j:` indices, `E:` energy in
Hartree) — see the CHEMVRSTRY README for the full specification.

## How it works

- `raw/*.xyz` — the datasets, versioned as plain files (single source of truth)
- `build_site.py` — CI build: gzip (deterministic) + `index.json` generation;
  dataset dates come from git history, so device caches only invalidate when
  a file actually changes
- `.github/workflows/publish.yml` — runs the build on every push to `main`
  and deploys to Pages

The app fetches:
`https://hweiske.github.io/chemvrstry-datasets/index.json`
