# QualPipe

`QualPipe` is a Python-based automation tool for the
CTAO data quality evaluations.
It leverages the `ctapipe` library to process telescope monitoring data
and applies configurable quality criteria to ensure that
the collected data meets desired standards.


## Features

- Define and apply quality checks to monitoring data based on configuration files.
- Modular and extensible framework for describing and validating data.
- Supports processing with telescope-specific criteria.
- YAML configuration for easy adaptability.

## Installation instructions

The package is under active development. To install QualPipe package we recommend to create and activate an isolated virtual environment with `Python >= 3.10` and `ctapipe`. This can be achieved via [`conda`][conda] or [`mamba`][mamba] commands:

```
mamba create -n qualpipe -c conda-forge python==3.12 ctapipe
mamba activate qualpipe
```

Next, follow the installation instructions for [users](#installation-for-users) or for [developers](#installation-for-developers).

### Installation for *users*

QualPipe has not been published on PyPi yet, but it can be installed using [`pip`][pip]:

```
pip install git+https://gitlab.cta-observatory.org/cta-computing/dpps/qualpipe/qualpipe
```

### Installation for *developers*

First, clone the source code from GitLab:

```
git clone https://gitlab.cta-observatory.org/cta-computing/dpps/qualpipe/qualpipe.git
cd qualpipe
```

Then perform an editable installation with `pip` to include documentation and testing dependencies:

```
pip install -e .[all]
```

We are using `pre-commit`, `code-spell` and `ruff` tools for automatic adherence to the code style. To enforce running these tools whenever you make a commit, setup the [`pre-commit hook`][pre-commit] executing:

```
pre-commit install
```

The `pre-commit hook` will then execute the tools with the same settings as when a merge request is checked on GitLab, and if any problems are reported the commit will be rejected. You then have to fix the reported issues before tying to commit again.


## License

This project is licensed under the BSD 3-Clause License. See the LICENSE file for details.


[conda]:https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html
[mamba]:https://mamba.readthedocs.io/en/latest/installation/mamba-installation.html
[pip]:https://pip.pypa.io/en/stable/
[pre-commit]:https://pre-commit.com/
