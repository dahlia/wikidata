Wikidata_ client library for Python
===================================

.. image:: https://badge.fury.io/py/Wikidata.svg
   :target: https://pypi.org/project/Wikidata/
   :alt: Latest PyPI version

.. image:: https://readthedocs.org/projects/wikidata/badge/?version=latest
   :target: https://wikidata.readthedocs.io/
   :alt: Documentation Status

.. image:: https://github.com/dahlia/wikidata/actions/workflows/main.yaml/badge.svg?branch=main
   :alt: GitHub Actions
   :target: https://github.com/dahlia/wikidata/actions/workflows/main.yaml

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
>>> search_results = client.search("Ireland")
[SearchResult(entity_id='Q27', name='Ireland', similarity_score=100.0%, description='sovereign state in Northwestern Europe'), 
SearchResult(entity_id='Q22890', name='Ireland', similarity_score=100.0%, description='island in the North Atlantic Ocean'), 
SearchResult(entity_id='Q28199768', name='Ireland', similarity_score=100.0%, description='family name')]
>>> search_results = client.search("Egypt", likeness_threshold=0.6, limit=5)
[SearchResult(entity_id='Q79', name='Egypt', similarity_score=100.0%, description='country in Northeast Africa and Southwest Asia'), 
SearchResult(entity_id='Q2083973', name='Egypt', similarity_score=100.0%, description='town in Arkansas'), 
SearchResult(entity_id='Q50868', name='Egyptian', similarity_score=76.9%, description='extinct language spoken in ancient Egypt'), 
SearchResult(entity_id='Q202311', name='Roman Egypt', similarity_score=62.5%, description='Roman province that encompassed most of modern-day Egypt')]

.. _Wikidata: https://www.wikidata.org/
