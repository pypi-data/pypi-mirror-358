def is_game(obj: object):
	return obj.__class__.__name__ == "Game"


def is_scene(obj: object):
	return obj.__class__.__name__ == "Scene"
