# tyssue : An epithelium simulation library

![A nice banner](doc/illus/banner.png)

<hr/>

| Version | Downloads | Python |
| --- | --- | --- |
| [![PyPI version](https://img.shields.io/pypi/v/tyssue.svg)](https://pypi.org/project/tyssue/) | [![PyPI downloads](https://img.shields.io/pypi/dm/tyssue.svg)](https://pypi.org/project/tyssue/) | [![Python versions](https://img.shields.io/pypi/pyversions/tyssue.svg)](https://pypi.org/project/tyssue/) |

| Tests | Doc | CHAT |
| --- | --- | --- |
| [![Tests](https://github.com/vivarium-collective/tyssue/actions/workflows/tests.yml/badge.svg)](https://github.com/vivarium-collective/tyssue/actions/workflows/tests.yml) | [![Doc Status](https://readthedocs.org/projects/tyssue/badge/?version=latest)](https://tyssue.readthedocs.io/en/latest/) |  [![Join the chat at https://gitter.im/DamCB/tyssue](https://badges.gitter.im/DamCB/tyssue.svg)](https://gitter.im/DamCB/tyssue?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge) |

The `tyssue` library seeks to provide a unified interface to implement
biomechanical models of living tissues.
Its main focus is on **vertex based epithelium models**.

## Install

tyssue is a pure Python package (Python 3.10 or later), installed from PyPI:

```bash
python -m pip install --upgrade tyssue
```

### Optional extras

```bash
python -m pip install "tyssue[viz]"   # 3D and interactive visualisation (ipyvolume, vispy)
python -m pip install "tyssue[zarr]"  # zarr file support
```

The base install is enough to run simulations and to draw with matplotlib.

### Writing gifs

`create_gif` and `create_gif_3d` use [ImageMagick](https://imagemagick.org),
which is not a Python package and has to be installed separately:

| Platform | Command |
| --- | --- |
| macOS | `brew install imagemagick` |
| Debian/Ubuntu | `sudo apt install imagemagick` |
| Windows | [installer](https://imagemagick.org/script/download.php#windows) |

### From source

```bash
git clone https://github.com/vivarium-collective/tyssue.git
cd tyssue
python -m pip install -e ".[dev]"
```

See [INSTALL.md](INSTALL.md) for running the tests and building the documentation.

## Getting started

```python
## Core object
from tyssue import Sheet
## Simple 2D geometry
from tyssue import PlanarGeometry
## Visualisation (matplotlib based)
from tyssue.draw import sheet_view

sheet = Sheet.planar_sheet_2d('basic2D', nx=6, ny=7,
                              distx=1, disty=1)
PlanarGeometry.update_all(sheet)
sheet.sanitize()
fig, ax = sheet_view(sheet)
```

## Documentation

The documentation at [tyssue.readthedocs.io](https://tyssue.readthedocs.io) has:

* **Tutorials**, from basic usage, geometry and visualisation to solvers,
  rearrangements, cell division, the event manager, type 3 transitions, and
  tubes, vessels and active migration. The notebooks are also in
  [doc/notebooks](doc/notebooks).
* The **API reference** for every module.
* The [changelog](changelog.md).

The [tissue closure notebook](notebooks/tissue_closure_demo.ipynb) shows
lateral-face fusion and apical-constriction lift on monolayers.

## What can you simulate?

* **Tissues**: 2D sheets (`Sheet`, also with holes or periodic boundaries),
  2D lateral sheets (`LateralSheet`), 3D apical sheets (flat, closed,
  ellipsoid, cylinder and vessel shaped), and 3D monolayers and bulk tissues
  (`Monolayer`).
* **Mechanics**: build a model from effectors (area, volume, perimeter and
  length elasticity, line tension, contractility, surface tension, radial
  tension, chiral torque, active migration and more) with `model_factory`.
  Variants hold the tissue border in place: `model_factory_cylinder` and
  `model_factory_vessel` for tubes, `model_factory_bound` for a tissue with
  fixed borders.
* **Solvers**: `QSSolver` finds the quasi-static (minimum energy) state;
  `EulerSolver` runs overdamped dynamics in time and records a `History`.
* **Topology changes**: type 1 transitions (neighbour exchange), type 2
  transitions (removal of small triangular cells), type 3 transitions (a border
  vertex joining the free edge of a neighbouring cell, `EulerSolver(..., with_t3=True)`),
  cell division, apoptosis and delamination.
* **Behaviours**: schedule events with an `EventManager`. `append` queues an
  event for the next step and `append_current` for the current one. An event
  that is already queued with the same arguments is not added twice, unless
  you pass `unique=False`.
* **Tissue closure**: fuse the facing lateral walls of two monolayer fronts
  into one continuous epithelium (`lumen_closure` and `fuse` behaviours).
* **Folding and overlap checks**: `check_intersections` reports cells that
  fold over themselves or overlap during a simulation.
* **Input and output**: HDF5 histories, Zarr (with the `zarr` extra), and mesh
  export through `meshio`.

## Upgrading from tyssue 1.x

* **Results differ slightly.** Unit edge vectors were computed from outdated
  edge lengths, which changed line tension and contractility forces, most of
  all on short edges.
* **Type 2 and type 3 transitions.** The removal of small triangular cells,
  previously called a type 3 transition, is now the type 2 transition:
  use `with_t2=` (`QSSolver`, `all_rearangements`, `single_rearangement`) and
  `auto_t2`. The old names still work, with a warning. `EulerSolver(with_t3=True)`
  enables the new type 3 transition.
* **`ActiveMigration`** reads each cell's direction from the face columns
  `mx`, `my` (and `mz`), and splits the cell's force between its vertices.
* **Removed**: the collision solvers (use `check_intersections` or
  `tyssue.collisions.intersections` to detect folds and overlaps), and the
  `EulerSolverDivision` / `EulerSolverDiv` solvers (use a division event with
  `EulerSolver`). `CylinderGeometryInit` is now `CylinderGeometry`.

The [changelog](changelog.md) lists every change.

## Overview

### What kind of Models does it implement?

The first model implemented is the one described in
Monier et al.<sup id="a1">[1](#f1)</sup>. It is an example of a vertex model,
where the interactions are only evaluated on the apical surface sheet
of the epithelium. The second class of models is still at an early
stage. They implement a description of the tissue's rheology, within a
dissipation function formalism.

![The two models considered](doc/illus/two_models.png)

### What kind of geometry does it model ?
`tyssue` allows to model different geometries in 2D and in 3D.  Presentation of the different geometries and how to create them are shown in this [notebook](doc/notebooks/01-Geometry.ipynb).
<p align="center">
 <img src="doc/illus/geometry.png" width="500">
</p>

### General Structure of the modeling API

#### Design principles

> [APIs not apps](https://opensource.com/education/15/9/apis-not-apps)

Each biological question, be it in morphogenesis or cancer studies is
unique, and requires tweeking of the models developed by the
physicists. Most of the modelling software follow an architecture
based on a core C++ engine with a combinaison of markup or scripting
capacities to run specific simulation.

In `tyssue`, we rather try to expose an API that simplifies the
building of tissue models and running simulations, while keeping the
possibilities as open as possible.

> Separate structure, geometry and models

We seek to have a design as modular as possible, to allow the same
epithelium mesh to be fed to different physical models.

> Accessible, easy to use data structures

The core of the tyssue library rests on two structures: a set of
`pandas DataFrame` holding the tissue geometry and associated data,
and nested dictionaries holding the model parameters, variables and
default values.

![Tyssue data structure](doc/illus/tyssue_data_management.png)

The API thus defines an `Epithelium` class. An instance of this class
is a container for the datasets and the specifications, and implements
methods to manipulate indexing of the dataframes to ease calculations.

The mesh structure is heavily inspired by
[CGAL Linear Cell Complexes](http://doc.cgal.org/latest/Linear_cell_complex/index.html),
most importantly, in the case of a 2D vertex sheet for example, each
junction edge between the cells is "splited" between two oriented **half
edges**.

## Visualisation
Thanks to @kephale, there is a napari plugin to visualise tyssue simulation output.
You can find it [here](https://github.com/kephale/napari-tyssue).

## About this repository

This repository is a fork of [DamCB/tyssue](https://github.com/DamCB/tyssue),
created by Guillaume Gay, Sophie Theis, Magali Suzanne and the tyssue contributors.
With the agreement of the original authors, tyssue is developed here by the
[vivarium-collective](https://github.com/vivarium-collective), and the `tyssue`
releases on PyPI are built from it starting with version 2.0.

Contributions are welcome: open an issue or a pull request.

### Mailing list:

tyssue@framaliste.org - https://framalistes.org/sympa/info/tyssue

Subscribe ➙ https://framalistes.org/sympa/subscribe/tyssue
Unsubscribe ➙ https://framalistes.org/sympa/sigrequest/tyssue

### Authors

* Bertrand Caré - @bcare
* Cyprien Gay - @cypriengay
* Guillaume Gay - @glyg
* Hadrien Mary - @hadim
* François Molino
* Magali Suzanne
* Sophie Theis - @sophietheis
* Tasnif Rahman (maintainer) - @sniffo

## Dependencies

tyssue is tested on Linux, macOS and Windows with Python 3.10 to 3.13.
<details>
  <summary>Show dependencies</summary>

### Core

- Python >= 3.10
- numpy
- scipy
- pandas
- matplotlib
- networkx
- meshio
- quantities
- scikit-image
- pytables
- ipywidgets

### Visualisation (`tyssue[viz]`)

- ipyvolume
- ipython_genutils
- pythreejs
- vispy
- jupyter
- notebook

### Zarr (`tyssue[zarr]`)

- zarr
- xarray

### Tests (`tyssue[test]`)

- pytest
- pytest-cov
- nbval
- nox

### Documentation (`tyssue[docs]`)

- jupyter-book 1.x
- ipykernel

</details>

## How to cite
If you find `tyssue` useful please cite the original publication and the
[upstream repository](https://github.com/DamCB/tyssue) using its DOI as follows:

> Theis, Suzanne, Gay, (2021). Tyssue: an epithelium simulation library. Journal of Open Source Software, 6(62), 2973 doi:[https://doi.org/10.21105/joss.02973](https://doi.org/10.21105/joss.02973)
>
> Zenodo doi:10.5281/zenodo.4817609

| ZENODO DOI | JOSS DOI |
| --- | --- |
| [![DOI](https://zenodo.org/badge/32533164.svg)](https://zenodo.org/badge/latestdoi/32533164) | [![DOI](https://joss.theoj.org/papers/10.21105/joss.02973/status.svg)](https://doi.org/10.21105/joss.02973) |

## Publications
If `tyssue` has made a substantial contribution to your work, please edit this file and open a PR.

Lou Y, Rupprecht JF, Theis S, Hiraiwa T, and Saunders TE. Curvature-induced cell rearrangements in biological tissues. Phys. Rev. Lett. 2023. doi: [10.1103/PhysRevLett.130.108401](https://doi.org/10.1103/PhysRevLett.130.108401)

Rahman T, Peters F and Wan LQ. Cell Jamming Regulates Epithelial Chiral Morphogenesis. J Biomech. 2023. doi: [10.1016/j.jbiomech.2023.111435](https://doi.org/10.1016/j.jbiomech.2023.111435)

Fiorentino J and Scialdone A. The role of cell geometry and cell-cell communication in gradient sensing. PLoS Comput Biol. 2022 doi: [10.1371/journal.pcbi.1009552](https://doi.org/10.1371/journal.pcbi.1009552)
Related repository: [https://github.com/ScialdoneLab/2DLEGI](https://github.com/ScialdoneLab/2DLEGI)

Courcoubetis G, Xu C, Nuzhdin SV, Haas S. Avalanches during epithelial tissue growth; Uniform Growth and a drosophila eye disc model, PLoS Comput Biol 2022 doi: [10.1371/journal.pcbi.1009952](https://doi.org/10.1371/journal.pcbi.1009952)

Martin E, Theis S, Gay G, Monier B, Rouvière C, Suzanne M. Arp2/3-dependent mechanical control of morphogenetic robustness in an inherently challenging environment. Dev Cell. 2021 doi: [10.1016/j.devcel.2021.01.005](https://doi.org/10.1016/j.devcel.2021.01.005)
Related repository: [https://github.com/suzannelab/polarity](https://github.com/suzannelab/polarity)

Gracia M, Theis S, Proag A, Gay G, Benassayag C, Suzanne M. Mechanical impact of epithelial-mesenchymal transition on epithelial morphogenesis in Drosophila. Nat Commun. 2019 doi: [10.1038/s41467-019-10720-0](https://doi.org/10.1038/s41467-019-10720-0)
Related repository: [https://github.com/suzannelab/invagination](https://github.com/suzannelab/invagination)

Monier B, Gettings M, Gay G, Mangeat T, Schott S, Guarner A, Suzanne M. Apico-basal forces exerted by apoptotic cells drive epithelium folding. Nature. 2015 doi: [10.1038/nature14152](https://doi.org/10.1038/nature14152)
Related repository: [https://github.com/glyg/leg-joint](https://github.com/glyg/leg-joint)

## Licence

Since version 0.3, this project is distributed under the terms of the [General Public Licence](https://www.gnu.org/licenses/gpl.html).

Versions before 0.3 were distributed under the [Mozilla Public Licence](https://www.mozilla.org/en-US/MPL/2.0/).

If GPL licencing is too restrictive for your intended usage, please contact the maintainer.

<hr/>

<b id="f1">1</b> : Monier B, Gettings M, Gay G, Mangeat T, Schott S, Guarner A, Suzanne M. Apico-basal forces exerted by apoptotic cells drive epithelium folding. Nature. 2015 doi: [10.1038/nature14152](https://doi.org/10.1038/nature14152) [↩](#a1)
