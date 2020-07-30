""":mod:`wikidata.multilingual` --- Multilingual texts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import collections.abc
from typing import Iterator, Mapping, NewType, Type, Union

__all__ = 'Locale', 'MonolingualText', 'MultilingualText'


#: The locale of each :class:`MonolingualText` or internal
#: mapping of each :class:`MultilingualText`.  Alias of :class:`str`.
#:
#: .. versionadded:: 0.7.0
Locale = NewType('Locale', str)


class MultilingualText(collections.abc.Mapping):

    __slots__ = 'texts',

    def __init__(self, texts: Mapping[Union[Locale, str], str]) -> None:
        self.texts = {Locale(lc): t for lc, t in texts.items()}

    def __iter__(self) -> Iterator[Locale]:
        for locale in self.texts:
            yield locale

    def __len__(self) -> int:
        return len(self.texts)

    def __contains__(self, locale: Locale) -> bool:  # type: ignore[override]
        return locale in self.texts

    def __getitem__(self, locale: Locale) -> str:
        return self.texts[locale]

    def __bool__(self) -> bool:
        return bool(self.texts)

    def __str__(self) -> str:
        try:
            return self.texts[Locale('en')]
        except KeyError:
            value = ''
            for lang, value in self.texts.items():
                if lang.startswith('en_'):
                    return value
            return value

    def __repr__(self) -> str:
        if self:
            return 'm{0!r}'.format(str(self))
        return '{0.__module__}.{0.__qualname__}({{}})'.format(type(self))


class MonolingualText(str):
    """
    Locale-denoted text. It's almost equivalent to :class:`str` (and indeed
    subclasses :class:`str`) except that it has an extra attribute,
    :attr:`locale`, that denotes what language the text is written in.
    """

    #: (:class:`Locale`) The code of :attr:`locale`.
    locale = None  # type: Locale

    def __new__(cls: Type[str],
                text: str,
                locale: Union[Locale, str]) -> 'MonolingualText':
        self = str.__new__(cls, text)  # type: ignore
        self.locale = locale
        return self

    def __repr__(self) -> str:
        altrepr = '({0}:) {1!s}'.format(self.locale, self)
        return '{0!r}[{1}:]'.format(altrepr, len(self.locale) + 4)
