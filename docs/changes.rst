Changelog
=========

Version 0.9.0
-------------

To be released.


Version 0.8.2
-------------

Released on July 10, 2024.

- Fixing issues [:issue:`35`] and [:issue:`54`]. Returns raw time dictionaries instead of crashing when encountering unsupported calendar models   [:pr:`61` by David Doukhan].


Version 0.8.0 & 0.8.1
---------------------

Released on July 7, 2024.

- Python 3.4--3.7 are no more supported.  The minimum supported Python version
  is Python 3.8.  Instead, now it's tested with Python 3.8--3.11.
- :class:`~wikidata.entity.Entity` and :class:`~wikidata.client.Client` became
  possible to be serialized using :mod:`pickle`.  [:issue:`31`]
- Fixed a typing bug that :attr:`Entity.label <wikidata.entity.Entity.label>`
  and :attr:`Entity.description <wikidata.entity.Entity.description>` properties
  were incorrectly typed.
- :class:`wikidata.multilingual.MultilingualText`'s constructor became to take
  only :class:`Locale` for parameter ``locale``.
- Added date precision 7 in :class:`wikidata.datavalue.decoder`.
  [:pr:`59` by Baptiste Bayche]
- Added date precision 10 in :class:`wikidata.datavalue.decoder`.
  [:pr:`60` by David Doukhan]


Version 0.7.0
-------------

Released on July 31, 2020.

- Marked the package as supporting type checking by following :pep:`561`.

- Now non-existent entities became able to be handled.  [:pr:`11`]

  - Added :class:`~wikidata.entity.EntityState` enum class.
  - Added :attr:`Entity.state <wikidata.entity.Entity.state>` attribute.
  - Fixed a bug that raised :exc:`~urllib.error.HTTPError` when
    non-existent :class:`~wikidata.entity.Entity` was requested.

- Languages (locales) became no more represented as :class:`babel.core.Locale`,
  but represented :class:`wikidata.multilingual.Locale` instead.
  [:issue:`2`, :issue:`27`, :pr:`30` by Nelson Liu]

  - Removed Babel_ from the dependencies.

  - Added :class:`wikidata.multilingual.Locale` type.

    To replace the :class:`babel.core.Locale` type,
    the :class:`wikidata.multilingual.Locale` type has been
    aliased to `str`. This is a *breaking change* for all Wikidata public API
    functions that formerly returned or ingested :class:`babel.core.Locale` .

- Added support for ``time`` datatypes with precision 9 (year-only).
  [:pr:`26` by Nelson Liu]

- Added support for globe coordinate datatype.  [:pr:`28` by Nelson Liu]

  - Added support for decoding the ``globe-coordinate`` datatype.
  - Added :mod:`wikidata.globecoordinate` module.

- Added support for quantity datatype.  [:pr:`29` by Nelson Liu]

  - Added support for decoding the ``quantity`` datatype.
  - Added :mod:`wikidata.quantity` module.  [:pr:`29`]

- Fixed :exc:`KeyError` from :meth:`Entity.getlist()
  <wikidata.entity.Entity.getlist>` if the property is explicitly associated
  with "no value". [:issue:`18`]

- Fixed a bug that raised :exc:`KeyError` when accessing an image more than
  once and :class:`~wikidata.cache.MemoryCachePolicy` was enabled.
  [:pr:`24` by Héctor Cordobés]


Version 0.6.1
-------------

Released on September 18, 2017.

- Fixed :exc:`ImportError` on Python 3.4 due to lack of :mod:`typing` module.
  [:issue:`4`]


Version 0.6.0
-------------

Released on September 12, 2017.

- Fixed :exc:`KeyError` from :meth:`Client.get() <wikidata.client.Client.get>`
  on an entity is redirected to its canonical entity.


Version 0.5.4
-------------

Released on September 18, 2017.

- Fixed :exc:`ImportError` on Python 3.4 due to lack of :mod:`typing` module.
  [:issue:`4`]


Version 0.5.3
-------------

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
-------------

Released on June 28, 2017.

- Fixed :exc:`AssertionError` from empty
  :class:`~wikidata.entity.multilingual_attribute`\ s.


Version 0.5.1
-------------

Released on June 28, 2017.

- Fixed :exc:`AssertionError` from :func:`len()` or iterating (:func:`iter()`)
  on :class:`~wikidata.entity.Entity` objects with empty claims.


Version 0.5.0
-------------

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
-------------

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
-------------

Released on June 28, 2017.

- Fixed :exc:`AssertionError` from empty
  :class:`~wikidata.entity.multilingual_attribute`\ s.


Version 0.4.2
-------------

Released on June 28, 2017.

- Fixed :exc:`AssertionError` from :func:`len()` or iterating (:func:`iter()`)
  on :class:`~wikidata.entity.Entity` objects with empty claims.


Version 0.4.1
-------------

Released on April 30, 2017.

- Fixed :exc:`AssertionError` from :meth:`~wikidata.entity.Entity.getlist()`
  on entities with empty claims.


Version 0.4.0
-------------

Released on April 24, 2017.

- Monolingual texts became able to be handled.

  - Added :class:`~wikidata.multilingual.MonolingualText` type which is a true
    subtype of :class:`str`.


Version 0.3.0
-------------

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
-------------

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
-------------

Initial version.  Released on February 15, 2017.
