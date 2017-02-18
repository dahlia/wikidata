Wikidata_ client library for Python
===================================

.. image:: https://badge.fury.io/py/Wikidata.svg
   :target: https://pypi.python.org/pypi/Wikidata
   :alt: Latest PyPI version

.. image:: https://readthedocs.org/projects/wikidata/badge/?version=latest
   :target: https://wikidata.readthedocs.io/
   :alt: Documentation Status

.. image:: https://travis-ci.org/dahlia/wikidata.svg
   :alt: Build Status
   :target: https://travis-ci.org/dahlia/wikidata

This package provides easy APIs to use Wikidata_ for Python.

>>> entity = client.get('Q494290')
>>> entity
<wikidata.entity.Entity Q494290 'Shin Jung-hyeon'>
>>> entity.description
m'South Korean rock guitarist and singer-songwriter'

.. _Wikidata: https://www.wikidata.org/
