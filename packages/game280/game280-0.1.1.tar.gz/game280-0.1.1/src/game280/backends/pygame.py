import asyncio
import math
import sys
from typing import Dict, Optional, Tuple

import aiohttp
import pygame

from game280.backends import Backend, Input, Renderer
from game280.helpers import Color, Vector2


def _convert_color(color: Color) -> pygame.Color:
	return pygame.Color(color.r, color.g, color.b, color.a)


class PygameRenderer(Renderer):
	image_map: Dict[
		Tuple[str, int, int, int, int, int, int, float], Tuple[pygame.Surface, int, int]
	]

	def __init__(self, width, height):
		self.width = width
		self.height = height
		self.init_screen()
		self.canvas = pygame.Surface((width, height), pygame.SRCALPHA)
		self.image_map = {}

	def init_screen(
		self, width: Optional[int] = None, height: Optional[int] = None, flags: int = 0
	):
		if width is None:
			width = self.width
		if height is None:
			height = self.height
		self.screen = pygame.display.set_mode(
			(width, height), pygame.SRCALPHA | pygame.RESIZABLE | flags
		)

	def render(self):
		canvas_aspect_ratio = self.width / self.height
		screen_aspect_ratio = self.screen.get_size()[0] / self.screen.get_size()[1]
		if canvas_aspect_ratio > screen_aspect_ratio:
			dest_size = (
				self.screen.get_size()[0],
				int(self.screen.get_size()[0] / canvas_aspect_ratio),
			)
			dest_position = (0, (self.screen.get_size()[1] - dest_size[1]) / 2)
		else:
			dest_size = (
				int(self.screen.get_size()[1] * canvas_aspect_ratio),
				self.screen.get_size()[1],
			)
			dest_position = ((self.screen.get_size()[0] - dest_size[0]) / 2, 0)
		resized_canvas = pygame.transform.scale(self.canvas, dest_size)
		self.screen.fill("black")
		self.screen.blit(resized_canvas, dest_position)
		pygame.display.flip()

	def set_size(self, width, height):
		super().set_size(width, height)
		self.screen = pygame.display.set_mode((width, height), pygame.SRCALPHA)
		self.canvas = pygame.Surface((width, height), pygame.SRCALPHA)

	def fill(self, color):
		self.canvas.fill(_convert_color(color))

	def rect(self, rect, outline, fill, outline_width=1):
		surface = pygame.Surface(self.canvas.get_size(), pygame.SRCALPHA)
		surface.fill((0, 0, 0, 0))
		surface.fill(
			_convert_color(fill),
			(rect.position.x, rect.position.y, rect.size.x, rect.size.y),
		)
		pygame.draw.lines(
			self.canvas,
			_convert_color(outline),
			True,
			[
				(rect.position.x, rect.position.y),
				(rect.position.x, rect.position.y + rect.size.y),
				(rect.position.x + rect.size.x, rect.position.y + rect.size.y),
				(rect.position.x + rect.size.x, rect.position.y),
			],
			outline_width,
		)
		self.canvas.blit(surface, (0, 0))

	def line(self, start, end, color, width=1):
		pygame.draw.line(
			self.canvas,
			_convert_color(color),
			(start.x, start.y),
			(end.x, end.y),
			width,
		)

	def image(
		self, image, source_position, source_size, dest_position, dest_size, dest_angle
	):
		im_entry = (
			image.id,
			source_position.x,
			source_position.y,
			source_size.x,
			source_size.y,
			dest_size.x,
			dest_size.y,
			dest_angle,
		)
		if im_entry not in self.image_map:
			source_image = pygame.image.frombytes(
				image.image.tobytes(), image.image.size, image.image.mode
			)
			dest_image = pygame.Surface((source_size.x, source_size.y), pygame.SRCALPHA)
			dest_image.blit(
				source_image,
				(0, 0),
				(source_position.x, source_position.y, source_size.x, source_size.y),
			)
			rotated_image = pygame.transform.rotate(
				dest_image, dest_angle * 180 / math.pi
			)
			render_offset_x = source_size.x / 2 - rotated_image.get_width() / 2
			render_offset_y = source_size.y / 2 - rotated_image.get_height() / 2
			resized_image = pygame.transform.scale(
				rotated_image,
				(dest_size.x - render_offset_x * 2, dest_size.y - render_offset_y * 2),
			)
			self.image_map[im_entry] = (resized_image, render_offset_x, render_offset_y)
		else:
			resized_image, render_offset_x, render_offset_y = self.image_map[im_entry]
		self.canvas.blit(
			resized_image,
			resized_image.get_rect(
				topleft=(
					dest_position.x + render_offset_x,
					dest_position.y + render_offset_y,
				)
			),
		)


class PygameInput(Input):
	def __init__(self):
		pygame.joystick.init()

	def get_key(self, key):
		return pygame.key.get_pressed()[pygame.key.key_code(key)]

	def get_mouse_position(self):
		return Vector2(*pygame.mouse.get_pos())

	def get_gamepad_button(self, button, gamepad=0):
		return pygame.joystick.Joystick(gamepad).get_button(int(button))

	def get_gamepad_axis(self, axis, gamepad=0):
		return pygame.joystick.Joystick(gamepad).get_axis(axis)


class PygameBackend(Backend):
	renderer: PygameRenderer
	clock: Optional[pygame.time.Clock]
	aiohttp_session: Optional[aiohttp.ClientSession]

	def __init__(self, width: int, height: int):
		self.renderer = PygameRenderer(width, height)
		self.input = PygameInput()
		self.clock = None
		self.fullscreen = False
		self.aiohttp_session = None

	def set_fullscreen(self, fullscreen):
		if fullscreen == self.fullscreen:
			return
		self.fullscreen = fullscreen
		if self.fullscreen:
			self.renderer.init_screen(0, 0, flags=pygame.FULLSCREEN)
		else:
			self.renderer.init_screen()

	def set_window_title(self, title):
		pygame.display.set_caption(title)

	def start_async(self, func):
		asyncio.run(func)

	def load_resource(self, path):
		if path.startswith("res://"):
			return open("res/" + path[len("res://") :], "rb").read()
		else:
			return self._load_resource_aiohttp(path)

	async def _load_resource_aiohttp(self, url):
		if self.aiohttp_session is None:
			self.aiohttp_session = aiohttp.ClientSession()
		async with self.aiohttp_session.get(url) as resp:
			data = await resp.content.read()
		return data

	async def pre_frame(self, delta):
		if delta > 0 and self.aiohttp_session is not None:
			await self.aiohttp_session.close()
			self.aiohttp_session = None
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()

	def tick(self, fps):
		if self.clock is None:
			self.clock = pygame.time.Clock()
		return self.clock.tick(fps) / 1000
