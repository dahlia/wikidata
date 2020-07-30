Contributing
============

How to run tests
----------------

As this project supports various Python interpreters (CPython and PyPy) and
versions, to ensure it works well with them, we use tox_.  You don't need to
create a virtual environment by yourself.  ``tox`` automatically creates
virtual environments for various Python versions and run the same test suite
on all of them.

The easiest to install ``tox`` is to use ``pip`` [#]_::

    pip install tox

Once you've installed ``tox``, it's very simple to run the test suite on
all Python versions this project aims to support::

    tox

Note that you need to install Python interpreters besides ``tox``.
If you don't want to install all of them use ``--skip-missing-interpreters``
option::

    tox --skip-missing-interpreters

To run tests on multiple interpreters at a time, use ``--parallel`` option::

    tox --parallel

.. [#] See also the `tox's official docs`__.
.. _tox: https://tox.readthedocs.io/
__ https://tox.readthedocs.io/en/latest/install.html
