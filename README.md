[![Pytest](https://github.com/PyEllips/pyElli/actions/workflows/pytest.yml/badge.svg)](https://github.com/PyEllips/pyElli/actions/workflows/pytest.yml) [![Documentation Status](https://readthedocs.org/projects/pyelli/badge/?version=latest)](https://pyelli.readthedocs.io/en/latest/?badge=latest) [![PyPI](https://img.shields.io/pypi/v/pyElli)](https://pypi.org/project/pyElli/) [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.5702469.svg)](https://doi.org/10.5281/zenodo.5702469)

# pyElli

PyElli is an open source numerical solver for spectral ellipsometry employing well-known 2x2 and 4x4 algorithms.
It is intended for a broad case of problems including simple fitting of layered structures, anisotropic layers and any other light interaction with layered 1D structures.
It serves as a system for the day to day ellipsometry task at hand and is easily extendable with your own dispersion models, EMAs or solvers.
Our goal is to provide a reproducible and flexible tool for the needs
of scientists working with spectral ellipsometry.

## Features

- A multitude of models to approximate the dielectric function of your material.
- Build up your structure easily from materials and layers.
- Simulate reflection and transmission spectra, ellipsometric parameters and Mueller matrices.
- Utilities to quickly convert, plot and fit your measurement data.
- Powerful when necessary, editable and expandable.

## How to get it

The installers for all releases are available at the [Python Package Index (PyPI)](https://pypi.org/project/pyElli/).

To install run:

```sh
pip install pyElli
```

A complete environment for pyElli is also available as a [Docker Container](https://hub.docker.com/r/domna/pyelli).
To pull and run it directly just execute

```sh
docker run -p 8888:8888 domna/pyelli
```

from your local docker install. After startup a link should
appear in your console. Click it and you will be directed
to a jupyter server with the latest release of pyElli available.

To install the latest development version use:

```sh
pip install git+https://github.com/PyEllips/pyElli.git
```

The source code is hosted on [GitHub](https://github.com/PyEllips/pyElli), to manually install from source, clone the repository and run `pip install -e .` in
the folder to install it in development mode:

```sh
git clone https://github.com/PyEllips/pyElli
cd pyElli
pip install -e .
```

## Acknowledgements

- Based on Olivier Castany's [Berreman4x4](https://github.com/Berreman4x4/Berreman4x4)
- Solver2x2 based on Steve Byrnes's [tmm](https://github.com/sbyrnes321/tmm)