.. _getting_started:

***************
Getting Started
***************

To install qualpipe package we recommend to create and activate an isolated virtual environment with Python >= 3.10. This can be achieved via *conda* or *mamba* commands:

.. code-block:: shell

    mamba create -n qualpipe -c conda-forge python==3.12 ctapipe
    mamba activate qualpipe

Follow then the installation instructions for :ref:`users <users>` or for :ref:`developers <developers>` to install the package and all its dependencies.

.. _users:

Installation for *users*
=================================

qualpipe package is under active development and has not been published on PyPi yet, but it can still be installed using `pip <https://pypi.org/project/pip/>`_ directly accessing the official GitLab repository:

.. code-block:: shell

    pip install git+https://gitlab.cta-observatory.org/cta-computing/dpps/qualpipe/qualpipe

After the first tagged release and deployment on PyPi (or TestPyPi) it will be possible to install QualPipe using the following command:

.. code-block:: shell

    pip install --extra-index-url https://test.pypi.org/simple/ qualpipe

.. **Note**: to install a specific version of `qualpipe` take a look at :ref:`version`.

.. _developers:

Installation for *developers*
=============================

First, clone the source code from GitLab:

.. code-block:: shell

    git clone https://gitlab.cta-observatory.org/cta-computing/dpps/qualpipe/qualpipe.git
    cd qualpipe

Then perform an editable installation with ``pip`` to include documentation and testing dependencies:

.. code-block:: shell

    pip install -e .[all]

We are using the ``pre-commit``, ``code-spell`` and ``ruff`` tools for automatic adherence to the code style. To enforce running these tools whenever you make a commit, setup the `pre-commit hook <https://pre-commit.com/>`_ executing:

.. code-block:: shell

    pre-commit install

The *pre-commit hook* will then execute the tools with the same settings as when a merge request is checked on GitLab, and if any problems are reported the commit will be rejected. You then have to fix the reported issues before tying to commit again.

.. _running_tests:

Running Tests
=============

The tests can be launched manually or in CI (recommended). For some tests, test files might be necessary. Please contact the maintainers to obtain them (if needed).

Tests are located in the folder ``./src/qualpipe/tests/``. The unit tests can be run with `pytest <https://pypi.org/project/pytest>`_ either through automatic search or providing a specific file, folder, mark, etc. To run all tests use ``pytest`` at any level of ``./src/qualpipe/tests/``.

.. .. _version:

.. How To Get a Specific Version
.. =============================

.. To install a specific version of ``qualpipe`` (e.g. version ``0.2.0``) you can use the following command:

.. .. code-block:: shell

..    $ mamba install -c conda-forge qualpipe=0.2.0

.. or with pip:

.. .. code-block:: shell

..    $ pip install qualpipe==0.2.0
