import pymunk

from game280.objects import ObjectContainer, SceneObject


class Physics(SceneObject):
	space: pymunk.Space
	world_scale: float
	step_time: float
	_delta: float

	def __init__(self, parent: ObjectContainer, /, world_scale: float = 64.0, **kwargs):
		super().__init__(parent)
		if self.scene._physics is not None:
			raise Exception("Physics already initialized")
		self.scene._physics = self
		self.space = pymunk.Space(threaded=True)
		self.space.threads = 2
		self.world_scale = world_scale
		self.step_time = 0.01

	def update(self, delta):
		super().update(delta)
		self._delta += delta
		while self._delta > self.step_time:
			self.space.step(self.step_time)
			self._delta -= self.step_time
