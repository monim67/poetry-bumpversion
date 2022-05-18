####################
poetry-bumpversion
####################

The ``poetry version`` command only updates version in ``pyproject.toml`` file.
This plugin updates version in other files when ``poetry version <version>``
command is executed.


********************
Getting Started
********************

++++++++++++++++++++
Prerequisites
++++++++++++++++++++

- poetry = ^1.2.0a1

++++++++++++++++++++
Install
++++++++++++++++++++

Install the plugin by poetry plugin command.

::

    poetry plugin add poetry-bumpversion

++++++++++++++++++++
Configure files
++++++++++++++++++++

Say you have ``__version__`` variable set at ``your_package/__init__.py`` file

.. code:: python

    __version__ = "0.1.0" # It MUST match the version in pyproject.toml file


Add the following to your ``pyproject.toml`` file.

.. code:: toml

    [tool.poetry_bumpversion.file."your_package/__init__.py"]

Now run ``poetry version patch`` to check if version in both ``pyproject.toml`` and
``your_package/__init__.py`` file has been updated.

You can add more files following the steps above. You can also fine define
search and replace terms to be more precise

.. code:: toml

    [tool.poetry_bumpversion.file."your_package/__init__.py"]
    search = '__version__ = "{current_version}"'
    replace = '__version__ = "{new_version}"'

********************
License
********************

This project is licensed under MIT License - see the
`LICENSE <https://github.com/monim67/poetry-bumpversion/blob/master/LICENSE>`_ file for details.
