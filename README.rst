####################
poetry-bumpversion
####################

| |logo|

The ``poetry version`` command only updates version in ``pyproject.toml`` file.
This plugin updates version in other files when ``poetry version <version>``
command is executed.

|  |build-status| |coverage.io| |pyversions| |pypi-version| |license|

********************
Getting Started
********************

++++++++++++++++++++
Prerequisites
++++++++++++++++++++

- poetry = ^1.2.0a2

++++++++++++++++++++
Install
++++++++++++++++++++

Install the plugin by poetry plugin command.

::

    poetry self add poetry-bumpversion

++++++++++++++++++++++++++++++
Configure version replacements
++++++++++++++++++++++++++++++

Say you have ``__version__`` variable set at ``your_package/__init__.py`` file

.. code:: python

    __version__ = "0.1.0" # It MUST match the version in pyproject.toml file


Add the following to your ``pyproject.toml`` file.

.. code:: toml

    [tool.poetry_bumpversion.file."your_package/__init__.py"]
    # Duplicate the line above to add more files

Now run ``poetry version patch --dry-run``, if your output looks somewhat like below
you are all set (dry-run does not update any file).

::

    Bumping version from 0.5.0 to 0.5.1
    poetry-bumpversion: processed file: your_package/__init__.py

If dry-run output looks fine you can run version update command without dry-run flag to
check if version in both ``pyproject.toml`` and ``your_package/__init__.py`` file has been updated.

********************
Advanced Usage
********************

You can define search and replace terms to be more precise

.. code:: toml

    [tool.poetry_bumpversion.file."your_package/__init__.py"]
    search = '__version__ = "{current_version}"'
    replace = '__version__ = "{new_version}"'

You can define replacements if you have same search/replace patterns
across multiple files.

.. code:: toml

    [[tool.poetry_bumpversion.replacements]]
    files = ["your_package/__init__.py", "your_package/version.py"]
    search = '__version__ = "{current_version}"'
    replace = '__version__ = "{new_version}"'

    [[tool.poetry_bumpversion.replacements]]
    files = ["README.md"]
    search = 'version: {current_version}'
    replace = 'version: {new_version}'

******************************
Usage with Github Workflow
******************************

This plugin uses itself in it's "Deploy to PyPI" workflow. When a release tag is created on
GitHub, the workflow updates package version using the release tag name and deploys it to PyPI.
You can copy the `deploy workflow code`_ to your repository to set it up.

.. _deploy workflow code: https://github.com/monim67/poetry-bumpversion/blob/master/.github/workflows/deploy.yml

********************
License
********************

This project is licensed under MIT License - see the
`LICENSE <https://github.com/monim67/poetry-bumpversion/blob/master/LICENSE>`_ file for details.


.. |logo| image:: https://github.com/monim67/poetry-bumpversion/blob/main/.github/assets/logo.png?raw=true
    :alt: Logo

.. |build-status| image:: https://github.com/monim67/poetry-bumpversion/actions/workflows/build.yml/badge.svg?event=push
    :target: https://github.com/monim67/poetry-bumpversion/actions/workflows/build.yml
    :alt: Build Status
    :height: 20px

.. |coverage.io| image:: https://coveralls.io/repos/github/monim67/poetry-bumpversion/badge.svg
    :target: https://coveralls.io/github/monim67/poetry-bumpversion
    :alt: Coverage Status
    :height: 20px

.. |pyversions| image:: https://img.shields.io/pypi/pyversions/poetry-bumpversion.svg
    :target: https://pypi.python.org/pypi/poetry-bumpversion
    :alt: Python Versions
    :height: 20px

.. |pypi-version| image:: https://badge.fury.io/py/poetry-bumpversion.svg
    :target: https://pypi.python.org/pypi/poetry-bumpversion
    :alt: PyPI version
    :height: 20px

.. |license| image:: https://img.shields.io/pypi/l/poetry-bumpversion.svg
    :target: https://pypi.python.org/pypi/poetry-bumpversion
    :alt: Licence
    :height: 20px
