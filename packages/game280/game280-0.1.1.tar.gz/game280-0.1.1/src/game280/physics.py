from abc import ABCMeta, abstractmethod
from enum import IntEnum

import pymunk

from game280.helpers import Vector2
from game280.objects import Object, SceneObject, SizedObject
from game280.renderers import SpriteRenderer


def _convert_vector(vector: Vector2):
	return pymunk.Vec2d(vector.x, -vector.y)


def _anti_convert_vector(vector: pymunk.Vec2d):
	return Vector2(vector.x, -vector.y)


class BodyType(IntEnum):
	STATIC = pymunk.Body.STATIC
	KINEMATIC = pymunk.Body.KINEMATIC
	DYNAMIC = pymunk.Body.DYNAMIC


class PhysicsBody(SceneObject):
	parent: SizedObject
	body: pymunk.Body

	def __init__(self, parent: SizedObject, /, body_type: BodyType = BodyType.DYNAMIC):
		super().__init__(parent)
		self.body = pymunk.Body(body_type=body_type.value)
		self.scene.physics.space.add(self.body)
		self.body.position = self.parent.world_position.tuple()

	def update(self, delta):
		super().update(delta)
		self.parent.world_position = (
			_anti_convert_vector(self.body.position) * self.scene.physics.world_scale
			- self.parent.size / 2
		)

	def destroy(self):
		super().destroy()
		self.scene.physics.world.DestroyBody(self.body)


class PhysicsAngleMapper(Object):
	parent: PhysicsBody
	renderer: SpriteRenderer

	def __init__(self, parent: PhysicsBody, renderer: SpriteRenderer, /):
		super().__init__(parent)
		self.renderer = renderer

	def update(self, delta):
		super().update(delta)
		self.renderer.angle = self.parent.body.angle


class Shape(SceneObject, metaclass=ABCMeta):
	parent: PhysicsBody
	shape: pymunk.Shape

	@abstractmethod
	def __init__(
		self,
		parent: PhysicsBody,
		/,
		friction: float = 0.0,
		density: float = 1.0,
		restitution: float = 0.0,
	):
		super().__init__(parent)

	def _add_shape(self):
		self.scene.physics.space.add(self.shape)


class CircleShape(Shape):
	def __init__(
		self,
		parent: PhysicsBody,
		/,
		radius: float,
		offset: Vector2 = Vector2.ZERO,
		friction=0.0,
		density=1.0,
		restitution=0.0,
	):
		"""
		Args:
			parent: The parent object.
			radius: The radius of the circle.
			offset: The offset of the circle from the center of the parent object.
			friction: The friction of the circle.
			density: The density of the circle.
			restitution: The restitution of the circle.
		"""
		super().__init__(parent, friction, density, restitution)
		pymunk.Circle(
			parent.body,
			radius / self.scene.physics.world_scale,
			(offset / self.scene.physics.world_scale).tuple(),
		)
		self._add_shape()


class BoxShape(Shape):
	def __init__(
		self,
		parent: PhysicsBody,
		/,
		topleft: Vector2,
		bottomright: Vector2,
		friction=0.0,
		density=1.0,
		restitution=0.0,
	):
		"""
		Args:
			parent: The parent object.
			topleft: The top left corner of the box, relative to the position of the parent object.
			bottomright: The bottom right corner of the box, relative to the position of the parent object.
			friction: The friction of the box.
			density: The density of the box.
			restitution: The restitution of the box.
		"""
		super().__init__(parent, friction, density, restitution)
		top = (
			topleft.y - self.parent.parent.size.y / 2
		) / -self.scene.physics.world_scale
		bottom = (
			bottomright.y - self.parent.parent.size.y / 2
		) / -self.scene.physics.world_scale
		left = (
			topleft.x - self.parent.parent.size.x / 2
		) / self.scene.physics.world_scale
		right = (
			bottomright.x - self.parent.parent.size.x / 2
		) / self.scene.physics.world_scale
		self.shape = pymunk.Poly(
			parent.body, [(top, left), (top, right), (bottom, right), (bottom, left)]
		)
		self._add_shape()
