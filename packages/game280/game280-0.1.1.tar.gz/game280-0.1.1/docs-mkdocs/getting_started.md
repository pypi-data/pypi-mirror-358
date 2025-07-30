# Getting Started

In this tutorial, we'll create a simple platformer game with Game280.

For project management, you can use [uv](https://docs.astral.sh/uv/) (recommended), [Poetry](https://python-poetry.org/), [PDM](https://pdm-project.org/) or no project manager at all.

First, we need to create a project:

=== "uv"

	```sh
	uv init --name my_platformer --no-package --bare
	```

=== "Poetry"

	```sh
	poetry init -n --name=my_platformer
	```

=== "PDM"

	```sh
	pdm init -n --no-git
	```

=== "No project manager"

	```sh
	python -m virtualenv .venv
	. .venv/bin/activate
	```

Then, we, of course, need to install Game280, and since we are going to use the Pygame backend, we are going to install Game280 with the `pygame` extra:

=== "uv"

	```sh
	uv add game280[pygame,box2d]
	```

=== "Poetry"

	```sh
	poetry add game280[pygame,box2d]
	```

=== "PDM"

	```sh
	pdm add game280[pygame,box2d]
	```

=== "No project manager"

	```sh
	pip install game280[pygame,box2d]
	pip freeze > requirements.txt
	```

Then, create a file named `main.py`, and add the following content:

```python
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
```

Then, start the game with the following command:

=== "uv"

	```sh
	uv run main.py
	```

=== "Poetry"

	```sh
	poetry run python main.py
	```

=== "PDM"

	```sh
	pdm run main.py
	```

=== "No project manager"

	```sh
	python main.py
	```

And this is your game. Blank screen. We need to add some objects to the scene. Add this to `main.py` before `game.load_and_run()`:

```python
# Add an object at position 0, 0 (top left corner of the screen) with size 64x64 pixels
player = SizedObject(scene, position=Vector2(0, 0), size=Vector2(64, 64))
```

Test your game. Blank screen again? Sure, that's right. We need a renderer:

```python
# Add a resource for our player image to the game
player_image = Resource(game, "https://romw314.com/static/player64.png")
# Add a renderer to the player
SpriteRenderer(player, player_image)
```

Test your game again. Ok, now we have a player, we need some platforms.

Of course, we could create a platform like the player:

```python
# Add an object
platform = SizedObject(scene, position=Vector2(-128, 128), size=Vector2(256, 64))
# Add a renderer
SpriteRenderer(platform, platform_image)
```

And repeat this for every platform. But there is a better way. We could of course create a function, but how about creating our own object type named `Platform` and use it instead of a [`SizedObject`][game280.objects.SizedObject] with a [`SpriteRenderer`][game280.renderers.SpriteRenderer].

So, let's create an object type. Object types are basically Python classes that inherit from [`Object`][game280.objects.Object]. But we can also inherit from [`SizedObject`][game280.objects.SizedObject]:

```python
# Add a resource
platform_image = Resource(game, "https://romw314.com/static/box64.png")


# Create our own object type
class Platform(SizedObject):
	def __init__(self, parent, /, position, size):
		super().__init__(parent, position=position, size=size)

		# Add a renderer
		SpriteRenderer(self, platform_image)
```

Now add some platforms:

```python
# Add platforms
Platform(scene, position=Vector2(-128, 128), size=Vector2(256, 64))
Platform(scene, position=Vector2(128, 64), size=Vector2(256, 64))
```

Test your game. Ok, we have a player, we have platforms, but the player doesn't fall. How about using a physics engine? Add this to the end of `Platform`'s `__init__`:

```python
body = PhysicsBody(self, body_type=BodyType.STATIC)
BoxShape(body)
```

And add this before `game.load_and_run()`:

```python
player_body = PhysicsBody(player, body_type=BodyType.DYNAMIC)
BoxShape(player_body)
```

<!-- TODO: complete tutorial -->
