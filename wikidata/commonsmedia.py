""":mod:`wikidata.commonsmedia` --- `Wikimedia Commons`_
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. _Wikimedia Commons: https://commons.wikimedia.org/

.. versionadded:: 0.3.0

"""
import collections
from typing import Mapping, Optional, Tuple, cast
import urllib.parse

from .client import Client

__all__ = 'File', 'FileError'


class File:
    """Represent a file on `Wikimedia Commons`_."""

    __slots__ = 'client', 'title', 'data'

    def __init__(self, client: Client, title: str) -> None:
        self.client = client
        self.title = title
        self.data = None  # type: Optional[Mapping[str, object]]

    @property
    def page_url(self) -> str:
        """(:class:`str`) The canonical url of the page."""
        url = self.attributes['canonicalurl']
        assert isinstance(url, str)
        return url

    @property
    def image_url(self) -> Optional[str]:
        """(:class:`~typing.Optional`\ [:class:`str`]) The image url.
        It may be :const:`None` if it's not an image.

        """
        images = self.attributes.get('imageinfo', [])
        if images and isinstance(images, collections.abc.Sequence):
            return images[0]['url']
        return None

    @property
    def image_mimetype(self) -> Optional[str]:
        """(:class:`~typing.Optional`\ [:class:`str`]) The MIME type of
        the image.  It may be :const:`None` if it's not an image.

        """
        images = self.attributes.get('imageinfo', [])
        if images and isinstance(images, collections.abc.Sequence):
            return images[0]['mime']
        return None

    @property
    def image_resolution(self) -> Optional[Tuple[int, int]]:
        """(:class:`~typing.Optional`\ [:class:`~typing.Tuple`\ [:class:`int`,
        :class:`int`]]) The (width, height) pair of the image.
        It may be :const:`None` if it's not an image.

        """
        images = self.attributes.get('imageinfo', [])
        if images and isinstance(images, collections.abc.Sequence):
            img = images[0]
            return img['width'], img['height']
        return None

    @property
    def image_size(self) -> Optional[int]:
        """(:class:`~typing.Optional`\ [:class:`int`]) The size of the image
        in bytes.  It may be :const:`None` if it's not an image.

        """
        images = self.attributes.get('imageinfo', [])
        if images and isinstance(images, collections.abc.Sequence):
            return images[0]['size']
        return None

    @property
    def attributes(self) -> Mapping[str, object]:
        if self.data is None:
            self.load()
        assert self.data is not None
        return self.data

    def load(self) -> None:
        url = './w/api.php?action=query&prop=imageinfo|info&inprop=url&iiprop=url|size|mime&format=json&titles={}'  # noqa: E501
        url = url.format(urllib.parse.quote(self.title))
        result = cast(Mapping[str, object], self.client.request(url))
        if result.get('error'):
            raise FileError('the server respond an error: ' +
                            repr(result['error']))
        query = result['query']
        assert isinstance(query, collections.Mapping)
        _, self.data = query['pages'].popitem()

    def __repr__(self) -> str:
        return '<{0.__module__}.{0.__qualname__} {1!r}>'.format(
            type(self), self.title
        )


class FileError(ValueError, RuntimeError):
    """Exception raised when something goes wrong with :class:`File`."""
