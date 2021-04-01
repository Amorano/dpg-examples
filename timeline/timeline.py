"""."""

import math
from time import perf_counter
from dearpygui import core, simple

def lerp(a, b, dist):
	if b > a:
		a, b = b, a
	return a * (1. - dist) + b * dist

class Timeline():
	def __init__(self):

		# the time entries
		self.__items = {}

		# max element last frame. Total runtime
		self.__duration = 0

		# playhead position
		self.__head = 0.

		# playback stopped
		self.__direction = 0.

		# loop playback in forward or reverse state
		self.__loop = True

		# since last frame (always caculated, even when stopped)
		self.__delta = perf_counter()

	def loop(self):
		"""Toggle looping."""
		self.__loop = not self.__loop

	@property
	def index(self):
		"""Current playhead position."""
		return self.__head

	@property
	def duration(self):
		return self.__duration

	@duration.setter
	def duration(self, value):
		top = -1
		for v in self.__items.values():
			keys = [k for k in v.keys()]
			top = max(top, keys[-1])
		self.__duration = max(top, value)

	def keyEdit(self, target: str, attr: str, timeIndex: float, value):
		"""."""
		# keys are fractional and contain the value (k,v)
		_attr = f"{target}.{attr}"
		data = self.__items.get(_attr, {})
		data[timeIndex] = value
		# sort the insert here, so its cheaper than runtime
		self.__items[_attr] = {k: data[k] for k in sorted(data.keys())}
		self.__duration = max(self.__duration, timeIndex)

	def play(self, direction: float=1.):
		"""Continue playback from head index in <- / -> direction.

		Direction can be negative for reverse playback, and can be
		greater than 1 or fractional, or stopped (0).
		"""
		self.__direction = direction

	def stop(self):
		"""Stop all playback."""
		self.__direction = 0.

	def seek(self, value: int=-1):
		"""Find frame `value`."""
		if value == -1:
			value = self.__duration
		# clamp to timeline min/max
		self.__head = max(0, min(value, self.__duration))

	def render(self):
		delta = perf_counter() - self.__delta
		self.__delta = perf_counter()
		# we are stepping through the timeline frames...
		# print(f'{self.__head} - {self.__direction}  {delta}')
		if self.__direction == 0:
			return

		# adjust the frame(s) to playback? based on last frametime?
		# for now, just play a single "frame"
		self.__head += (delta * self.__direction)

		# looping?
		if self.__head < 0:
			if self.__loop:
				self.__head += self.__duration
			else:
				self.__head = 0
				self.stop()
				return
		elif self.__head > self.__duration:
			if self.__loop:
				self.__head -= self.__duration
			else:
				self.__head = self.__duration
				self.stop()
				return

		# if we are here, we are playing back something?
		# iterating this whole block feels bad... callbacks...?
		for source, data in self.__items.items():
			widget, attr = source.split('.')
			tline = [k for k in data.keys()]
			v1 = min(tline, key=lambda k: math.floor(abs(k - self.__head)))
			# LERP?
			index1 = index2 = tline.index(v1)
			if index1 < len(tline) - 1:
				index2 = index1 + 1

			t1 = tline[index1]
			t2 = tline[index2]
			v1 = data[t1]
			v2 = data[t2]
			delta = t2 - t1
			if delta != 0:
				delta = abs(self.__head - t1) / delta

			# lerp for all things, except? string?
			singleVal = False
			if not isinstance(v1, list):
				singleVal = True
				v1 = [v1]
				v2 = [v2]
			# strings are merely held over?
			if not isinstance(v1[0], str):
				value = [lerp(v1[i], v2[i], delta) for i in range(len(v1))]
				if isinstance(v1[0], int):
					value = [int(lerp(v1[i], v2[i], delta)) for i in range(len(v1))]
				else:
					value = [lerp(v1[i], v2[i], delta) for i in range(len(v1))]
			if singleVal:
				value = value[0]
			core.configure_item(widget, **{f'{attr}': value})
			print(t1, t2, self.__head, delta, value)
			# print(t1, t2, self.__head, delta)

_TIMELINE = Timeline()
_FPS = 0

def render(sender, data):
	_TIMELINE.render()
	_FPS = 1. / core.get_delta_time()
	core.set_value('ShuttleFPS', int(_FPS))
	core.set_value('MediabarIndex', _TIMELINE.index)

def cbSeek(sender, data):
	# get the time index of sender, and set the _TIMELINE.seek()
	print(sender, data)
	_TIMELINE.seek(data)

def unittest():
	core.set_style_item_spacing(1, 1)
	cmds = {
		'<<': lambda: _TIMELINE.seek(0),
		'<-': lambda: _TIMELINE.play(-1),
		'||': _TIMELINE.stop,
		'->': lambda: _TIMELINE.play(1),
		'>>': lambda: _TIMELINE.seek(-1),
		'@@': lambda: _TIMELINE.loop()
	}

	_width = 60
	_size = len(cmds.keys()) * _width

	with simple.window("Window"):
		with simple.group("MediaBar"):
			with simple.group("Shuttle"):
				for k, v in cmds.items():
					core.add_button(f"Shuttle#{k}", label=k, width=_width, height=25, callback=v)
					core.add_same_line()
				core.add_text("ShuttleFPS")
			core.add_drag_float("MediabarIndex", label="", width=_size, callback=cbSeek)

		core.add_color_button("TEST BUTTON", [255, 255, 255], width=400, height=400)

	colors = [
		(0, [255, 0, 0, 255]),
		(.2, [196, 32, 0, 255]),
		(.4, [128, 64, 32, 255]),
		(.6, [196, 128, 64, 255]),
		(.8, [255, 255, 255, 255]),
	]

	_TIMELINE.keyEdit("TEST BUTTON", 'width', 0, 400)
	_TIMELINE.keyEdit("TEST BUTTON", 'width', 2, 100)
	_TIMELINE.keyEdit("TEST BUTTON", 'width', 3.75, 400)

	core.set_render_callback(render)
	core.start_dearpygui(primary_window="Window")
# ==============================================================================
if __name__ == "__main__":
	core.set_vsync(False)
	unittest()
