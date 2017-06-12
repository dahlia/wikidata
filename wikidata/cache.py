""":mod:`wikidata.cache` --- Caching policies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. versionchanged:: 0.5.0

"""
import collections
import hashlib
import logging
import pickle
import re
from typing import NewType, Optional

__all__ = ('CacheKey', 'CachePolicy', 'CacheValue',
           'MemoryCachePolicy', 'NullCachePolicy', 'ProxyCachePolicy')


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


class ProxyCachePolicy(CachePolicy):
    """This proxy policy is a proxy or an adaptor to another cache object.
    Cache objects can be anything if they satisfy the following interface::

        def get(key: str) -> Optional[bytes]: pass
        def set(key: str, value: bytes, timeout: int=0) -> None: pass
        def delete(key: str) -> None: pass

    (The above methods omit ``self`` parameters.)  It's compatible with
    de facto interface for caching libraries in Python (e.g. python-memcached,
    :mod:`werkzeug.contrib.cache`).

    :param cache_object: The cache object to adapt.
                         Read the above explanation.
    :param timeout: Lifespan of every cache in seconds.  0 means no expiration.
    :type timeout: :class:`int`
    :param property_timeout: Lifespan of caches for properties (in seconds).
                             Since properties don't change frequently or
                             their changes usually don't make important effect,
                             longer lifespan of properties' cache can be
                             useful.  0 means no expiration.
                             Set to the same as ``timeout`` by default.
    :type property_timeout: :class:`int`
    :param namespace: The common prefix attached to every cache key.
                      ``'wd_'`` by default.
    :type namespace: :class:`str`

    """

    PROPERTY_KEY_RE = re.compile(r'/P\d+\.json$')

    def __init__(self, cache_object, timeout: int,
                 property_timeout: Optional[int]=None,
                 namespace: str='wd_') -> None:
        self.cache_object = cache_object
        self.timeout = timeout  # type: int
        if property_timeout is None:
            property_timeout = timeout
        self.property_timeout = property_timeout  # type: int
        self.namespace = namespace  # type: str

    def encode_key(self, key: CacheKey) -> str:
        k = self.namespace + hashlib.md5(key.encode('utf-8')).hexdigest()
        logging.getLogger(__name__ + '.ProxyCachePolicy.encode_key').debug(
            'Encoded from key %r: %r', key, k
        )
        return k

    @classmethod
    def is_property(cls, key: CacheKey) -> bool:
        return bool(cls.PROPERTY_KEY_RE.search(key))

    def get(self, key: CacheKey) -> Optional[CacheValue]:
        k = self.encode_key(key)
        v = self.cache_object.get(k)
        if v is None:
            return None
        return pickle.loads(v)

    def set(self, key: CacheKey, value: Optional[CacheValue]) -> None:
        k = self.encode_key(key)
        if value is None:
            self.cache_object.delete(k)
            return
        v = pickle.dumps(value)
        time = self.property_timeout if self.is_property(key) else self.timeout
        self.cache_object.set(k, v, time)
