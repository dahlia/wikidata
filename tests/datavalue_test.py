import datetime
from typing import Dict, cast

from pytest import mark, raises

from wikidata.client import Client
from wikidata.commonsmedia import File
from wikidata.datavalue import DatavalueError, Decoder
from wikidata.entity import Entity, EntityId
from wikidata.globecoordinate import GlobeCoordinate
from wikidata.multilingual import MonolingualText
from wikidata.quantity import Quantity


def test_datavalue_error():
    with raises(TypeError):
        DatavalueError()
    with raises(TypeError):
        DatavalueError('message')
    assert str(DatavalueError('message', {'type': 'string', 'value': '...'})) \
        == "message: {'type': 'string', 'value': '...'}"
    assert str(DatavalueError('msg', {'foo': 'bar'})) == "msg: {'foo': 'bar'}"


def test_decoder_missing_type(fx_client: Client):
    d = Decoder()
    with raises(DatavalueError):
        d(fx_client, 'string', {'value': '...'})


def test_decoder_missing_value(fx_client: Client):
    d = Decoder()
    with raises(DatavalueError):
        d(fx_client, 'string', {'type': 'string'})


def test_decoder_unsupported_type(fx_client: Client):
    d = Decoder()
    with raises(DatavalueError):
        d(fx_client, 'unsupportedtype', {'type': 'unsupport', 'value': '...'})
    with raises(DatavalueError):
        d(fx_client, 'string', {'type': 'unsupport', 'value': '...'})


@mark.parametrize('datatype', ['string', 'wikibase-item'])
def test_decoder_wikibase_entityid(datatype: str,
                                   fx_client: Client,
                                   fx_loaded_entity: Entity):
    d = Decoder()
    with raises(DatavalueError):
        d(
            fx_client, datatype,
            {'type': 'wikibase-entityid', 'value': 'not mapping'}
        )
    with raises(DatavalueError):
        d(
            fx_client, datatype,
            {'type': 'wikibase-entityid', 'value': {}}  # no id
        )
    decoded = d(
        fx_client, datatype,
        {'type': 'wikibase-entityid', 'value': {'id': fx_loaded_entity.id}}
    )
    assert decoded is fx_loaded_entity


@mark.parametrize('datatype', ['string', 'external-id'])
def test_decoder_string(datatype: str, fx_client: Client):
    d = Decoder()
    assert d(fx_client, datatype,
             {'type': 'string', 'value': 'foobar'}) == 'foobar'


@mark.parametrize('datatype', ['time', 'string'])
def test_decoder__time(datatype: str, fx_client: Client):
    d = Decoder()
    valid_value = {
        'calendarmodel': 'http://www.wikidata.org/entity/Q1985727',
        'time': '+2017-02-22T02:53:12Z',
        'timezone': 0, 'before': 0, 'after': 0, 'precision': 14,
    }
    valid = {'type': 'time', 'value': valid_value}

    def other_value(**kwargs) -> Dict[str, object]:
        value = dict(valid_value, **cast(Dict[str, object], kwargs))
        return dict(valid, value={
            k: v for k, v in value.items() if v is not None
        })
    assert (datetime.date(2017, 2, 22) ==
            d(fx_client, datatype, other_value(precision=11)))
    assert 2017 == d(fx_client, datatype, other_value(precision=9))
    utc = datetime.timezone.utc
    assert (datetime.datetime(2017, 2, 22, 2, 53, 12, tzinfo=utc) ==
            d(fx_client, datatype, valid))
    with raises(DatavalueError):
        d(fx_client, datatype, dict(valid, value='not mapping'))
    with raises(DatavalueError):
        d(fx_client, datatype, other_value(calendarmodel=None))
        # no calendarmodel field
    with raises(DatavalueError):
        d(fx_client, datatype, other_value(time=None))
        # no time field
    with raises(DatavalueError):
        d(
            fx_client, datatype,
            other_value(calendarmodel='unspported calendar model')
        )
    with raises(DatavalueError):
        d(fx_client, datatype, other_value(time='-2017-02-22T02:53:12Z'))
        # only AD (CE) time is supported
    with raises(DatavalueError):
        d(fx_client, datatype, other_value(timezone=None))
        # timezone field is missing
    with raises(DatavalueError):
        d(fx_client, datatype, other_value(timezone=60))
        # timezone field should be 0
    with raises(DatavalueError):
        d(fx_client, datatype, other_value(after=None))
        # after field is missing
    with raises(DatavalueError):
        d(fx_client, datatype, other_value(before=None))
        # before field is missing
    with raises(DatavalueError):
        d(fx_client, datatype, other_value(after=60))
        # after field (other than 0) is unsupported
    with raises(DatavalueError):
        d(fx_client, datatype, other_value(before=60))
        # before field (other than 0) is unsupported
    with raises(DatavalueError):
        d(fx_client, datatype, other_value(precision=None))
        # precision field is missing
    for p in range(1, 15):
        if p in (9, 11, 14):
            continue
        with raises(DatavalueError):
            d(fx_client, datatype, other_value(precision=p))
            # precision (other than 11 or 14) is unsupported


def test_decoder_monolingualtext(fx_client: Client):
    d = Decoder()
    assert d(fx_client, 'monolingualtext', {
        'type': 'monolingualtext',
        'value': {
            'language': 'ko',
            'text': '윤동주',
        },
    }) == MonolingualText('윤동주', 'ko')


def test_decoder_commonsMedia__string(fx_client: Client):
    d = Decoder()
    f = d(fx_client, 'commonsMedia',
          {'value': 'The Fabs.JPG', 'type': 'string'})
    assert isinstance(f, File)
    assert f.title == 'File:The Fabs.JPG'


def test_decoder_quantity_with_unit(fx_client: Client):
    d = Decoder()
    decoded = d(fx_client, 'quantity', {
        'value': {
            "amount": "+610.13",
            "lower_bound": "+610.12",
            "upper_bound": "+610.14",
            "unit": "http://www.wikidata.org/entity/Q828224"
        },
        'type': 'quantity'
    })
    gold = Quantity(
        amount=610.13,
        lower_bound=610.12,
        upper_bound=610.14,
        unit=fx_client.get(EntityId("Q828224")))
    assert decoded == gold


def test_decoder_quantity_unitless(fx_client: Client):
    d = Decoder()
    decoded = d(fx_client, 'quantity', {
        'value': {
            "amount": "+12",
            "unit": "1"
        },
        'type': 'quantity'
    })
    gold = Quantity(
        amount=12,
        lower_bound=None,
        upper_bound=None,
        unit=None)
    assert decoded == gold


def test_decoder_globecoordinate(fx_client: Client):
    d = Decoder()
    decoded = d(fx_client, 'globe-coordinate', {
        'value': {
            "latitude": 70.1525,
            "longitude": 70.1525,
            "precision": 0.0002777777777777778,
            "globe": "http://www.wikidata.org/entity/Q111"
        },
        'type': 'globecoordinate'
    })
    gold = GlobeCoordinate(70.1525,
                           70.1525,
                           fx_client.get(EntityId("Q111")),
                           0.0002777777777777778,)
    assert decoded == gold
