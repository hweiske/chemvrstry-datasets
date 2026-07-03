# OpenAvatar Datasets

Public potential energy surface (PES) datasets for the
[OpenAvatar](https://github.com/hweiske/open-avatar) VR visualization app,
served via GitHub Pages.

- `index.json` — dataset listing the app fetches (`{ "items": [...] }`)
- `content/*.xyz.gz` — gzipped extended-XYZ energy grids

## Publishing a dataset

```bash
./publish.py my_surface.xyz --name "CCH" --description "C2H+ reaction surface" --method DFT
git add -A && git commit -m "Add CCH dataset" && git push
```

The app's `listUrl` points at:
`https://hweiske.github.io/open-avatar-datasets/index.json`
