# Tablegen

LAMMPS potential table generator for [LAMMPS](https://lammps.sandia.gov), developed by Vasilii Maksimov.

**Tablegen** is a command-line utility for generating two-body and three-body potential tables for use with LAMMPS simulations. It supports several interaction models commonly used in materials science and glass chemistry, including:

- SHIK potential (Buckingham + Wolf summation)
- Classical Buckingham potential
- Extended Buckingham potential with softening
- Truncated harmonic three-body interactions

## 🔧 Features

- Command-line interface with `argparse`-based subcommands
- Supports plotting potential curves with `matplotlib`
- Generates `.table` and `.3b` files directly usable in LAMMPS
- Fully modular: new potentials can be added as new handler classes
- Handles numeric precision using `mpmath`
- Actively developed for materials modeling workflows

## 📦 Installation

### Install from PyPI (preferred)

Once the package is published on PyPI you can install the latest stable release with:

```bash
pip install tablegen
```

### Install directly from GitHub (bleeding‑edge)

If you need the most recent commit:

```bash
pip install git+https://github.com/superde1fin/tablegen.git
```

### Clone & install locally

For local experimentation or contributing:

```bash
git clone https://github.com/superde1fin/tablegen.git
cd tablegen

# Standard install (no dev extras)
pip install .

# OR editable install (auto‑reload while editing)
pip install -e .
```

> **Tip :** add the `[dev]` extra to pull in testing, type‑checking, and release tools:
>
> ```bash
> pip install .[dev]
> ```
>
> This installs `pytest`, `ruff`, `mypy`, `twine`, and other developer utilities declared in **pyproject.toml**.

*Requires Python ≥ 3.9 and a working C/Fortran toolchain if installing `numpy` from source.*

## 🥪 Usage

After installation, invoke the CLI with:

```bash
tablegen [subcommand] [options]
```

### Available subcommands:

- `shik`: Generate two-body tables using the SHIK potential
- `buck`: Generate tables using the standard Buckingham potential
- `buck_ext`: Use the extended Buckingham potential with softened short-range repulsion
- `3b_trunc`: Generate three-body truncated harmonic tables

### Example usage:

```bash
tablegen shik structure_file.lmp Si O -t SHIK.table -p
```

```bash
tablegen buck Na-O Si-O -c 10 -d 5000 -t buck.table -p -10 10
```

## 📚 Documentation

All subcommands support `-h` or `--help` flags for detailed usage:

```bash
tablegen shik --help
```

## 🧠 Design Overview

The project is modular:

- `cli.py`: Main entry point, defines CLI and parses arguments
- `handlers/`: Contains one handler class per potential type (`SHIK`, `BUCK`, etc.)
- `constants.py`: Shared constants (e.g., cutoffs, physical constants, default coefficients)
- `__init__.py`: Exposes handler classes and version metadata
- `pyproject.toml`: Build and dependency metadata

Each handler:
- Parses user-provided arguments
- Validates species/pair/triplet input
- Prompts for coefficients
- Provides `eval_force` and `eval_pot` methods used by `two_body()` or `three_body()`

## 📈 Plotting

If the `--plot` option is passed, `matplotlib` will be used to visualize the potential curves for the specified pairs or triplets.

## 🥪 Development

Install dev dependencies:

```bash
pip install .[dev]
```

Run tests:

```bash
pytest
```

## 🔖 License

GNU General Public License v3.0 (GPLv3). See [`LICENSE`](LICENSE) for details.

## 👤 Author

Vasilii Maksimov  
University of North Texas  
✉️ VasiliiMaksimov@my.unt.edu

## 🌐 Links

- 🔬 [LAMMPS Official Site](https://lammps.sandia.gov)
- 📆 [PyPI Page (coming soon)](https://pypi.org/project/tablegen)
- 🐙 [GitHub Repository](https://github.com/superde1fin/tablegen)

