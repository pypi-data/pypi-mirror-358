# DMQCLib

The *DMQCLib* package offers helper functions and classes that simplify model building and evaluation for the *AIQC* project.

## Package Manager
You can create a new environment using any package management system, such as *conda* and *mamba*. 

Additionally, using *uv* is recommended when contributing modifications to the package.

 - uv (https://docs.astral.sh/uv/)

After the installation of *uv*, running `uv sync` inside the project will create the environment.

### Example of Environment Setup
For example, the following commands create a new *conda* environment with *mamba* and set up the library environment with *uv*:
```bash
mamba create -n aiqc -c conda-forge python=3.12
mamba activate aiqc
mamba install uv

cd /your/path/to/dmqclib
uv sync
```

## Unit Test
You may need to install the library in editable mode at least once before running unit tests.

```bash
uv pip install -e .
```

After the library installation, you can run unit tests with *pytest*.

```bash
uv run pytest -v
```

## Python Linter
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


## Code Formatter
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

