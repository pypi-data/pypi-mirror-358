from game280 import Camera, Game, Scene
from game280.backends.pygame import PygameBackend
from game280.helpers import Vector2
from game280.objects import SizedObject
from game280.physics import (
	BodyType,
	BoxShape,
	PhysicsAngleMapper,
	PhysicsBody,
)
from game280.renderers import SpriteRenderer
from game280.resources import Resource

game = Game(640, 480, backend=PygameBackend)
scene = Scene(game)
camera = Camera(scene)


# Add an object at position 0, 0 (top left corner of the screen) with size 64x64 pixels
player = SizedObject(scene, position=Vector2(0, 0), size=Vector2(64, 64))


# Add a resource for our player image to the game
player_image = Resource(game, "https://romw314.com/static/player64.png")
# Add a renderer to the player
SpriteRenderer(player, player_image)


# Add a resource
platform_image = Resource(game, "https://romw314.com/static/box64.png")


# Create our own object type
class Platform(SizedObject):
	def __init__(self, parent, /, position, size):
		super().__init__(parent, position=position, size=size)

		# Add a renderer
		SpriteRenderer(self, platform_image)

		body = PhysicsBody(self, body_type=BodyType.STATIC)
		BoxShape(body, topleft=Vector2(0, 0), bottomright=size)


# Add platforms
Platform(scene, position=Vector2(-128, 128), size=Vector2(256, 64))
Platform(scene, position=Vector2(128, 64), size=Vector2(256, 64))


player_body = PhysicsBody(player, body_type=BodyType.DYNAMIC)
BoxShape(player_body, topleft=Vector2(0, 0), bottomright=Vector2(64, 64))


game.load_and_run()
