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
		self.__delta = core.get_delta_time()

		# everyone registered to get a callback...
		self.__callback = None

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

	def callback(self, who):
		self.__callback = self.__callback or []
		self.__callback.append(who)

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
		delta = core.get_delta_time()

		print(self.__head, self.__direction, delta)

		# we are stepping through the timeline frames...
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

		if self.__callback is None:
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



			for cmd in self.__callback:
				cmd(widget, {f'{attr}': value})

class ExampleAnimator():
	def __init__(self):
		core.set_vsync(False)
		core.set_style_item_spacing(1, 1)

		self.__timeline = Timeline()
		self.__timeline.callback(self.__timelineRender)
		self.__fps = 0

		cmds = {
			'<<': lambda: self.__timeline.seek(0),
			'<-': lambda: self.__timeline.play(-1),
			'||': self.__timeline.stop,
			'->': lambda: self.__timeline.play(1),
			'>>': lambda: self.__timeline.seek(-1),
			'@@': self.__timeline.loop
		}

		_width = 60
		_size = len(cmds.keys()) * _width

		with simple.window("main"):
			with simple.group("MediaBar"):
				with simple.group("Shuttle"):
					for k, v in cmds.items():
						core.add_button(f"Shuttle#{k}", label=k, width=_width, height=25, callback=v)
						core.add_same_line()
					core.add_text("ShuttleFPS")
				core.add_drag_float("MediabarIndex", label="", width=_size, callback=self.__cbSeek)

			core.add_color_button("TEST BUTTON", [255, 255, 255], width=400, height=400)

		self.__timeline.keyEdit("TEST BUTTON", 'width', 0, 400)
		self.__timeline.keyEdit("TEST BUTTON", 'width', 2., 10)
		self.__timeline.keyEdit("TEST BUTTON", 'width', 3.75, 400)

		core.set_render_callback(self.__render)

	def __timelineRender(self, widget, data):
		core.configure_item(widget, **data)

	def __render(self, sender, data):
		self.__timeline.render()
		self.__fps = 1. / core.get_delta_time()
		core.set_value('ShuttleFPS', int(self.__fps))
		core.set_value('MediabarIndex', self.__timeline.index)

	def __cbSeek(self, sender, data):
		# get the time index of sender, and set the _TIMELINE.seek()
		print(sender, data)
		self.__timeline.seek(data)

if __name__ == "__main__":
	ExampleAnimator()
	core.start_dearpygui(primary_window="main")
