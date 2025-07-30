from enum import IntEnum
from numbers import Number
from typing import TYPE_CHECKING, Self, Tuple

import vectors  # type: ignore[import-untyped]
from classproperties import classproperty  # type: ignore[import-untyped]


class Vector2(vectors.Vector2):
	@classproperty
	def ZERO(cls) -> Self:
		return cls(0, 0)

	@classproperty
	def ONE(cls) -> Self:
		return cls(1, 1)

	if TYPE_CHECKING:
		from game280.helpers import Vector2

		ZERO: Self = Vector2(0, 0)  # type: ignore[no-redef]
		ONE: Self = Vector2(1, 1)  # type: ignore[no-redef]
		del Vector2

		def __init__(self, x: float, y: float): ...

	x: float
	y: float

	def clone(self) -> Self:
		return Vector2(self.x, self.y)

	def __add__(self, other: Self) -> Self:
		new = self.clone()
		new.add(other)
		return new

	def __sub__(self, other: Self) -> Self:
		new = self.clone()
		new.subtract(other)
		return new

	def __mul__(self, other: Self | float) -> Self:
		if isinstance(other, Number):
			return Vector2(self.x * other, self.y * other)  # type: ignore[operator]
		new = self.clone()
		new.multiply(other)
		return new

	def __floordiv__(self, other: Self | float) -> Self:
		if isinstance(other, Number):
			return Vector2(self.x // other, self.y // other)  # type: ignore[operator]
		return Vector2(self.x // other.x, self.y // other.y)  # type: ignore[union-attr]

	def __div__(self, other: Self | float) -> Self:
		return self // other

	def __truediv__(self, other: Self | float) -> Self:
		if isinstance(other, Number):
			return Vector2(self.x / other, self.y / other)  # type: ignore[operator]
		return self * Vector2(1 / other.x, 1 / other.y)  # type: ignore[union-attr]

	def __eq__(self, other: object) -> bool:
		if not isinstance(other, Vector2):
			return NotImplemented
		return self.x == other.x and self.y == other.y

	def __repr__(self):
		return f"Vector2({self.x}, {self.y})"


class Color:
	TRANSPARENT: "Color"
	BLACK: "Color"
	WHITE: "Color"
	RED: "Color"
	ORANGE: "Color"
	YELLOW: "Color"
	GREEN: "Color"
	CYAN: "Color"
	BLUE: "Color"
	MAGENTA: "Color"
	PURPLE: "Color"

	def __init__(self, r: int, g: int, b: int, a: int = 255):
		self.r = r
		self.g = g
		self.b = b
		self.a = a

	def tuple(self) -> Tuple[int, int, int, int]:
		return self.r, self.g, self.b, self.a

	def list(self) -> list[int]:
		return [self.r, self.g, self.b, self.a]

	def __repr__(self):
		return f"Color({self.r}, {self.g}, {self.b}, {self.a})"


Color.TRANSPARENT = Color(0, 0, 0, 0)
Color.BLACK = Color(0, 0, 0)
Color.WHITE = Color(255, 255, 255)
Color.RED = Color(255, 0, 0)
Color.ORANGE = Color(255, 128, 0)
Color.YELLOW = Color(255, 255, 0)
Color.GREEN = Color(0, 255, 0)
Color.CYAN = Color(0, 255, 255)
Color.BLUE = Color(0, 0, 255)
Color.MAGENTA = Color(255, 0, 255)
Color.PURPLE = Color(128, 0, 255)


class Rect:
	position: Vector2
	size: Vector2

	def __init__(self, position: Vector2, size: Vector2):
		self.position = position
		self.size = size

	def __repr__(self):
		return f"Rect(position={self.position}, size={self.size})"


class GamepadButton(IntEnum):
	A = 0
	B = 1
	X = 2
	Y = 3
	LeftBumper = 4
	RightBumper = 5
	LeftTrigger = 6
	RightTrigger = 7
	Select = 8
	Start = 9
	LeftStick = 10
	RightStick = 11
	Up = 12
	Down = 13
	Left = 14
	Right = 15
	Guide = 16


class GamepadAxis(IntEnum):
	LeftX = 0
	LeftY = 1
	RightX = 2
	RightY = 3
