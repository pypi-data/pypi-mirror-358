"""Base classes for all backends"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Awaitable, Optional

from game280.helpers import Color, GamepadAxis, GamepadButton, Rect, Vector2

if TYPE_CHECKING:
	from game280.resources import Resource


class Renderer(ABC):
	width: int
	height: int

	def __init__(self, width: int, height: int):
		self.set_size(width, height)

	def set_size(self, width: int, height: int):
		self.width = width
		self.height = height

	@abstractmethod
	def fill(self, color: Color): ...

	@abstractmethod
	def rect(self, rect: Rect, outline: Color, fill: Color, outline_width: int = 1): ...

	@abstractmethod
	def line(self, start: Vector2, end: Vector2, color: Color, width: int = 1): ...

	@abstractmethod
	def image(
		self,
		image: "Resource",
		source_position: Vector2,
		source_size: Vector2,
		dest_position: Vector2,
		dest_size: Vector2,
		dest_angle: float = 0.0,
	): ...

	def render(self): ...


class Input(ABC):
	@abstractmethod
	def get_key(self, key: str) -> bool:
		"""Returns True if the specified key is pressed"""
		...

	@abstractmethod
	def get_mouse_position(self) -> Vector2:
		"""Returns the mouse position"""
		...

	@abstractmethod
	def get_gamepad_button(self, button: GamepadButton, gamepad: int = 0) -> bool:
		"""Returns True if the specified gamepad button is pressed"""
		...

	@abstractmethod
	def get_gamepad_axis(self, axis: GamepadAxis, gamepad: int = 0) -> float:
		"""Returns the value of the specified gamepad axis"""
		...


class Backend(ABC):
	"""The base class for all backends"""

	renderer: Renderer
	"""The renderer for the backend"""

	input: Input
	"""The input for the backend"""

	@abstractmethod
	def __init__(self, width: int, height: int):
		"""Initializes the backend. Should set the renderer and input."""
		...

	@abstractmethod
	def set_fullscreen(self, fullscreen: bool):
		"""Sets the fullscreen status of the window"""
		...

	@abstractmethod
	def set_window_title(self, title: str):
		"""Sets the title of the window"""
		...

	@abstractmethod
	def load_resource(self, path: str) -> bytes | Awaitable[bytes]:
		"""Loads a resource. Should support at least res://, http:// and https:// protocols."""
		...

	@abstractmethod
	def start_async(self, func: Awaitable[None]):
		"""Starts an asynchronous function. In most cases, this should use asyncio.run()."""
		...

	async def pre_frame(self, delta: float):
		"""Called before each frame"""
		...

	def tick(self, fps: int) -> Optional[int]:
		"""Use this to provide a custom clock implementation. Return None to use the default implementation."""
		...
