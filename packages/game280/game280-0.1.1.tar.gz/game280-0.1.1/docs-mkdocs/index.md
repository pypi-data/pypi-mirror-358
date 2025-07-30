# Game280

Yet another 2D game engine.

[Get started](./getting_started.md){: .button .green role=button}

## Features

- Object tree: in Game280, you have an object tree, with the [Game][game280.Game] being the root object, then some [Scene][game280.Scene]s in the game, a [Camera][game280.Camera] in the scene and so on.
- Scene switching: in Game280, you have multiple [Scene][game280.Scene]s of which only one is active. Other scenes aren't processed by the game engine.
- Multiple backends: there are two official backends - a [Pygame backend][game280.backends.pygame] for creating desktop games and a [Pyodide backend][game280.backends.pyodide] for creating HTML5 games. And of course, you can always create your own backend.
