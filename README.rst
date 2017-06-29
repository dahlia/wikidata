Wikidata_ client library for Python
===================================

.. image:: https://badge.fury.io/py/Wikidata.svg
   :target: https://pypi.org/project/Wikidata/
   :alt: Latest PyPI version

.. image:: https://readthedocs.org/projects/wikidata/badge/?version=latest
   :target: https://wikidata.readthedocs.io/
   :alt: Documentation Status

.. image:: https://travis-ci.org/dahlia/wikidata.svg
   :alt: Build Status
   :target: https://travis-ci.org/dahlia/wikidata

This package provides easy APIs to use Wikidata_ for Python.

>>> from wikidata.client import Client
>>> client = Client()  # doctest: +SKIP
>>> entity = client.get('Q20145', load=True)
>>> entity
<wikidata.entity.Entity Q20145 'IU'>
>>> entity.description
m'South Korean singer and actress'
>>> image_prop = client.get('P18')
>>> image = entity[image_prop]
>>> image
<wikidata.commonsmedia.File 'File:KBS "The Producers" press conference, 11 May 2015 10.jpg'>
>>> image.image_resolution
(820, 1122)
>>> image.image_url
'https://upload.wikimedia.org/wikipedia/commons/6/60/KBS_%22The_Producers%22_press_conference%2C_11_May_2015_10.jpg'

.. _Wikidata: https://www.wikidata.org/
