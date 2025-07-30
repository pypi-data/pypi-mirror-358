from game280 import Camera, Game, Scene
from game280.backends.pygame import PygameBackend
from game280.helpers import Vector2
from game280.objects import Object, SizedObject
from game280.physics import (
	BodyType,
	BoxShape,
	CircleShape,
	PhysicsAngleMapper,
	PhysicsBody,
)
from game280.renderers import SpriteRenderer
from game280.resources import Resource


def main():
	# A minimal Game280 physics example
	#
	# In Game280, there is a tree of objects, with each object having a parent,
	# except for the Game. The Game is the root of the tree, and all other objects
	# are children of the Game.
	#
	# In the Game, there are Scene-s. There must be at least one Scene in the Game.
	# One of those is the current Scene and others are not processed.
	#
	# Each Scene must have a Camera. Object-s are rendered relative to the Camera.
	#
	# So, the simplest object tree looks like this:
	#
	# Game
	#   Scene
	#     Camera
	#
	# However, that'll only render the background color, so let's add some objects.
	#
	# The ObjectContainer class has children Object-s, but doesn't have a parent.
	#
	# The Object class is the base class for all objects. It has a parent, which is
	# a reference to the ObjectContainer that contains it. It is a subclass of ObjectContainer.
	#
	# A SceneObject is an Object that must be in a Scene.
	#
	# The PositionalObject is a SceneObject with a position, so it can be
	# moved around and rendered at it's position. However, it doesn't have a size,
	# so we more frequently use SizedObject. SizedObject is a PositionalObject with a size.
	#
	# Object-s (not PositionalObject-s) are frequently used as "behaviors", which
	# only do something with their parent. Good examples are Renderer-s. Renderers
	# render an image at the position of the parent onto the screen. For example,
	# the SpriteRenderer just renders a given image at the position of the parent.
	#
	# But renderers aren't useful without images. The game contains Resource-s,
	# which load files. The SpriteRenderer needs a Resource for the image.
	# Resource-s aren't Object-s, so they don't have children.
	#
	# And finally, let's explain physics. There are PhysicsBody-s (they are behaviors),
	# which should be children of SizedObject-s. Then, the SizedObject-s
	# have gravity, forces, etc. There are also Shape-s (CircleShape-s, BoxShape-s),
	# which should be children of PhysicsBody-s and specify the shape of the body.
	#
	# So, the class hierarchy looks like this:
	#
	# ObjectContainer
	#   Game
	#   Object
	#     PhysicsBody
	#     Shape
	#       BoxShape
	#       CircleShape
	#     Renderer
	#       SpriteRenderer
	#       TilingRenderer
	#       NineSliceRenderer
	#     Scene
	#     SceneObject
	#       PositionalObject
	#         SizedObject
	#       Camera
	# Resource

	# Create the game
	game = Game(800, 600, backend=PygameBackend)

	# Load images
	box_image = Resource(game, "https://romw314.com/static/box64.png")
	ball_image = Resource(game, "https://romw314.com/static/ball64.png")

	# Create a scene
	scene = Scene(game)

	# Add a camera to the scene
	Camera(scene)

	# Create our own "behavior" object that destroys it's parent when it goes out of the screen
	class DeleteWhenOutOfScreen(Object):
		# The update function is called every frame
		def update(self, delta):
			# If the parent is out of the screen
			if (
				self.parent.screen_position.x < 0
				or self.parent.screen_position.x > self.game.screen_size.x
				or self.parent.screen_position.y < 0
				or self.parent.screen_position.y > self.game.screen_size.y
			):
				# Destroy the parent
				self.parent.destroy()

	def create_box(x_offset):
		# Create the object
		obj = SizedObject(
			scene, position=Vector2(368 + x_offset, -64), size=Vector2(64, 64)
		)
		# Add a physics body
		body = PhysicsBody(obj)
		# Add a shape
		BoxShape(body)
		# Add a renderer to render the image
		renderer = SpriteRenderer(obj, box_image)
		# Add an angle mapper to render the image at the correct angle
		PhysicsAngleMapper(body, renderer)

	# Create a ball
	ball = SizedObject(scene, position=Vector2(368, 512), size=Vector2(64, 64))
	# Add a physics body
	static_body = PhysicsBody(ball, body_type=BodyType.STATIC)
	# Add a shape
	CircleShape(static_body, radius=32, density=0.1)
	# Add a renderer
	SpriteRenderer(ball, ball_image)

	# Create 2 new boxes every 0.7 seconds
	box_creating_interval = 0.7

	# Keep track of time
	time = 0

	# We define a global update function that is called every frame but doesn't belong to any object
	@game.global_update
	def global_update(delta):
		nonlocal time

		# Delta is the time since the last frame, in seconds

		# Update time
		time += delta

		# If it's time to create new boxes
		if time // box_creating_interval > (time - delta) // box_creating_interval:
			# Create 2 new boxes
			create_box(42)
			create_box(-42)

	# Start the game
	game.load_and_run()


if __name__ == "__main__":
	main()
