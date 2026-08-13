:mod:`wikidata.cache` --- Caching policies
==========================================

.. versionadded:: 0.5.0

.. automodule:: wikidata.cache
   :members:

Sample usage with cache ``pip install cachelib``:

>>> from wikidata.client import Client
>>> from cachelib.file import FileSystemCache
>>> 
>>> wikidata_cache = wikidata.cache.ProxyCachePolicy(
>>>    timeout=3600*24*30, # One month cache in seconds
>>>    FileSystemCache(
>>>    "/tmp/wikidata"
>>> )
>>> client = Client(cache_policy=wikidata_cache)
