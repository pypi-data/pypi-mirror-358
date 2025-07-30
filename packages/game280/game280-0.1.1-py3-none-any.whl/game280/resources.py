import asyncio
import io
from typing import Optional
from uuid import uuid4

from PIL import Image

from game280._base import BaseClass, Game


class Resource(BaseClass):
	image: Optional[Image.Image]
	id: str
	_loader: Optional[asyncio.Task[None]]
	path: str

	def __init__(self, game: Game, path: str):
		super().__init__(game)
		game.resources.append(self)

		self.id = str(uuid4())
		self.path = path

		self.image = None
		self._loader = None

	async def _load(self):
		data = self.game.backend.load_resource(self.path)
		if isinstance(data, bytes):
			self.data = data
		else:
			self.data = await data

	def load(self) -> asyncio.Task[None]:
		if self._loader is None:
			self._loader = asyncio.create_task(self._load())

		return self._loader

	def open_as_image(self):
		self.image = Image.open(io.BytesIO(self.data))
		self.image.load()
		self.image = self.image.convert("RGBA")
