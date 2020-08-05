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

As this project supports various Python interpreters (CPython and PyPy) and
versions, to ensure it works well with them, we use tox_.  You don't need to
create a virtual environment by yourself.  ``tox`` automatically creates
virtual environments for various Python versions and run the same test suite
on all of them.

The easiest to install ``tox`` is to use ``pip`` [#]_::

    pip install tox tox-pip-version

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
