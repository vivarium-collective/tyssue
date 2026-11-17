# tyssue

The `tyssue` library provides a unified interface to implement
biomechanical models of living tissues. Its main focus is on **vertex based
epithelium models**, in 2D, on curved apical sheets, and in 3D monolayers.

![tyssue banner](illus/banner.png)

## Install

tyssue is a pure Python package:

```bash
python -m pip install --upgrade tyssue
```

Optional extras: `tyssue[viz]` for 3D and interactive visualisation
(ipyvolume, vispy) and `tyssue[zarr]` for zarr files. Gif export needs
[ImageMagick](https://imagemagick.org). See {doc}`install` for details.

## Design

- **Data in DataFrames.** An epithelium is a set of `pandas` DataFrames
  (`vert_df`, `edge_df`, `face_df`, `cell_df`) on a half-edge mesh, plus
  nested dictionaries of specifications.
- **Separate structure, geometry and models.** The same mesh can be fed to
  different geometry classes and physical models, and models are assembled
  from independent effectors by a model factory.
- **Solvers and events.** A quasi-static solver finds energy minima; a
  viscous (Euler) solver integrates the dynamics in time and runs biological
  events (division, apoptosis, rearrangements...) through an event manager.

Start with the {doc}`notebooks/00-Basic_Usage` tutorial, or browse the API
reference.

## What's new in 2.0

- **Pure Python**: CGAL is no longer a dependency.
- **Type 3 transitions** merge free tissue borders ({doc}`notebooks/E-T3Transitions`).
  The removal of small triangles is now called a type 2 transition (`with_t2`).
- **Different results**: unit edge vectors were computed from outdated edge
  lengths, which changed line tension and contractility forces.
- **Tubes and vessels**: `CylinderGeometry`, `VesselGeometry` and their model
  factories, active migration, and fixed-border models
  ({doc}`notebooks/F-CylinderVesselMigration`).
- **Intersection detection** of folded and overlapping faces, and events
  added to the current step with `EventManager.append_current`.
- **Faster** sheet simulations.

See the {doc}`changelog` for the full list.

## Citing tyssue

tyssue is published in the Journal of Open Source Software:
[doi:10.21105/joss.02973](https://doi.org/10.21105/joss.02973).

Source code: [vivarium-collective/tyssue](https://github.com/vivarium-collective/tyssue),
a fork of [DamCB/tyssue](https://github.com/DamCB/tyssue) developed with the
agreement of the original authors.
