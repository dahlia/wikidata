""":mod:`wikidata.multilingual` --- Multilingual texts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import collections.abc
from typing import Iterator, Mapping, Type, Union

from babel.core import Locale

__all__ = 'MonolingualText', 'MultilingualText', 'normalize_locale_code'


class MultilingualText(collections.abc.Mapping):

    __slots__ = 'texts',

    def __init__(self, texts: Mapping[Union[Locale, str], str]) -> None:
        self.texts = {normalize_locale_code(l): t for l, t in texts.items()}

    def __iter__(self) -> Iterator[Locale]:
        for locale_code in self.texts:
            yield Locale.parse(locale_code)

    def __len__(self) -> int:
        return len(self.texts)

    def __contains__(self, locale: Locale) -> bool:
        return str(locale) in self.texts

    def __getitem__(self, locale: Locale) -> str:
        return self.texts[str(locale)]

    def __bool__(self) -> bool:
        return bool(self.texts)

    def __str__(self) -> str:
        try:
            return self.texts['en']
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
    """Locale-denoted text.  It's almost equivalent to :class:`str`
    (and indeed subclasses :class:`str`) except that it has two more
    attribute: :attr:`locale` and :attr:`locale_code` that denote
    what language the text is written in.

    """

    #: (:class:`str`) The code of :attr:`locale`.
    locale_code = None  # type: Locale

    def __new__(cls: Type[str],
                text: str,
                locale: Union[Locale, str]) -> 'MonolingualText':
        self = str.__new__(cls, text)  # type: ignore
        self.locale_code = normalize_locale_code(locale)
        return self

    @property
    def locale(self) -> Locale:
        """(:class:`~babel.core.Locale`) The language (locale) that the text is
        written in.

        """
        return Locale.parse(self.locale_code)

    def __repr__(self) -> str:
        altrepr = '({0}:) {1!s}'.format(self.locale_code, self)
        return '{0!r}[{1}:]'.format(altrepr, len(self.locale_code) + 4)


def normalize_locale_code(locale: Union[Locale, str]) -> str:
    """Determine the normalized locale code string.

    >>> normalize_locale_code('ko-kr')
    'ko_KR'
    >>> normalize_locale_code('zh_TW')
    'zh_Hant_TW'
    >>> normalize_locale_code(Locale.parse('en_US'))
    'en_US'

    """
    if not isinstance(locale, Locale):
        locale = Locale.parse(locale.replace('-', '_'))
    return str(locale)
