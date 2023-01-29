from .entity import Entity

__all__ = 'GlobeCoordinate',


class GlobeCoordinate:
    """
    Literal data for a geographical position given as a latitude-longitude pair
    in gms or decimal degrees for the given stellar body.
    """

    latitude = None  # type: float
    longitude = None  # type: float
    globe = None  # type: Entity
    precision = None  # type: float

    def __init__(self,
                 latitude: float,
                 longitude: float,
                 globe: Entity,
                 precision: float) -> None:
        self.latitude = latitude
        self.longitude = longitude
        self.globe = globe
        self.precision = precision

    def __eq__(self, other) -> bool:
        if not isinstance(other, type(self)):
            raise TypeError(
                'expected an instance of {0.__module__}.{0.__qualname__}, '
                'not {1!r}'.format(type(self), other)
            )
        return (other.latitude == self.latitude and
                other.longitude == self.longitude and
                other.globe == self.globe and
                other.precision == self.precision)

    def __hash__(self):
        return hash((self.longitude,
                     self.latitude,
                     self.globe,
                     self.precision))

    def __repr__(self) -> str:
        return ('{0.__module__}.{0.__qualname__}({1!r}, '
                '{2!r}, {3!r}, {4!r})').format(
                    type(self),
                    self.latitude,
                    self.longitude,
                    self.globe,
                    self.precision
                )
