import asyncio
from typing import TYPE_CHECKING, List

from game280._utils import is_game, is_scene
from game280.helpers import Vector2

if TYPE_CHECKING:
	from game280._base import Game, Scene


class ObjectContainer:
	"""A container for objects"""

	_objects: List["Object"]

	def __init__(self):
		"""Creates a new ObjectContainer"""
		self._objects = []

	def __iter__(self):
		return iter(self._objects)

	def __len__(self):
		return len(self._objects)

	def __getitem__(self, index):
		return self._objects[index]

	def __contains__(self, item):
		return item in self._objects

	def update(self, delta: float):
		"""Updates all objects inside the container"""
		for obj in self._objects:
			obj.update(delta)

	def render(self, delta: float):
		"""Renders all objects inside the container"""
		for obj in self._objects:
			obj.render(delta)

	async def load(self):
		"""Loads all objects inside the container"""
		tasks = []
		for obj in self._objects:
			tasks.append(obj.load())
		await asyncio.gather(*tasks)


class Object(ObjectContainer):
	"""An object. This is the base class for all objects and behaviors in the game."""

	parent: "ObjectContainer"
	"""The parent object"""

	game: "Game"
	"""The game the object belongs to"""

	destroyable: bool = False
	"""Whether the object can be destroyed"""

	def __init__(self, parent: "ObjectContainer", /):
		"""Creates a new Object"""
		super().__init__()
		self.parent = parent
		parent._objects.append(self)

		game: ObjectContainer = self
		while not is_game(game):
			if not isinstance(game, Object):
				raise Exception("Object must be a child of a Game")
			game = game.parent
		if TYPE_CHECKING:
			assert isinstance(game, Game)
		self.game = game

	def destroy(self):
		"""Destroys the object"""
		if not self.__class__.destroyable:
			raise Exception("Object is not destroyable")
		for obj in self:
			obj.destroy()
		self.parent._objects.remove(self)


class SceneObject(Object):
	"""An object that must be in a Scene"""

	scene: "Scene"
	"""The scene the object belongs to"""

	def __init__(self, parent: "ObjectContainer", /):
		super().__init__(parent)

		scene: ObjectContainer = self
		while not is_scene(scene):
			if not isinstance(scene, Object):
				raise Exception("SceneObject must be a child of a Scene")
			scene = scene.parent
		if TYPE_CHECKING:
			assert isinstance(scene, Scene)
		self.scene = scene


class PositionalObject(SceneObject):
	"""An object that has a position"""

	position: Vector2
	"""The position of the object, relative to the parent object"""

	destroyable: bool = True
	"""Whether the object can be destroyed"""

	def __init__(self, parent: "ObjectContainer", /, position: Vector2):
		"""Creates a new PositionalObject"""
		super().__init__(parent)
		self.position = position

	@property
	def x(self) -> float:
		"""The x position of the object"""
		return self.position.x

	@x.setter
	def x(self, value: float):
		self.position.x = value

	@property
	def y(self) -> float:
		"""The y position of the object"""
		return self.position.y

	@y.setter
	def y(self, value: float):
		self.position.y = value

	@property
	def world_position(self) -> Vector2:
		"""The absolute position of the object"""
		result = Vector2(0, 0)
		curr: ObjectContainer = self
		while isinstance(curr, Object):
			if isinstance(curr, PositionalObject):
				result.add(curr.position)
			curr = curr.parent
		return result

	@world_position.setter
	def world_position(self, value: Vector2):
		position_delta = value - self.world_position
		self.position.add(position_delta)

	@property
	def screen_position(self) -> Vector2:
		"""The screen position of the object, relative to the top left corner of the screen"""

		assert self.scene.camera is not None

		return (
			self.world_position
			- self.scene.camera.world_position
			+ self.game.screen_size / 2
		)


class SizedObject(PositionalObject):
	"""A positional object that has a size"""

	size: Vector2
	"""The size of the object"""

	def __init__(self, parent: "ObjectContainer", /, position: Vector2, size: Vector2):
		super().__init__(parent, position=position)
		self.size = size

	@property
	def width(self) -> float:
		"""The width of the object"""
		return self.size.x

	@width.setter
	def width(self, value: float):
		self.size.x = value

	@property
	def height(self) -> float:
		"""The height of the object"""
		return self.size.y

	@height.setter
	def height(self, value: float):
		self.size.y = value

	@property
	def center(self) -> Vector2:
		"""The center position of the object"""
		return self.position + self.size / 2
