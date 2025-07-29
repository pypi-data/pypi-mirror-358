# Martini Templates

Martini Templates is a Python package that provides a CLI for generating Martini MDP files with sensible defaults. It uses Jinja2 templates to create MDP files for molecular dynamics simulations, allowing users to customize parameters and generate files for different simulation types.

## Features

- Generate MDP files for NVT, NPT, and energy minimization simulations.
- Override default values for reference temperature (`ref_t`) and pressure (`ref_p`).
- Create all simulation files at once using the `--all` flag.
- Customizable output filenames.

## Installation

Ensure Python 3.10 or higher is installed, then install the package using:

```bash
pip install .
```

## Usage

Run the CLI tool to generate MDP files:

```bash
martini-templates [options]
```

### Options

- `--nvt`: Generate an NVT file (20 ns, no pressure coupling).
- `--npt`: Generate an NPT file (50 ns, pressure coupling).
- `--em`: Generate an energy minimization file.
- `--all`: Generate all files (NVT, NPT, EM).
- `--ref_t`: Set the reference temperature (default: 298 K).
- `--ref_p`: Set the reference pressure (default: 1 bar).
- `--output`: Specify a custom output filename (overrides default naming).

### Examples

Generate an NVT file with default settings:

```bash
martini-templates --nvt
```

Generate an NPT file with a custom temperature and pressure:

```bash
martini-templates --npt --ref_t 310 --ref_p 1.5
```

Generate all files:

```bash
martini-templates --all
```

### Recommended Usage with `uvx`

For better CLI experience and command management, it is recommended to use `uvx`:

```bash
uvx martini-templates --nvt
```

## License

This project is licensed under the MIT License.
