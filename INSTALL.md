tyssue is a pure python package, installed with `pip`. No compiler toolchain is required.

Conda packaging is no longer maintained; the conda-forge `tyssue` package is frozen
at the last upstream release and does not track this project.

## Install tyssue using pip

```sh
python -m pip install --upgrade tyssue
```

Optional extras:

```sh
python -m pip install "tyssue[viz]"   # ipyvolume, pythreejs, vispy, jupyter
python -m pip install "tyssue[zarr]"  # zarr + xarray, for tyssue.io.zarr
```

## ImageMagick (only for gif export)

`create_gif` and `create_gif_3d` shell out to [ImageMagick](https://imagemagick.org),
which is a system binary, not a Python package, and so is not installed by pip:

| Platform | Command |
| --- | --- |
| macOS | `brew install imagemagick` |
| Debian/Ubuntu | `sudo apt install imagemagick` |
| Windows | [installer](https://imagemagick.org/script/download.php#windows) |

## Installing from source

### Download and install `tyssue` from source

Clone the repository:

```bash
git clone https://github.com/vivarium-collective/tyssue.git
cd tyssue
```

Create a virtual environment and install in editable mode with the dev extras:

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
python -m pip install -e ".[dev]"
```

All runtime dependencies are declared in `pyproject.toml`, so pip resolves them
for you.

If all went well, you have successfully installed tyssue.

### Running the tests

The `dev` extra installs pytest and nbval. A `Makefile` provides shortcuts:

```sh
make test      # run the test suite
make coverage  # run the tests with coverage
make flake8    # check PEP8 on the code
make nbtest    # run the tutorial notebooks with nbval
```

### Building the documentation

The documentation is a [Jupyter Book](https://jupyterbook.org) (version 1.x)
in `doc/`. The tutorial notebooks in `doc/notebooks` are executed at each
build, so ImageMagick is needed:

```sh
python -m pip install -e ".[docs,viz,zarr]"
make docs      # jupyter-book build doc/
```

The HTML pages are written to `doc/_build/html`.
