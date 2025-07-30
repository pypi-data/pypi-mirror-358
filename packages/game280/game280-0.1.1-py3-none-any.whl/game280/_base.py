import asyncio
import time
from abc import ABC
from collections.abc import Callable
from typing import TYPE_CHECKING, List, Optional, Type

from game280.backends import Backend
from game280.helpers import Color, Vector2
from game280.objects import Object, ObjectContainer, PositionalObject, SizedObject

if TYPE_CHECKING:
	from game280._physics_global import Physics
	from game280.resources import Resource


class BaseClass(ABC):
	game: "Game"

	def __init__(self, game: "Game"):
		self.game = game


class Clock(BaseClass):
	"""
	A clock for the game.

	Tries to keep the game running at the specified FPS, measuring the delta time.

	Args:
		game: The game the clock belongs to
			fps: The target FPS
	"""

	_last_tick: Optional[float]

	fps: int
	"""The target FPS."""

	def __init__(self, game: "Game", fps: int):
		super().__init__(game)
		self._last_tick = None
		self.fps = fps

	def tick(self) -> float:
		"""
		Tick the clock

		Returns:
			The delta time
		"""
		# Backends can have their own clock implementation (e.g. Pygame has it's own clock)
		backend_impl_result = self.game.backend.tick(self.fps)
		if backend_impl_result is not None:
			return backend_impl_result

		now = time.time()
		if self._last_tick is None:
			self._last_tick = now

		delta: float = 0

		while delta < 1 / self.fps:
			now = time.time()
			delta = now - self._last_tick
		self._last_tick = now
		return delta


class Camera(PositionalObject):
	"""
	A camera. Each Scene must have exactly one Camera.
	"""

	def __init__(self, parent: ObjectContainer, position: Optional[Vector2] = None):
		"""
		Creates a new Camera.

		Args:
			parent: The parent object
			position: The position of the camera, defaults to the center of the parent object
		"""
		super().__init__(parent, position=Vector2.ZERO)
		if position is None:
			if isinstance(parent, Scene):
				position = self.game.screen_size / 2
			elif isinstance(parent, SizedObject):
				position = parent.size / 2
			else:
				raise Exception(
					"When no position is given, Camera must be a direct child of a Scene or a SizedObject"
				)
		self.position = position
		if self.scene.camera is not None:
			raise Exception("Scene must have exactly one Camera")
		self.scene.camera = self


class Scene(Object):
	"""
	A scene. Basically, you have Scene-s in a Game and can switch them.
	A scene that is not the current scene is not processed.
	"""

	camera: Optional[Camera]
	_physics: Optional["Physics"]

	def __init__(self, game: "Game", /):
		"""
		Creates a new Scene.

		Args:
			game: The game the scene belongs to
		"""
		super().__init__(game)
		if game.current_scene is None:
			game.current_scene = self
		self.camera = None
		self._physics = None

	def init_physics(self, **kwargs):
		"""Initializes the physics engine for this scene."""
		from game280._physics_global import Physics

		Physics(self, **kwargs)

	if TYPE_CHECKING:
		physics: "Physics"
	else:
		@property
		def physics(self) -> "Physics":
			"""Returns the physics engine that belongs to this scene."""
			if self._physics is None:
				self.init_physics()
			assert self._physics is not None
			return self._physics

	def update(self, delta):
		"""Updates the scene"""
		if self.game.current_scene != self:
			return
		if self.camera is None:
			raise Exception("Scene must have exactly one Camera")
		super().update(delta)

	def render(self, delta):
		"""Renders the scene"""
		if self.game.current_scene != self:
			return
		super().render(delta)


class Game(ObjectContainer):
	"""The game. The game is the root of the object hierarchy."""

	backend: Backend
	"""The backend of the game"""

	resources: List["Resource"]
	"""The resources of the game"""

	current_scene: Optional[Scene]
	"""The current scene of the game"""

	screen_size: Vector2
	"""The size of the screen"""

	clock: Clock
	"""The clock of the game"""

	background_color: Color
	"""The background color of the game"""

	loading_screen_image: Optional["Resource"]
	"""The loading screen image of the game"""

	loading_screen_min_time: float
	"""The minimum time the loading screen should be shown"""

	_update: List[Callable[[float], None]]
	_title: str

	def __init__(
		self,
		/,
		screen_width: int,
		screen_height: int,
		backend: Type[Backend],
		background_color: Color = Color(201, 201, 201),
		loading_screen_image: Optional["Resource"] = None,
		loading_screen_min_time: float = 3.0,
		fps: int = 60,
	):
		"""
		Creates a new Game.

		Args:
			screen_width: The width of the screen
			screen_height: The height of the screen
			backend: The backend of the game
			background_color: The background color of the game
			loading_screen_image: The loading screen image of the game
			loading_screen_min_time: The minimum time the loading screen should be shown
		"""
		super().__init__()
		self.backend = backend(screen_width, screen_height)
		self.resources = []
		self.current_scene = None
		self.screen_size = Vector2(screen_width, screen_height)
		self.background_color = background_color
		self.loading_screen_image = loading_screen_image
		self.loading_screen_min_time = loading_screen_min_time
		self._update = []
		self.title = "Game280"
		self.clock = Clock(self, fps)

	async def _show_loading_screen(self):
		from game280.resources import Resource

		self.backend.renderer.fill(Color(106, 190, 48))
		if self.loading_screen_image is None:
			self.loading_screen_image = Resource(
				self, "https://romw314.com/static/game280-loading.png"
			)
		await self.loading_screen_image.load()
		self.loading_screen_image.open_as_image()
		canvas_aspect_ratio = self.screen_size.x / self.screen_size.y
		image_aspect_ratio = (
			self.loading_screen_image.image.width
			/ self.loading_screen_image.image.height
		)
		if image_aspect_ratio > canvas_aspect_ratio:
			image_size = Vector2(
				self.screen_size.x, int(self.screen_size.x / image_aspect_ratio)
			)
			image_position = Vector2(0, (self.screen_size.y - image_size.y) / 2)
		else:
			image_size = Vector2(
				int(self.screen_size.y * image_aspect_ratio), self.screen_size.y
			)
			image_position = Vector2((self.screen_size.x - image_size.x) / 2, 0)
		self.backend.renderer.image(
			self.loading_screen_image,
			Vector2.ZERO,
			Vector2(
				self.loading_screen_image.image.width,
				self.loading_screen_image.image.height,
			),
			image_position,
			image_size,
			0,
		)
		self.backend.renderer.render()

	@property
	def title(self):
		"""The title of the window"""
		return self._title

	@title.setter
	def title(self, value):
		self._title = value
		self.backend.set_window_title(value)

	def update(self, delta: float):
		"""Updates the game"""
		self.backend.renderer.fill(self.background_color)
		super().update(delta)
		for func in self._update:
			func(delta)
		self.render(delta)
		self.backend.renderer.render()

	async def _load_and_run_async(self):
		await self._show_loading_screen()
		tasks = []
		for resource in self.resources:
			tasks.append(resource.load())
		future = asyncio.gather(
			*tasks, self.load(), asyncio.sleep(self.loading_screen_min_time)
		)
		while not future.done():
			await self.backend.pre_frame(0)
			await asyncio.sleep(0)
			self.backend.renderer.render()
		await self._run()

	def load_and_run(self):
		"""Loads all resources in the game and runs it"""
		if self.current_scene is None:
			raise Exception("Game must have at least one Scene")
		self.backend.start_async(self._load_and_run_async())

	def global_update(self, func: Callable[[float], None]):
		"""Registers a global update function"""
		self._update.append(func)
		return func

	async def _run(self):
		while True:
			delta = self.clock.tick()
			await self.backend.pre_frame(delta)
			self.update(delta)
