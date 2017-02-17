""":mod:`wikidata.client` --- Client session
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import io
import json
from typing import Mapping, MutableMapping, Optional, Sequence, Union, cast
import urllib.parse
import urllib.request
import weakref

from .entity import Entity, EntityId, EntityType

__all__ = 'WIKIDATA_BASE_URL', 'Client'


WIKIDATA_BASE_URL = 'https://www.wikidata.org/wiki/'


class Client:
    """Wikidata client session.

    :param base_url: The base url of the Wikidata.
                     :const:`WIKIDATA_BASE_URL` is used by default.
    :type base_url: :class:`str`
    :param opener: The opener for :mod:`urllib.request`.
                   If omitted or :const:`None` the default opener is used.
    :type opener: :class:`urllib.request.OpenerDirector`
    :param entity_type_guess: Whether to guess :attr:`~.entity.Entity.type`
                              of :class:`~.entity.Entity` from its
                              :attr:`~.entity.Entity.id` for less HTTP
                              requests.  :const:`True` by default.
    :type entity_type_guess: :class:`bool`

    .. versionadded:: 0.2.0
       The ``entity_type_guess`` option.

    """

    #: (:class:`bool`) Whether to guess :attr:`~.entity.Entity.type`
    #: of :class:`~.entity.Entity` from its :attr:`~.entity.Entity.id`
    #: for less HTTP requests.
    #:
    #: .. versionadded:: 0.2.0
    entity_type_guess = True

    def __init__(self,
                 base_url: str=WIKIDATA_BASE_URL,
                 opener: Optional[urllib.request.OpenerDirector]=None,
                 entity_type_guess: bool=True,
                 repr_string: Optional[str]=None) -> None:
        if opener is None:
            if urllib.request._opener is None:  # type: ignore
                try:
                    urllib.request.urlopen('')
                except (ValueError, TypeError):
                    pass
            opener = urllib.request._opener  # type: ignore
        assert isinstance(opener, urllib.request.OpenerDirector)
        self.base_url = base_url
        self.opener = opener  # type: urllib.request.OpenerDirector
        self.entity_type_guess = entity_type_guess
        self.identity_map = cast(MutableMapping[EntityId, Entity],
                                 weakref.WeakValueDictionary())
        self.repr_string = repr_string

    def get(self, entity_id: EntityId) -> Entity:
        """Get a Wikidata entity by its :class:`~.entity.EntityId`."""
        try:
            entity = self.identity_map[entity_id]
        except KeyError:
            entity = Entity(entity_id, self)
            self.identity_map[entity_id] = entity
        return entity

    def guess_entity_type(self, entity_id: EntityId) -> Optional[EntityType]:
        """Guess :class:`~.entity.EntityType` from the given
        :class:`~.entity.EntityId`.  It could return :const:`None` when it
        fails to guess.

        .. note::

           It always fails to guess when :attr:`entity_type_guess`
           is configued to :const:`False`.

        :return: The guessed :class:`~.entity.EntityId`, or :const:`None`
                 if it fails to guess.
        :rtype: :class:`~typing.Optional`\ [:class:`~.entity.EntityType`]

        .. versionadded:: 0.2.0

        """
        if not self.entity_type_guess:
            return
        if entity_id[0] == 'Q':
            return EntityType.item
        elif entity_id[0] == 'P':
            return EntityType.property

    def request(self, id: EntityId) -> Union[
        bool, int, float, str,
        Mapping[
            str,
            Union[bool, int, float, str, Mapping[str, object], Sequence]
        ],
        Sequence[Union[bool, int, float, str, Mapping[str, object], Sequence]]
    ]:
        url = urllib.parse.urljoin(
            self.base_url,
            './Special:EntityData/{}.json'.format(id)
        )
        response = self.opener.open(url)
        buffer_ = io.TextIOWrapper(response, encoding='utf-8')
        result = json.load(buffer_)
        return result

    def __repr__(self) -> str:
        if self.repr_string is not None:
            return self.repr_string
        return '{0.__module__}.{0.__qualname__}({1!r})'.format(
            type(self),
            self.base_url
        )
