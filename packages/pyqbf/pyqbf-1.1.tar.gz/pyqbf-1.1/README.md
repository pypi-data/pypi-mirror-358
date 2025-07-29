PyQBF
=====

Bringing the world of QBF to Python.

Checkout with PyPI
------------------
    pip install pyqbf

Checkout with GitLab
--------------------
    git clone ... --recursive 

or, if you already cloned the project:

    git submodule update --init --recursive


Setup
-----
For a complete setup guide, check out our [setup documentation](https://qbf.pages.sai.jku.at/pyqbf/manual/install.html).
For a quick setup, execute the following:
```
pip install --user git+https://gitlab.sai.jku.at/qbf/pyqbf.git
```


Implementation Notes
--------------------

We expose some common operations (solving, certificate handling,
pre-processing) to Python using an IPASIR-like interface, similar to the way
[PySAT](https://pysathq.github.io/) exposes SAT tools to Python. We use
[CMake](https://cmake.org/cmake/help/latest/module/FetchContent.html) to fetch
and build external projects and
[nanobind](https://nanobind.readthedocs.io/en/latest/index.html) to bind them
to Python. We bundle as many dependencies as possible inside this Git
repository using [Git LFS](https://git-lfs.com/), as long as a tool's license
allows redistribution, to guard against issues with external sources.

![overview.png](overview.png)