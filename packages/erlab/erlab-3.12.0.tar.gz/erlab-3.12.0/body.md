## v3.12.0 (2025-06-29)

### ✨ Features

- **io:** allow loading single-wave `.itx` files using `xarray.open_dataarray` ([c5a0d59](https://github.com/kmnhan/erlabpy/commit/c5a0d5972941b5db165277f232162ee9a855e2fe))

- **imagetool:** allow more color options to be passed to the ImageTool constructor ([983b7ab](https://github.com/kmnhan/erlabpy/commit/983b7ab78436fd0779ab190dd10ffd34b1bdb471))

  Adds boolean flag `high_contrast` and numbers `vmin` and `vmax` to the ImageTool constructor.

- **imagetool.manager:** add duplicate functionality ([f635236](https://github.com/kmnhan/erlabpy/commit/f635236a67549d3e6ebc30d084babcfc4cc3df00))

  ImageTool windows in the manager can now be duplicated from the right-click context menu.

- **imagetool.manager:** replace data in existing ImageTool manager windows ([a86b64b](https://github.com/kmnhan/erlabpy/commit/a86b64b0616b811698cf17f5fff7897ca748d24a))

  Adds a new function `erlab.interactive.imagetool.manager.replace_data` that allows replacing the data in existing ImageTool manager windows. Also adds a new argument `replace` to the `itool` function which takes a list of indexes of existing ImageTool manager windows to replace their data.

- **io.dataloader:** add new method `pre_combine_multiple` method for data pre-processing ([91b7455](https://github.com/kmnhan/erlabpy/commit/91b745510ba6307d5f9c244b1aa971a98ed53622))

  Adds a new method `pre_combine_multiple` to the `DataLoader` class that allows pre-processing multiple data files prior to combining them.

### 🐞 Bug Fixes

- **analysis.tranform.symmetrize:** fix subtract behavior to produce properly antisymmetrized output (#150) ([b00625c](https://github.com/kmnhan/erlabpy/commit/b00625cf253a77719a5c2d89c32805e4ff223f00))

- **goldtool:** fix potential segfault by copying instead of supplying a pointer ([5e3a812](https://github.com/kmnhan/erlabpy/commit/5e3a812480e9f212ab1b17ec131ce7dfe26d3fdf))

- **imagetool.manager:** do not override recent directory and loader name for already open data explorer ([e82c73b](https://github.com/kmnhan/erlabpy/commit/e82c73ba956cf0715dfbf20a3a221d3f46b132a7))

- **imagetool:** preserve color levels when reloading compatible data ([5948c56](https://github.com/kmnhan/erlabpy/commit/5948c56c496b9e63a129fab9a09ccd5172705c73))

- **imagetool:** keep color related settings when opening in new window from existing tool ([96dfa7a](https://github.com/kmnhan/erlabpy/commit/96dfa7a2802e0f3d74912e73b7220829cde1fc33))

- **imagetool:** keep visible colorbar on unarchive or reload ([1f3af1c](https://github.com/kmnhan/erlabpy/commit/1f3af1ceebdc660c0afcff5269426303985223e0))

- **imagetool.manager:** fix tools not showing on windows ([4e8f8a8](https://github.com/kmnhan/erlabpy/commit/4e8f8a8bed33a202bf792c559632d378120390f4))

- **io.plugins.merlin:** fix broken energy axis while concatenating non-dither mode motor scans ([861e68f](https://github.com/kmnhan/erlabpy/commit/861e68f696192062a81b9f7ce25a023ed8fcc77f))

- **analysis.fit.models:** allow StepEdgeModel to be used in composite models ([77fb4e6](https://github.com/kmnhan/erlabpy/commit/77fb4e6c076b635d99973cbe2e3e6609a0269aab))

### ♻️ Code Refactor

- **imagetool.manager:** improve server connection handling ([7989b5d](https://github.com/kmnhan/erlabpy/commit/7989b5dd76513b575dfa32fec2068ae1d23f61d6))

[main e77180d] bump: version 3.11.1 → 3.12.0
 3 files changed, 3 insertions(+), 3 deletions(-)

