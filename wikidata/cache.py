""":mod:`wikidata.cache` --- Caching policies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. versionchanged:: 0.5.0

"""
from typing import NewType, Optional

__all__ = 'CacheKey', 'CachePolicy', 'CacheValue'


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
