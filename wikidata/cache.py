""":mod:`wikidata.cache` --- Caching policies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. versionchanged:: 0.5.0

"""
import collections
from typing import NewType, Optional

__all__ = ('CacheKey', 'CachePolicy', 'CacheValue',
           'MemoryCachePolicy', 'NullCachePolicy')


#: The type of keys to look up cached values.  Alias of :class:`str`.
CacheKey = NewType('CacheKey', str)

#: The type of cached values.
CacheValue = NewType('CacheValue', object)


class CachePolicy:
    """Interface for caching policies."""

    def get(self, key: CacheKey) -> Optional[CacheValue]:
        """Look up a cached value by its ``key``.

        :param key: The key string to look up a cached value.
        :type key: :const:`CacheKey`
        :return: The cached value if it exists.
                 :const:`None` if there's no such ``key``.
        :rtype: :class:`~typing.Optional`\ [:const:`CacheValue`]

        """
        raise NotImplementedError(
            'Concreate subclasses of {0.__module__}.{0.__qualname__} have to '
            'override .get() method'.format(CachePolicy)
        )

    def set(self, key: CacheKey, value: Optional[CacheValue]) -> None:
        """Create or update a cache.

        :param key: A key string to create or update.
        :type key: :const:`CacheKey`
        :param value: A value to cache.  :const:`None` to remove cache.
        :type value: :class:`~typing.Optional`\ [:const:`CacheValue`]

        """
        raise NotImplementedError(
            'Concreate subclasses of {0.__module__}.{0.__qualname__} have to '
            'override .set() method'.format(CachePolicy)
        )


class NullCachePolicy(CachePolicy):
    """No-op cache policy."""

    def get(self, key: CacheKey) -> Optional[CacheValue]:
        return None

    def set(self, key: CacheKey, value: Optional[CacheValue]) -> None:
        pass


class MemoryCachePolicy(CachePolicy):
    """LRU (least recently used) cache in memory.

    :param max_size: The maximum number of values to cache.  128 by default.
    :type max_size: :class:`int`

    """

    def __init__(self, max_size: int=128) -> None:
        self.max_size = max_size  # type: int
        self.values = \
            collections.OrderedDict()  # type: collections.OrderedDict

    def get(self, key: CacheKey) -> Optional[CacheValue]:
        try:
            v = self.values[key]
        except KeyError:
            v = None
        else:
            self.values.move_to_end(key)
        return v

    def set(self, key: CacheKey, value: Optional[CacheValue]) -> None:
        try:
            del self.values[key]
        except KeyError:
            pass
        if value is None:
            return
        self.values[key] = value
        while len(self.values) > self.max_size:
            self.values.popitem(last=False)
