from game280.helpers import Vector2
from game280.objects import Object, ObjectContainer, SizedObject
from game280.resources import Resource


class Renderer(Object):
	pass


class SpriteRenderer(Renderer):
	image: Resource
	parent: SizedObject
	angle: float

	def __init__(
		self,
		parent: ObjectContainer,
		image: Resource,
		/,
		angle: float = 0.0,
		preload: bool = True,
	):
		if not isinstance(parent, SizedObject):
			raise Exception("SpriteRenderer must be a direct child of a SizedObject")
		super().__init__(parent)
		self.image = image
		self.angle = angle
		self.preload = preload

	async def load(self):
		await super().load()
		await self.image.load()
		if self.preload and self.image.image is None:
			self.image.open_as_image()

	def render(self, delta: float):
		super().update(delta)
		if self.image.image is None:
			self.image.open_as_image()
		assert self.image.image is not None
		self.game.backend.renderer.image(
			self.image,
			Vector2.ZERO,
			Vector2(self.image.image.width, self.image.image.height),
			self.parent.screen_position,
			self.parent.size,
			self.angle,
		)


class TilingRenderer(Renderer):
	image: Resource
	parent: SizedObject
	tile_offset: Vector2

	def __init__(
		self,
		parent: ObjectContainer,
		image: Resource,
		/,
		tile_offset: Vector2 = Vector2.ZERO,
		preload: bool = True,
	):
		if not isinstance(parent, SizedObject):
			raise Exception("TilingRenderer must be a direct child of a SizedObject")
		super().__init__(parent)
		self.image = image
		self.preload = preload
		self.tile_offset = tile_offset

	async def load(self):
		await super().load()
		await self.image.load()
		if self.preload and self.image.image is None:
			self.image.open_as_image()

	def render(self, delta: float):
		super().update(delta)
		if self.image.image is None:
			self.image.open_as_image()
		assert self.image.image is not None

		topleft_x: int
		topleft_y: int
		render_offset_y = -int(self.tile_offset.y)
		while render_offset_y < self.parent.size.y:
			if render_offset_y < 0:
				topleft_y = 0
				image_offset_y = -render_offset_y
			else:
				topleft_y = render_offset_y
				image_offset_y = 0
			image_height = min(
				self.parent.size.y - render_offset_y, self.image.image.height
			)

			render_offset_x = -int(self.tile_offset.x)
			while render_offset_x < self.parent.size.x:
				if render_offset_x < 0:
					topleft_x = 0
					image_offset_x = -render_offset_x
				else:
					topleft_x = render_offset_x
					image_offset_x = 0
				image_width = min(
					self.parent.size.x - render_offset_x, self.image.image.width
				)

				self.game.backend.renderer.image(
					self.image,
					Vector2(image_offset_x, image_offset_y),
					Vector2(image_width, image_height),
					self.parent.screen_position + Vector2(topleft_x, topleft_y),
					Vector2(image_width, image_height),
					0,
				)

				render_offset_x += self.image.image.width
			render_offset_y += self.image.image.height


class NineSliceRenderer(Renderer):
	image: Resource
	parent: SizedObject
	topleft_size: Vector2
	bottomright_size: Vector2

	def __init__(
		self,
		parent: ObjectContainer,
		image: Resource,
		/,
		topleft_size: Vector2 = Vector2.ZERO,
		bottomright_size: Vector2 = Vector2.ZERO,
		preload: bool = True,
	):
		if not isinstance(parent, SizedObject):
			raise Exception("NineSliceRenderer must be a direct child of a SizedObject")
		super().__init__(parent)
		self.image = image
		self.preload = preload
		self.topleft_size = topleft_size
		self.bottomright_size = bottomright_size

	async def load(self):
		await super().load()
		await self.image.load()
		if self.preload and self.image.image is None:
			self.image.open_as_image()

	def render(self, delta):
		super().render(delta)
		if self.image.image is None:
			self.image.open_as_image()

		# Top left
		self.game.backend.renderer.image(
			self.image,
			Vector2.ZERO,
			self.topleft_size,
			self.parent.screen_position,
			self.topleft_size,
			0,
		)

		# Top
		self.game.backend.renderer.image(
			self.image,
			Vector2(self.topleft_size.x, 0),
			Vector2(
				self.image.image.width - self.topleft_size.x - self.bottomright_size.x,
				self.topleft_size.y,
			),
			self.parent.world_position + Vector2(self.topleft_size.x, 0),
			Vector2(
				self.parent.size.x - self.topleft_size.x - self.bottomright_size.x,
				self.topleft_size.y,
			),
			0,
		)

		# Top right
		self.game.backend.renderer.image(
			self.image,
			Vector2(self.image.image.width - self.bottomright_size.x, 0),
			Vector2(self.bottomright_size.x, self.topleft_size.y),
			self.parent.world_position
			+ Vector2(self.parent.size.x - self.bottomright_size.x, 0),
			Vector2(self.bottomright_size.x, self.topleft_size.y),
			0,
		)

		# Left
		self.game.backend.renderer.image(
			self.image,
			Vector2(0, self.topleft_size.y),
			Vector2(
				self.topleft_size.x,
				self.image.image.height - self.topleft_size.y - self.bottomright_size.y,
			),
			self.parent.world_position + Vector2(0, self.topleft_size.y),
			Vector2(
				self.topleft_size.x,
				self.parent.size.y - self.topleft_size.y - self.bottomright_size.y,
			),
			0,
		)

		# Center
		self.game.backend.renderer.image(
			self.image,
			self.topleft_size,
			Vector2(self.image.image.width, self.image.image.height)
			- self.topleft_size
			- self.bottomright_size,
			self.parent.world_position + self.topleft_size,
			self.parent.size - self.topleft_size - self.bottomright_size,
			0,
		)

		# Right
		self.game.backend.renderer.image(
			self.image,
			Vector2(
				self.image.image.width - self.bottomright_size.x, self.topleft_size.y
			),
			Vector2(
				self.bottomright_size.x,
				self.image.image.height - self.topleft_size.y - self.bottomright_size.y,
			),
			self.parent.world_position
			+ Vector2(
				self.parent.size.x - self.bottomright_size.x, self.topleft_size.y
			),
			Vector2(
				self.bottomright_size.x,
				self.parent.size.y - self.topleft_size.y - self.bottomright_size.y,
			),
			0,
		)

		# Bottom left
		self.game.backend.renderer.image(
			self.image,
			Vector2(0, self.image.image.height - self.bottomright_size.y),
			Vector2(self.topleft_size.x, self.bottomright_size.y),
			self.parent.world_position
			+ Vector2(0, self.parent.size.y - self.bottomright_size.y),
			Vector2(self.topleft_size.x, self.bottomright_size.y),
			0,
		)

		# Bottom
		self.game.backend.renderer.image(
			self.image,
			Vector2(
				self.topleft_size.x, self.image.image.height - self.bottomright_size.y
			),
			Vector2(
				self.image.image.width - self.topleft_size.x - self.bottomright_size.x,
				self.bottomright_size.y,
			),
			self.parent.world_position
			+ Vector2(
				self.topleft_size.x, self.parent.size.y - self.bottomright_size.y
			),
			Vector2(
				self.parent.size.x - self.topleft_size.x - self.bottomright_size.x,
				self.bottomright_size.y,
			),
			0,
		)

		# Bottom right
		self.game.backend.renderer.image(
			self.image,
			Vector2(
				self.image.image.width - self.bottomright_size.x,
				self.image.image.height - self.bottomright_size.y,
			),
			Vector2(self.bottomright_size.x, self.bottomright_size.y),
			self.parent.world_position
			+ Vector2(
				self.parent.size.x - self.bottomright_size.x,
				self.parent.size.y - self.bottomright_size.y,
			),
			Vector2(self.bottomright_size.x, self.bottomright_size.y),
			0,
		)
