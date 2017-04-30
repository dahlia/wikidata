""":mod:`wikidata.entity` --- Wikidata entities
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import collections.abc
import enum
import logging
from typing import (TYPE_CHECKING, Iterator, Mapping, NewType,
                    Optional, Sequence, Tuple, Union)

from babel.core import Locale, UnknownLocaleError

from .multilingual import MultilingualText

if TYPE_CHECKING:
    from .client import Client  # noqa: F401

__all__ = 'Entity', 'EntityId', 'EntityType'


#: The identifier of each :class:`Entity`.  Alias of :class:`str`.
EntityId = NewType('EntityId', str)


class multilingual_attribute:
    """Define accessor to a multilingual attribute of entity."""

    def __init__(self, attribute: str) -> None:
        self.attribute = attribute

    def __get__(self,
                obj: 'Entity',
                cls=None) -> Union[MultilingualText, type]:
        if obj is None:
            return self
        cache_id = '$' + self.attribute
        try:
            value = obj.__dict__[cache_id]
        except KeyError:
            def parse(locale: str) -> Optional[Locale]:
                try:
                    return Locale.parse(locale.replace('-', '_'))
                except UnknownLocaleError:
                    return None
            attr = obj.attributes.get(self.attribute, {})
            assert isinstance(attr, collections.abc.Mapping)
            pairs = (
                (parse(item['language']), item['value'])
                for item in attr.values()
            )
            value = MultilingualText({k: v for k, v in pairs if k})
            obj.__dict__[cache_id] = value
        return value


class EntityType(enum.Enum):
    """The enumerated type which consists of two possible values:

    - :attr:`~EntityType.item`
    - :attr:`~EntityType.property`

    .. versionadded:: 0.2.0

    """

    #: (:class:`EntityType`) Items are :class:`Entity` objects that are
    #: typically represented by Wikipage (at least in some Wikipedia
    #: languages).  They can be viewed as "the thing that a Wikipage is about,"
    #: which could be an individual thing (the person `Albert Einstein`_),
    #: a general class of things (the class of all Physicists_),
    #: and any other concept that is the subject of some Wikipedia page
    #: (including things like `History of Berlin`_).
    #:
    #: .. seealso::
    #:
    #:    Items_ --- Wikibase Data Model
    #:       The data model of Wikibase describes the structure of
    #:       the data that is handled in Wikibase.
    #:
    #: .. _Albert Einstein: https://en.wikipedia.org/wiki/Albert_Einstein
    #: .. _Physicists: https://en.wikipedia.org/wiki/Physicist
    #: .. _History of Berlin: https://en.wikipedia.org/wiki/History_of_Berlin
    #: .. _Items: https://www.mediawiki.org/wiki/Wikibase/DataModel#Items
    item = 'item'

    #: (:class:`EntityType`) Properties are :class:`Entity` objects that
    #: describe a relationship between items (or other :class:`Entity` objects)
    #: and values of the property.  Typical properties are *population*
    #: (using numbers as values), *binomial name* (using strings as values),
    #: but also *has father* and *author of* (both using items as values).
    #:
    #: .. seealso::
    #:
    #:    Properties_ --- Wikibase Data Model
    #:       The data model of Wikibase describes the structure of
    #:       the data that is handled in Wikibase.
    #:
    #: .. _Properties: https://mediawiki.org/wiki/Wikibase/DataModel#Properties
    property = 'property'


class Entity(collections.abc.Mapping, collections.abc.Hashable):
    """Wikidata entity.  Can be an item or a property.  Its attrributes
    can be lazily loaded.

    To get an entity use :meth:`Client.get() <wikidata.client.Client.get>`
    method instead of the constructor of :class:`Entity`.

    .. note::

       Although it implements :class:`~typing.Mapping`\ [:class:`EntityId`,
       :class:`object`], it actually is multidict.  See also :meth:`getlist()`
       method.

    .. versionchanged:: 0.2.0

       Implemented :class:`~typing.Mapping`\ [:class:`EntityId`,
       :class:`object`] protocol for easy access of statement values.

    .. versionchanged:: 0.2.0

       Implemented :class:`~typing.Hashable` protocol and
       :token:`==`/:token:`!=` operators for equality test.

    """

    label = multilingual_attribute('labels')
    description = multilingual_attribute('descriptions')

    def __init__(self, id: EntityId, client: 'Client') -> None:
        self.id = id
        self.client = client
        self.data = None  # type: Optional[Mapping[str, object]]

    def __eq__(self, other) -> bool:
        if not isinstance(other, type(self)):
            raise TypeError(
                'expected an instance of {0.__module__}.{0.__qualname__}, '
                'not {1!r}'.format(type(self), other)
            )
        return other.id == self.id and self.client is other.client

    def __hash__(self) -> int:
        return hash((self.id, id(self.client)))

    def __len__(self) -> int:
        claims_map = self.attributes.get('claims', {})
        assert isinstance(claims_map, collections.abc.Mapping)
        return len(claims_map)

    def __iter__(self) -> Iterator['Entity']:
        client = self.client
        claims_map = self.attributes.get('claims', {})
        assert isinstance(claims_map, collections.abc.Mapping)
        for prop_id in claims_map:
            yield client.get(prop_id)

    def __getitem__(self, key: 'Entity') -> object:
        result = self.getlist(key)
        if result:
            return result[0]
        raise KeyError(key)

    def getlist(self, key: 'Entity') -> Sequence[object]:
        """Return all values associated to the given ``key`` property
        in sequence.

        :param key: The property entity.
        :type key: :class:`Entity`
        :return: A sequence of all values associated to the given ``key``
                 property.  It can be empty if nothing is associated to
                 the property.
        :rtype: :class:`~typing.Sequence`\ [:class:`object`]

        """
        if not (isinstance(key, type(self)) and
                key.type is EntityType.property):
            return []
        claims_map = self.attributes.get('claims') or {}
        assert isinstance(claims_map, collections.abc.Mapping)
        claims = claims_map.get(key.id, [])
        claims.sort(key=lambda claim: claim['rank'],  # FIXME
                    reverse=True)
        logger = logging.getLogger(__name__ + '.Entity.getitem')
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug('claim data: %s',
                         __import__('pprint').pformat(claims))
        decode = self.client.decode_datavalue
        return [decode(snak['datatype'], snak['datavalue'])
                for snak in (claim['mainsnak'] for claim in claims)]

    def iterlists(self) -> Iterator[Tuple['Entity', Sequence[object]]]:
        for prop in self:
            yield prop, self.getlist(prop)

    def lists(self) -> Sequence[Tuple['Entity', Sequence[object]]]:
        """Similar to :meth:`items()` except the returning pairs have
        each list of values instead of each single value.

        :return: The pairs of (key, values) where values is a sequence.
        :rtype: :class:`~typing.Sequence`\ [:class:`~typing.Tuple`\ \
[:class:`Entity`, :class:`~typing.Sequence`\ [:class:`object`]]]

        """
        return list(self.iterlists())

    def iterlistvalues(self) -> Iterator[Sequence[object]]:
        for _, values in self.iterlists():
            yield values

    def listvalues(self) -> Sequence[Sequence[object]]:
        return list(self.iterlistvalues())

    @property
    def type(self) -> EntityType:
        """(:class:`EntityType`) The type of entity, :attr:`~EntityType.item`
        or :attr:`~EntityType.property`.

        .. versionadded:: 0.2.0

        """
        if self.data is None:
            guessed_type = self.client.guess_entity_type(self.id)
            if guessed_type is not None:
                return guessed_type
            # If guessing was failed follow the straightforward way.
        return EntityType(self.attributes['type'])

    @property
    def attributes(self) -> Mapping[str, object]:
        if self.data is None:
            self.load()
        assert self.data is not None
        return self.data

    def load(self) -> None:
        url = './wiki/Special:EntityData/{}.json'.format(self.id)
        result = self.client.request(url)
        assert isinstance(result, collections.abc.Mapping)
        entities = result['entities']
        assert isinstance(entities, collections.abc.Mapping)
        data = entities[self.id]
        assert isinstance(data, collections.abc.Mapping)
        self.data = data

    def __repr__(self) -> str:
        if self.data:
            label = str(self.label) if self.label else ...
        else:
            label = None
        return '<{0.__module__}.{0.__qualname__} {1}{2}>'.format(
            type(self), self.id,
            ' {!r}'.format(label) if label else ''
        )
