from dataclasses import dataclass

from coordinates import Coordinate


class Color(Coordinate):
    default_order = "rgb"


@dataclass(unsafe_hash=True, eq=True)
class JoPColor:
    color: Color


@dataclass(unsafe_hash=True, eq=True)
class JoPPureColor(JoPColor):
    position: Coordinate
    opacity: float = 1.0

    # def __eq__(self, other):
    #     return (isinstance(other, JoPPureColor) and
    #             self.color == other.color and self.opacity == other.opacity)


@dataclass(unsafe_hash=True, eq=True)
class JoPMixedColor(JoPColor):
    colors: list[JoPPureColor]

    # def __eq__(self, other):
    #     return isinstance(other, JoPMixedColor) and self.colors == other.colors
