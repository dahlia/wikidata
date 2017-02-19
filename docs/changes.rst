Changelog
=========

Version 0.3.0
'''''''''''''

To be released.

- The meaning of :class:`~wikidata.client.Client` constructor's ``base_url``
  prameter beccame not to contain the trailing path ``wiki/`` from
  ``https://www.wikidata.org/wiki/``.  As its meaning changed, the value of
  :const:`~wikidata.client.WIKIDATA_BASE_URL` constant also changed to not
  have the trailing path.


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
