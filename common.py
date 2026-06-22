from dataclasses import dataclass

from coordinates import Coordinate


class Color(Coordinate):
    default_order = "rgb"


@dataclass
class JoPColor:
    color: Color


@dataclass
class JoPPureColor(JoPColor):
    position: Coordinate


@dataclass
class JoPMixedColor(JoPColor):
    color1: JoPColor
    color2: JoPColor
    opacity: float
