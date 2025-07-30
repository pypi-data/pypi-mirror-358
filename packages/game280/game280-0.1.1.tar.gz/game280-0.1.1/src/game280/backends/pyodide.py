import asyncio
import io
from typing import Any

import js  # type: ignore
from pyodide.code import run_js  # type: ignore
from pyodide.ffi import create_proxy  # type: ignore

from game280.backends import Backend, Input, Renderer
from game280.helpers import Color, GamepadAxis, GamepadButton, Vector2


class PyodideRenderer(Renderer):
	canvas: js.HTMLCanvasElement
	image_map: dict[str, Any]

	def __init__(self, width, height):
		super().__init__(width, height)
		self.screen = js.document.createElement("canvas")
		self.canvas = js.document.createElement("canvas")
		js.document.body.appendChild(self.screen)
		self.screen.style.position = "fixed"
		js.addEventListener("resize", create_proxy(lambda _: self._resize()))
		self.screen_context = self.canvas.getContext("2d")
		self.screen_context.imageSmoothingEnabled = False
		self.context = self.canvas.getContext("2d")
		self.context.imageSmoothingEnabled = False
		self._resize()

	def _resize(self):
		self.screen.width = js.innerWidth
		self.screen.height = js.innerHeight

	def render(self):
		self.screen_context.drawImage(
			self.canvas, 0, 0, self.screen.width, self.screen.height
		)

	def _set_colors(self, outline: Color, fill: Color):
		self.context.strokeStyle = (
			f"rgba({outline.r}, {outline.g}, {outline.b}, {outline.a})"
		)
		self.context.fillStyle = f"rgba({fill.r}, {fill.g}, {fill.b}, {fill.a})"

	def set_size(self, width, height):
		super().set_size(width, height)
		self.canvas.width = width
		self.canvas.height = height

	def fill(self, color: Color):
		self._set_colors(Color.TRANSPARENT, color)
		self.context.fillRect(0, 0, self.width, self.height)

	def rect(self, rect, outline, fill):
		self._set_colors(outline, fill)
		self.context.beginPath()
		self.context.rect(rect.position.x, rect.position.y, rect.size.x, rect.size.y)
		self.context.stroke()
		self.context.fill()

	def line(self, start, end, color, width=1):
		self._set_colors(color, Color.TRANSPARENT)
		self.context.lineWidth = width
		self.context.beginPath()
		self.context.moveTo(start.x, start.y)
		self.context.lineTo(end.x, end.y)
		self.context.stroke()

	def image(
		self,
		image,
		source_position,
		source_size,
		dest_position,
		dest_size,
		dest_angle=0,
	):
		pngio = io.BytesIO()
		image.image.save(pngio, format="png")
		pngio.seek(0)
		if image.id not in self.image_map:
			js._game280_imid = image.id
			loading_status = run_js("""
				(function() {
					if (!('_game280_imageloaders' in window)) window._game280_imageloaders = {};
					if (!(window._game280_imid in window._game280_imageloaders)) return 0;
					if ('result' in window._game280_imageloaders[window._game280_imid]) return 2;
					return 1;
				})()
			""")
			if loading_status == 1:
				return
			if loading_status == 2:
				self.image_map[image.id] = run_js(
					"window._game280_imageloaders[window._game280_imid].result"
				)
			else:
				assert loading_status == 0
				js._game280_image = pngio.read()
				self.image_map[image.id] = run_js(
					"createImageBitmap(new Blob([_game280_image.toJs()], {type: 'image/png'})).then(function(im) { window._game280_imageloaders[window._game280_imid].result = im; })"
				)

		self.context.drawImage(
			self.image_map[image.id],
			source_position.x,
			source_position.y,
			source_size.x,
			source_size.y,
			dest_position.x,
			dest_position.y,
			dest_size.x,
			dest_size.y,
		)


class PyodideInput(Input):
	BUTTON_MAP = {
		"FACE_1": GamepadButton.A,
		"FACE_2": GamepadButton.B,
		"FACE_3": GamepadButton.X,
		"FACE_4": GamepadButton.Y,
		"LEFT_SHOULDER": GamepadButton.LeftBumper,
		"RIGHT_SHOULDER": GamepadButton.RightBumper,
		"LEFT_SHOULDER_BOTTOM": GamepadButton.LeftTrigger,
		"RIGHT_SHOULDER_BOTTOM": GamepadButton.RightTrigger,
		"SELECT": GamepadButton.Select,
		"START": GamepadButton.Start,
		"LEFT_ANALOG_BUTTON": GamepadButton.LeftStick,
		"RIGHT_ANALOG_BUTTON": GamepadButton.RightStick,
		"DPAD_UP": GamepadButton.Up,
		"DPAD_DOWN": GamepadButton.Down,
		"DPAD_LEFT": GamepadButton.Left,
		"DPAD_RIGHT": GamepadButton.Right,
		"HOME": GamepadButton.Guide,
	}

	AXIS_MAP = {
		"LEFT_ANALOG_STICK": (GamepadAxis.LeftX, GamepadAxis.LeftY),
		"RIGHT_ANALOG_STICK": (GamepadAxis.RightX, GamepadAxis.RightY),
	}

	_keys: set[str]

	_gamepad_buttons: dict[int, dict[GamepadButton, int]]
	_gamepad_axes: dict[int, dict[GamepadAxis, float]]

	def __init__(self, backend: "PyodideBackend"):
		backend.renderer.canvas.addEventListener(
			"keydown", create_proxy(lambda e: self._keydown(e.key))
		)
		backend.renderer.canvas.addEventListener(
			"keyup", create_proxy(lambda e: self._keyup(e.key))
		)
		backend.renderer.canvas.addEventListener(
			"mousedown", create_proxy(lambda e: self._mousedown(e.button))
		)
		backend.renderer.canvas.addEventListener(
			"mouseup", create_proxy(lambda e: self._mouseup(e.button))
		)
		backend.renderer.canvas.addEventListener(
			"mousemove", create_proxy(lambda e: self._mousemove(e.offsetX, e.offsetY))
		)
		js.Controller.search()
		button_updater = create_proxy(lambda e: self._gamepad_button_update(e.detail))
		js.addEventListener("gc.button.hold", button_updater)
		js.addEventListener("gc.button.release", button_updater)
		js.addEventListener(
			"gc.analog.change",
			create_proxy(lambda e: self._gamepad_axis_update(e.detail)),
		)
		self._keys = set()
		self._gamepad_buttons = {}
		self._gamepad_axes = {}

	def _keydown(self, key: str):
		self._keys.add(key)

	def _keyup(self, key: str):
		self._keys.discard(key)

	def get_key(self, key):
		return key in self._keys

	def _mousedown(self, button: int):
		raise NotImplementedError

	def _mouseup(self, button: int):
		raise NotImplementedError

	def _mousemove(self, x: int, y: int):
		self._mouse_position = Vector2(x, y)

	def _gamepad_button_update(self, button: Any):
		gamepad: int = button.controllerIndex
		if gamepad not in self._gamepad_buttons:
			self._gamepad_buttons[gamepad] = {}
		self._gamepad_buttons[gamepad][self.BUTTON_MAP[button.name]] = button.value

	def get_mouse_position(self):
		return self._mouse_position

	def get_gamepad_button(self, button, gamepad=0):
		return (
			0
			if gamepad not in self._gamepad_buttons
			or button not in self._gamepad_buttons[gamepad]
			else self._gamepad_buttons[gamepad][button]
		)

	def _gamepad_axis_update(self, axis: Any):
		gamepad: int = axis.controllerIndex
		if gamepad not in self._gamepad_axes:
			self._gamepad_axes[gamepad] = {}
		xAxis, yAxis = self.AXIS_MAP[axis.name]
		self._gamepad_axes[gamepad][xAxis] = axis.position.x
		self._gamepad_axes[gamepad][yAxis] = axis.position.y

	def get_gamepad_axis(self, axis, gamepad=0):
		return (
			0
			if gamepad not in self._gamepad_axes
			or axis not in self._gamepad_axes[gamepad]
			else self._gamepad_axes[gamepad][axis]
		)


class PyodideBackend(Backend):
	renderer: PyodideRenderer

	def __init__(self, width: int, height: int):
		self.renderer = PyodideRenderer(width, height)
		self.input = PyodideInput(self)

	def set_window_title(self, title):
		js.document.title = title

	def start_async(self, func):
		asyncio.run(func)

	async def load_resource(self, path):
		if path.startswith("res://"):
			return await js.fetch("res/" + path[len("res://") :])
		return await js.fetch(path)

	async def pre_frame(self, _):
		await asyncio.sleep(0)
