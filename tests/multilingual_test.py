from pytest import fixture

from wikidata.multilingual import Locale, MonolingualText, MultilingualText


@fixture
def fx_multilingual_text() -> MultilingualText:
    return MultilingualText({
        'ko': '윤동주',
        'ja': '尹東柱',
        'zh-hans': '尹东柱',
        'en': 'Yun Dong-ju',
    })


def test_multilingual_text_mapping(fx_multilingual_text: MultilingualText):
    mt = fx_multilingual_text
    assert set(mt) == {"ko", "ja", "zh-hans", "en"}
    assert len(mt) == 4
    assert Locale("ko") in mt
    assert Locale("ja") in mt
    assert Locale("zh-hans") in mt
    assert Locale("en") in mt
    assert Locale("ko-kp") not in mt
    assert Locale("zh-hant") not in mt
    assert Locale("en-gb") not in mt
    assert mt[Locale("ko")] == mt.get("ko") == '윤동주'
    assert mt[Locale("ja")] == mt.get("ja") == '尹東柱'
    assert mt[Locale("zh-hans")] == mt.get("zh-hans") == '尹东柱'
    assert mt[Locale("en")] == mt.get("en") == 'Yun Dong-ju'
    assert mt.get("ko-kp") is None
    assert mt.get('zh-hant') is None
    assert mt.get('en-gb') is None


def test_multilingual_text_str(fx_multilingual_text: MultilingualText):
    assert str(fx_multilingual_text) == 'Yun Dong-ju'
    assert str(MultilingualText({})) == ''


def test_multilingual_text_repr(fx_multilingual_text: MultilingualText):
    assert repr(fx_multilingual_text) == "m'Yun Dong-ju'"
    assert repr(MultilingualText({})) == \
        "wikidata.multilingual.MultilingualText({})"


def test_monolingual_text_locale():
    a = MonolingualText('윤동주', 'ko')
    assert a.locale == 'ko'
    c = MonolingualText('周樹人', 'zh-hant')
    assert c.locale == 'zh-hant'


def test_monolingual_text_repr():
    a = MonolingualText('윤동주', 'ko')
    assert repr(a) == "'(ko:) 윤동주'[6:]"
    assert eval(repr(a)) == str(a)
    b = MonolingualText('周樹人', 'zh-hant')
    assert repr(b) == "'(zh-hant:) 周樹人'[11:]"
    assert eval(repr(b)) == str(b)
