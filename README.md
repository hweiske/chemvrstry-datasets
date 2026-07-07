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
