""":mod:`wikidata.entity` --- Wikidata entities
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import enum
from typing import TYPE_CHECKING, Mapping, NewType, Optional, Union

from babel.core import Locale, UnknownLocaleError

from .multilingual import MultilingualText

if TYPE_CHECKING:
    from .client import Client  # noqa: F401

__all__ = 'Entity', 'EntityId', 'EntityType'


#: The identifier of each :class:`Entity`.
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


class Entity:
    """Wikidata entity.  Can be an item or a property.  Its attrributes
    can be lazily loaded.

    """

    label = multilingual_attribute('labels')
    description = multilingual_attribute('descriptions')

    def __init__(self, id: EntityId, client: 'Client') -> None:
        self.id = id
        self.client = client
        self.data = None  # type: Optional[object]

    @property
    def type(self) -> EntityType:
        """(:class:`EntityType`) The type of entity, :attr:`~EntityType.item`
        or :attr:`~EntityType.property`.

        .. versionadded:: 0.2.0

        """
        return EntityType(self.attributes['type'])

    @property
    def attributes(self) -> Mapping[str, object]:
        if self.data is None:
            self.load()
        return self.data

    def load(self) -> None:
        self.data = self.client.request(self.id)['entities'][self.id]

    def __repr__(self) -> str:
        if self.data:
            label = str(self.label) if self.label else ...
        else:
            label = None
        return '<{0.__module__}.{0.__qualname__} {1}{2}>'.format(
            type(self), self.id,
            ' {!r}'.format(label) if label else ''
        )
