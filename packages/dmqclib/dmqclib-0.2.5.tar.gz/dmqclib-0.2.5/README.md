# DMQCLib

![PyPI - Version](https://img.shields.io/pypi/v/dmqclib)
[![Anaconda-Server Badge](https://anaconda.org/takayasaito/dmqclib/badges/version.svg)](https://anaconda.org/takayasaito/dmqclib)
[![Check Package](https://github.com/AIQC-Hub/dmqclib/actions/workflows/check_package.yml/badge.svg)](https://github.com/AIQC-Hub/dmqclib/actions/workflows/check_package.yml)
[![codecov](https://codecov.io/gh/AIQC-Hub/dmqclib/graph/badge.svg?token=N6P5V9KBNJ)](https://codecov.io/gh/AIQC-Hub/dmqclib)
[![CodeFactor](https://www.codefactor.io/repository/github/aiqc-hub/dmqclib/badge)](https://www.codefactor.io/repository/github/aiqc-hub/dmqclib)

The *DMQCLib* package offers helper functions and classes that simplify model building and evaluation for the *AIQC* project.

## Installation
The package is indexed on [PyPI](https://pypi.org/project/dmqclib/) and [Anaconda.org](https://anaconda.org/takayasaito/dmqclib), allowing you to install it using either *pip* or *conda*.

Using *pip*:
```bash
pip install dmqclib
```

Using *conda*:
```bash
conda install takayasaito::dmqclib 
```


## Contribution

### Package Manager
You can create a new environment using any package management system, such as *conda* and *mamba*. 

Additionally, using *uv* is recommended when contributing modifications to the package.

 - [uv](https://docs.astral.sh/uv/)

After the installation of *uv*, running `uv sync` inside the project will create the environment.

#### Example of Environment Setup
For example, the following commands create a new *conda* environment with *mamba* and set up the library environment with *uv*:
```bash
mamba create -n aiqc -c conda-forge python=3.12
mamba activate aiqc
mamba install uv

cd /your/path/to/dmqclib
uv sync
```

### Unit Test
You may need to install the library in editable mode at least once before running unit tests.

```bash
uv pip install -e .
```

After the library installation, you can run unit tests with *pytest*.

```bash
uv run pytest -v
```

### Python Linter
To lint the code under the *src* folder with [ruff](https://astral.sh/ruff), use the following command:

```bash
uvx ruff check src
```

and the unit test code under the *tests* folder:

```bash
uvx ruff check tests
```

Alternatively, to lint the code with [flake8](https://flake8.pycqa.org), use the following command:

```bash
uvx flake8 src --max-line-length=100
```


### Code Formatter
To format the code under the *src* folder with [ruff](https://astral.sh/ruff), use the following command:

```bash
uvx ruff format src
```

and the unit test code under the *tests* folder:

```bash
uvx ruff format tests
```

Alternatively, to format the code with [black](https://pypi.org/project/black/), use the following command:

```bash
uvx black src
```

## Deployment

### Release to PyPI
The GitHub Action (.github/workflows/publish_to_pypi.yaml) automatically publishes the package to [PyPI](https://pypi.org/project/dmqclib/) whenever a GitHub release is created.

Alternatively, you can manually publish the package to PyPI:

```bash
uv build
uv publish --token pypi-xxxx-xxxx-xxxx-xxxx
```

### Release to Anaconda.org

Unlike using a GitHub Action for PyPI, publishing to [Anaconda.org](https://anaconda.org/takayasaito/dmqclib) is a manual process.

You’ll need the following tools:

  - conda-build
  - anaconda-client
  - grayskull

Install them (preferably in a dedicated environment):
```bash
conda install -c conda-forge conda-build anaconda-client grayskull
```

#### 1. Generate the conda recipe with Grayskull

From the project root, run:
```bash

grayskull pypi dmqclib
```

This creates a meta.yaml file in the dmqclib/ directory.

#### 2. Build the package
```bash
cd dmqclib
conda build .
cd ..
```

This creates a .conda package in your local conda-bld directory (e.g., ~/miniconda3/conda-bld/noarch/).

#### 3. Upload to Anaconda.org

```bash
anaconda login
anaconda upload /full/path/to/conda-bld/noarch/dmqclib-<version>-<build>.conda
```

#### 4. Keep the recipe under version control

```bash
cp dmqclib/meta.yaml conda/meta.yaml
rm -r dmqclib
```
