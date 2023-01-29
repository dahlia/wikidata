from typing import Optional

from .entity import Entity

__all__ = 'Quantity',


class Quantity:
    """A Quantity value represents a decimal number, together with information
    about the uncertainty interval of this number, and a unit of measurement.
    """

    amount = None  # type: float
    lower_bound = None  # type: Optional[float]
    upper_bound = None  # type: Optional[float]
    unit = None  # type: Optional[Entity]

    def __init__(self,
                 amount: float,
                 lower_bound: Optional[float],
                 upper_bound: Optional[float],
                 unit: Optional[Entity]) -> None:
        self.amount = amount
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.unit = unit

    def __eq__(self, other) -> bool:
        if not isinstance(other, type(self)):
            raise TypeError(
                'expected an instance of {0.__module__}.{0.__qualname__}, '
                'not {1!r}'.format(type(self), other)
            )
        return (other.amount == self.amount and
                other.lower_bound == self.lower_bound and
                other.upper_bound == self.upper_bound and
                other.unit == self.unit)

    def __hash__(self):
        return hash((self.amount,
                     self.lower_bound,
                     self.upper_bound,
                     self.unit))

    def __repr__(self) -> str:
        return ('{0.__module__}.{0.__qualname__}({1!r}, '
                '{2!r}, {3!r}, {4!r})').format(
                    type(self),
                    self.amount,
                    self.lower_bound,
                    self.upper_bound,
                    self.unit
                )
