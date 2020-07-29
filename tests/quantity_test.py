from pytest import fixture

from wikidata.client import Client
from wikidata.entity import Entity, EntityId
from wikidata.quantity import Quantity


@fixture
def fx_quantity_unitless() -> Quantity:
    # From Q605704 (dozen)
    return Quantity(
        amount=12,
        lower_bound=None,
        upper_bound=None,
        unit=None)


@fixture
def fx_quantity_with_unit() -> Quantity:
    client = Client()
    # From Q520
    return Quantity(
        amount=610.13,
        lower_bound=610.12,
        upper_bound=610.14,
        unit=client.get(EntityId("Q828224")))


def test_quantity_unitless_value(fx_quantity_unitless: Quantity):
    assert fx_quantity_unitless.amount == 12
    assert fx_quantity_unitless.lower_bound is None
    assert fx_quantity_unitless.upper_bound is None
    assert fx_quantity_unitless.unit is None


def test_quantity_unitless_repr(fx_quantity_unitless: Quantity):
    assert (repr(fx_quantity_unitless) ==
            ("wikidata.quantity.Quantity(12, None, None, None)"))


def test_quantity_with_unit_value(fx_quantity_with_unit: Quantity):
    assert fx_quantity_with_unit.amount == 610.13
    assert fx_quantity_with_unit.lower_bound == 610.12
    assert fx_quantity_with_unit.upper_bound == 610.14
    assert isinstance(fx_quantity_with_unit.unit, Entity)
    assert fx_quantity_with_unit.unit.id == "Q828224"


def test_quantity_with_unit_repr(fx_quantity_with_unit: Quantity):
    assert (repr(fx_quantity_with_unit) ==
            ("wikidata.quantity.Quantity(610.13, 610.12, 610.14, "
             "<wikidata.entity.Entity Q828224>)"))
