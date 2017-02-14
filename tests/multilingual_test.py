import functools

from babel.core import Locale  # type: ignore
from pytest import fixture, raises

from wikidata.multilingual import MultilingualText, normalize_locale_code


@fixture
def fx_multilingual_text() -> MultilingualText:
    return MultilingualText({
        'ko-kr': '윤동주',
        'ja_JP': '尹東柱',
        'zh_Hans': '尹东柱',
        Locale.parse('en_US'): 'Yun Dong-ju',
    })


def test_multilingual_text_mapping(fx_multilingual_text: MultilingualText):
    mt = fx_multilingual_text
    ko = functools.partial(Locale.parse, 'ko_KR')
    ja = functools.partial(Locale.parse, 'ja_JP')
    zh = functools.partial(Locale.parse, 'zh_Hans')
    en = functools.partial(Locale.parse, 'en_US')
    assert set(mt) == {ko(), ja(), zh(), en()}
    assert len(mt) == 4
    assert ko() in mt
    assert ja() in mt
    assert zh() in mt
    assert en() in mt
    assert Locale.parse('ko_KP') not in mt
    assert Locale.parse('zh_Hant') not in mt
    assert Locale.parse('en_GB') not in mt
    assert mt[ko()] == mt.get(ko()) == '윤동주'
    assert mt[ja()] == mt.get(ja()) == '尹東柱'
    assert mt[zh()] == mt.get(zh()) == '尹东柱'
    assert mt[en()] == mt.get(en()) == 'Yun Dong-ju'
    with raises(KeyError):
        mt[Locale.parse('ko_KP')]
    assert mt.get(Locale.parse('ko_KP')) is None
    with raises(KeyError):
        mt[Locale.parse('zh_Hant')]
    assert mt.get(Locale.parse('zh_Hant')) is None
    with raises(KeyError):
        mt[Locale.parse('en_GB')]
    assert mt.get(Locale.parse('en_GB')) is None


def test_multilingual_text_str(fx_multilingual_text: MultilingualText):
    assert str(fx_multilingual_text) == 'Yun Dong-ju'
    assert str(MultilingualText({})) == ''


def test_multilingual_text_repr(fx_multilingual_text: MultilingualText):
    assert repr(fx_multilingual_text) == "m'Yun Dong-ju'"
    assert repr(MultilingualText({})) == \
        "wikidata.multilingual.MultilingualText({})"


def test_normalize_locale_code():
    assert normalize_locale_code('ko-kr') == 'ko_KR'
    assert normalize_locale_code('zh_TW') == 'zh_Hant_TW'
    assert normalize_locale_code(Locale.parse('en_US')) == 'en_US'
