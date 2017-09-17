Changelog
=========

Version 0.5.4
'''''''''''''

To be released.


Version 0.5.3
'''''''''''''

Released on June 30, 2017.

- Fixed :exc:`ValueError` from :attr:`Entity.label
  <wikidata.entity.Entity.label>`/:attr:`Entity.description
  <wikidata.entity.Entity.description>` with languages `ISO 639-1`_
  doesn't cover (e.g. ``cbk-zam``).  [:issue:`2`]

  Although this fix prevents these properties from raising :exc:`ValueError`,
  it doesn't completely fix the problem.  :class:`babel.core.Locale` type,
  which Wikidata depends on, currently doesn't supprot languages other
  than `ISO 639-1`_.  In order to completely fix the problem, we need to
  patch Babel_ to support them, or make Wikidata independent from Babel_.

.. _ISO 639-1: https://www.iso.org/standard/22109.html
.. _Babel: http://babel.pocoo.org/


Version 0.5.2
'''''''''''''

Released on June 28, 2017.

- Fixed :exc:`AssertionError` from empty
  :class:`~wikidata.entity.multilingual_attribute`\ s.


Version 0.5.1
'''''''''''''

Released on June 28, 2017.

- Fixed :exc:`AssertionError` from :func:`len()` or iterating (:func:`iter()`)
  on :class:`~wikidata.entity.Entity` objects with empty claims.


Version 0.5.0
'''''''''''''

Released on June 13, 2017.

- Wikidata API calls over network became possible to be cached.

  - :class:`~wikidata.client.Client` now has
    :attr:`~wikidata.client.Client.cache_policy` attribute and constructor
    option.  Nothing is cached by default.

  - Added :mod:`wikidata.cache` module and :class:`~wikidata.cache.CachePolicy`
    interface in it.  Two built-in implementation of the interface were added:

    :class:`~wikidata.cache.NullCachePolicy`
       No-op.

    :class:`~wikidata.cache.MemoryCachePolicy`
       LRU cache in memory.

    :class:`~wikidata.cache.ProxyCachePolicy`
       Proxy/adapter to another proxy object.  Useful for utilizing third-party
       cache libraries.

  - ``wikidata.client.Client.request`` logger became to record logs about
    cache hits as :const:`~logging.DEBUG` level.


Version 0.4.4
'''''''''''''

Released on June 30, 2017.

- Fixed :exc:`ValueError` from :attr:`Entity.label
  <wikidata.entity.Entity.label>`/:attr:`Entity.description
  <wikidata.entity.Entity.description>` with languages `ISO 639-1`_
  doesn't cover (e.g. ``cbk-zam``).  [:issue:`2`]

  Although this fix prevents these properties from raising :exc:`ValueError`,
  it doesn't completely fix the problem.  :class:`babel.core.Locale` type,
  which Wikidata depends on, currently doesn't supprot languages other
  than `ISO 639-1`_.  In order to completely fix the problem, we need to
  patch Babel_ to support them, or make Wikidata independent from Babel_.


Version 0.4.3
'''''''''''''

Released on June 28, 2017.

- Fixed :exc:`AssertionError` from empty
  :class:`~wikidata.entity.multilingual_attribute`\ s.


Version 0.4.2
'''''''''''''

Released on June 28, 2017.

- Fixed :exc:`AssertionError` from :func:`len()` or iterating (:func:`iter()`)
  on :class:`~wikidata.entity.Entity` objects with empty claims.


Version 0.4.1
'''''''''''''

Released on April 30, 2017.

- Fixed :exc:`AssertionError` from :meth:`~wikidata.entity.Entity.getlist()`
  on entities with empty claims.


Version 0.4.0
'''''''''''''

Released on April 24, 2017.

- Monolingual texts became able to be handled.

  - Added :class:`~wikidata.multilingual.MonolingualText` type which is a true
    subtype of :class:`str`.


Version 0.3.0
'''''''''''''

Released on February 23, 2017.

- Now :class:`~wikidata.client.Client` became able to customize how it decodes
  datavalues to Python objects.

  - Added :mod:`wikidata.datavalue` module and
    :class:`~wikidata.datavalue.Decoder` class inside it.
  - Added :attr:`~.wikidata.client.Client.datavalue_decoder` option to
    :class:`~wikidata.client.Client`.

- Now files on Wikimeda Commons became able to be handled.

  - New decoder became able to parse Wikimedia Commons files e.g. images.
  - Added :mod:`wikidata.commonsmedia` module and
    :class:`~wikidata.commonsmedia.File` class inside it.

- The meaning of :class:`~wikidata.client.Client` constructor's ``base_url``
  prameter beccame not to contain the trailing path ``wiki/`` from
  ``https://www.wikidata.org/wiki/``.  As its meaning changed, the value of
  :const:`~wikidata.client.WIKIDATA_BASE_URL` constant also changed to not
  have the trailing path.

- Added ``load`` option to :meth:`Client.get() <wikidata.client.Client.get>`
  method.


Version 0.2.0
'''''''''''''

Released on February 19, 2017.

- Made :class:`~wikidata.entity.Entity` multidict.  Now it satisfies
  :class:`~typing.Mapping`\ [:class:`~wikidata.entity.Entity`, :class:`object`]
  protocol.
- Added :attr:`Entity.type <wikidata.entity.Entity.type>` property and
  :class:`~wikidata.entity.EntityType` enum class to represent it.
- Added :attr:`~wikidata.client.Client.entity_type_guess` option and
  :meth:`~wikidata.client.Client.guess_entity_type()` method to
  :class:`~wikidata.client.Client` class.
- Implemented :class:`~typing.Hashable` protocol and :token:`==`/:token:`!=`
  operators to :class:`~wikidata.entity.Entity` for equality test.


Version 0.1.0
'''''''''''''

Initial version.  Released on February 15, 2017.
