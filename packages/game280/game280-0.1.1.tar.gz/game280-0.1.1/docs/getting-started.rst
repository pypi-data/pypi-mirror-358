Getting Started
===============

In this tutorial, we'll create a simple platformer with game280.


First, we need to install game280::

	pip install game280

Then, create a file named ``main.py`` and add the following content::

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


	game.load_and_run()

Then, run the game::

	python main.py

Blank screen? Add this before ``game.load_and_run()``::

	# Add an object at position 0, 0 (top left corner of the screen) with size 64x64 pixels
	player = SizedObject(scene, position=Vector2(0, 0), size=Vector2(64, 64))

Test your game. Blank screen again? We need a renderer::

	# Add a resource for our player image to the game
	player_image = Resource(game, "https://romw314.com/static/player64.png")
	# Add a renderer to the player
	SpriteRenderer(player, player_image)

Test your game again. Ok, now we have a player, we need some platforms.

Of course, we could create a platform like the player::

	# Add an object
	platform = SizedObject(scene, position=Vector2(-128, 128), size=Vector2(256, 64))
	# Add a renderer
	SpriteRenderer(platform, platform_image)

.. TODO: complete tutorial
