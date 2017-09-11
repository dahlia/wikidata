import json
from typing import Iterable
import urllib.request

from babel.core import Locale
from pytest import raises

from .mock import ENTITY_FIXTURES_PATH
from wikidata.client import Client
from wikidata.entity import Entity, EntityId, EntityType
from wikidata.multilingual import MultilingualText


def test_entity_equality(fx_client_opener: urllib.request.OpenerDirector,
                         fx_client: Client,
                         fx_loaded_entity: Entity):
    # When entity id and client are the same
    assert fx_loaded_entity is fx_client.get(fx_loaded_entity.id)
    assert fx_loaded_entity == fx_client.get(fx_loaded_entity.id)
    assert hash(fx_loaded_entity) == hash(fx_client.get(fx_loaded_entity.id))
    # When entity id differs
    assert fx_loaded_entity is not fx_client.get(EntityId('Q1299'))
    assert fx_loaded_entity != fx_client.get(EntityId('Q1299'))
    assert hash(fx_loaded_entity) != hash(fx_client.get(EntityId('Q1299')))
    # When client differs
    client = Client(opener=fx_client_opener)
    assert fx_loaded_entity is not client.get(fx_loaded_entity.id)
    assert fx_loaded_entity != client.get(fx_loaded_entity.id)
    assert hash(fx_loaded_entity) != hash(client.get(fx_loaded_entity.id))


def test_entity_label(fx_loaded_entity: Entity,
                      fx_unloaded_entity: Entity):
    assert isinstance(fx_loaded_entity.label, MultilingualText)
    assert fx_loaded_entity.label[Locale.parse('ko')] == '신중현'
    assert fx_loaded_entity.label[Locale.parse('zh_Hant')] == '申重鉉'
    assert isinstance(fx_unloaded_entity.label, MultilingualText)
    assert fx_unloaded_entity.label[Locale.parse('en')] == 'The Beatles'
    assert fx_unloaded_entity.label[Locale.parse('ko')] == '비틀즈'


def test_entity_description(fx_loaded_entity: Entity,
                            fx_unloaded_entity: Entity):
    assert isinstance(fx_loaded_entity.description, MultilingualText)
    assert fx_loaded_entity.description[Locale.parse('ko')] == \
        '대한민국의 록 음악 싱어송라이터 및 기타리스트'
    assert fx_loaded_entity.description[Locale.parse('ja')] == \
        '韓国のロックミュージシャン'
    assert isinstance(fx_unloaded_entity.description, MultilingualText)
    assert fx_unloaded_entity.description[Locale.parse('en')] == \
        'English rock band'
    assert fx_unloaded_entity.description[Locale.parse('ko')] == \
        '영국의 락 밴드'


def test_entity_label_description_three_chars_lang_codes(fx_client: Client):
    """As a short-term workaround, we currently ignore language codes
    ISO 639-1 doesn't cover.

    See also: https://github.com/dahlia/wikidata/issues/2

    """
    cbk_zam = fx_client.get(EntityId('Q33281'), load=True)
    assert isinstance(cbk_zam.label, MultilingualText)
    assert cbk_zam.label[Locale.parse('ko')] == '차바카노어'
    assert 'cbk-zam' not in cbk_zam.label
    assert 'cbk_zam' not in cbk_zam.label
    assert isinstance(cbk_zam.description, MultilingualText)
    assert cbk_zam.description[Locale.parse('en')] == \
        'Spanish-based creole language spoken in the Philippines'
    assert 'cbk-zam' not in cbk_zam.description
    assert 'cbk_zam' not in cbk_zam.description


def test_entity_type(fx_item: Entity,
                     fx_property: Entity,
                     fx_client_opener: urllib.request.OpenerDirector):
    assert fx_item.type == EntityType.item
    assert fx_property.type == EntityType.property
    guess_client = Client(opener=fx_client_opener, entity_type_guess=True)
    item = guess_client.get(EntityId('Q494290'))
    prop = guess_client.get(EntityId('P434'))
    assert item.type == EntityType.item
    assert item.data is None  # entity data shouldn't be loaded
    assert prop.type == EntityType.property
    assert prop.data is None  # entity data shouldn't be loaded
    noguess_client = Client(opener=fx_client_opener, entity_type_guess=False)
    item = noguess_client.get(EntityId('Q494290'))
    prop = noguess_client.get(EntityId('P434'))
    assert item.type == EntityType.item
    assert item.data is not None
    assert item.data['type'] == 'item'
    assert prop.type == EntityType.property
    assert prop.data is not None
    assert prop.data['type'] == 'property'


def test_entity_mapping(fx_client: Client,
                        fx_loaded_entity: Entity):
    occupation = fx_client.get(EntityId('P106'))
    musicbrainz_id = fx_client.get(EntityId('P434'))
    singer = fx_client.get(EntityId('Q177220'))
    instagram_username = fx_client.get(EntityId('P2003'))
    assert len(fx_loaded_entity) == 13
    expected_ids = {
        'P19', 'P21', 'P27', 'P31', 'P106', 'P136', 'P345', 'P434', 'P569',
        'P646', 'P1303', 'P1728', 'P1953'
    }
    expected = {fx_client.get(EntityId(pid)) for pid in expected_ids}
    assert set(fx_loaded_entity) == expected
    assert musicbrainz_id in fx_loaded_entity
    assert (fx_loaded_entity[musicbrainz_id] ==
            fx_loaded_entity.get(musicbrainz_id) ==
            fx_loaded_entity.get(musicbrainz_id, ...) ==
            '3eb63662-a02c-4d2d-9544-845cd92fd4e7')
    assert (fx_loaded_entity.getlist(musicbrainz_id) ==
            ['3eb63662-a02c-4d2d-9544-845cd92fd4e7'])
    assert occupation in fx_loaded_entity
    assert (fx_loaded_entity[occupation] ==
            fx_loaded_entity.get(occupation) ==
            fx_loaded_entity.get(occupation, ...) ==
            singer)
    assert (fx_loaded_entity.getlist(occupation) ==
            [singer, fx_client.get(EntityId('Q753110'))])
    assert instagram_username not in fx_loaded_entity
    with raises(KeyError):
        fx_loaded_entity[instagram_username]
    assert fx_loaded_entity.get(instagram_username) is None
    assert fx_loaded_entity.get(instagram_username, ...) is ...
    assert fx_loaded_entity.getlist(instagram_username) == []
    assert (dict(fx_loaded_entity.iterlists()) ==
            dict(fx_loaded_entity.lists()) ==
            {p: fx_loaded_entity.getlist(p) for p in expected})

    def sorted_list(v: Iterable) -> list:
        return list(sorted(v, key=str))
    assert (sorted_list(fx_loaded_entity.iterlistvalues()) ==
            sorted_list(fx_loaded_entity.listvalues()) ==
            sorted_list(fx_loaded_entity.getlist(p) for p in expected))


def test_entity_attributes(fx_unloaded_entity: Entity,
                           fx_loaded_entity: Entity):
    for entity in fx_unloaded_entity, fx_loaded_entity:
        filename = '{}.json'.format(entity.id)
        with (ENTITY_FIXTURES_PATH / filename).open('r') as f:
            assert entity.attributes == json.load(f)['entities'][entity.id]


def test_entity_load(fx_unloaded_entity: Entity):
    fx_unloaded_entity.load()
    with (ENTITY_FIXTURES_PATH / 'Q1299.json').open('r') as f:
        assert fx_unloaded_entity.data == json.load(f)['entities']['Q1299']


def test_entity_load_redirected_entity(fx_client: Client,
                                       fx_redirected_entity: Entity):
    canonical_id = EntityId('Q3571994')
    alternate_id = EntityId('Q16231742')
    assert fx_redirected_entity.id == alternate_id
    fx_redirected_entity.load()
    assert fx_redirected_entity.id == canonical_id


def test_entity_repr(fx_unloaded_entity: Entity,
                     fx_loaded_entity: Entity):
    assert repr(fx_unloaded_entity) == '<wikidata.entity.Entity Q1299>'
    assert repr(fx_loaded_entity) == \
        "<wikidata.entity.Entity Q494290 'Shin Jung-hyeon'>"
