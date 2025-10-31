Contributing
============

What branch to work on
----------------------

This project follows `Semantic Versioning`_, and every release is tagged.
There are also branches looking like version numbers except of they have only
one period (instead of two), e.g., *0.6*, *0.7*.  These are maintenance
branches.  The branch named *main* [#]_ is for preparing next major version.

If you send a patch to fix a bug your pull request usually should be based on
the latest maintenance branch, not *main*.

If you send a patch to add a new feature it should be based on
the *main* branch.

.. [#] We don't use the term *master*.  For the rationale, please read
   the following discussion and articles:

   - https://lore.kernel.org/git/CAOAHyQwyXC1Z3v7BZAC+Bq6JBaM7FvBenA-1fcqeDV==apdWDg@mail.gmail.com/
   - https://www.bbc.com/news/technology-53050955
   - https://sfconservancy.org/news/2020/jun/23/gitbranchname/

.. _Semantic Versioning: https://semver.org/


How to run tests
----------------

This project uses `uv`_ for dependency management and virtual environment
handling. We support various Python interpreters (CPython and PyPy) and
versions, and use tox_ for running tests across multiple environments.

First, install `uv` (see `uv's installation guide`_). Then, sync dependencies::

    uv sync --extra tests

To run the test suite on all supported Python versions::

    uv run tox

If you don't want to install all Python interpreters, use
``--skip-missing-interpreters`` option::

    uv run tox --skip-missing-interpreters

To run tests on multiple interpreters at a time, use ``--parallel`` option::

    uv run tox --parallel

To run a single test::

    uv run pytest tests/client_test.py::test_client_get -v

For type checking::

    uv run mypy -p wikidata

For linting::

    uv run flake8

.. _uv: https://github.com/astral-sh/uv
.. _uv's installation guide: https://docs.astral.sh/uv/getting-started/installation/
.. _tox: https://tox.readthedocs.io/
__ https://tox.readthedocs.io/en/latest/install.html
