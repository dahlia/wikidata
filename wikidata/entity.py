""":mod:`wikidata.entity` --- Wikidata entities
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
from typing import TYPE_CHECKING, Mapping, NewType, Optional, Union

from babel.core import Locale, UnknownLocaleError

from .multilingual import MultilingualText

if TYPE_CHECKING:
    from .client import Client  # noqa: F401

__all__ = 'Entity', 'EntityId'


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
