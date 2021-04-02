"""."""
import math
from time import perf_counter

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
