"""."""
import re
import math
import json
import os.path as path
from collections import OrderedDict
from dearpygui import core, simple
# ==============================================================================
def polar2cart(rho, theta, oldpos):
	theta = math.radians(theta)
	x = rho * math.cos(theta)
	y = rho * math.sin(theta)
	return [x + y for x, y in zip((x, y), oldpos)]

def cart2polar(x, y):
	return math.hypot(x, y), math.degrees(math.atan2(y, x))

class Fractal():
	# case-sensitive so we can use A-Z and a-z
	_reFractal = re.compile('[A-Z]')

	def __init__(self, **kw):
		self.title = kw.get('title', '')
		self.axiom = kw.get('axiom', 'F')
		self.dAngle = kw.get('angle', 60)
		self.delta = kw.get('delta', 10.)
		self.rule = kw.get('rule', {})
		self.__data = ""

	def parse(self, iteration: int=10):
		self.__data = ""
		iteration = max(1, min(13, iteration))

		def transcribe(m):
			"""Convert a character into its rule entry, if any exists."""
			k = m.group()
			# potential matches or itself
			return self.rule.get(k, k)

		ret = self.axiom
		for _ in range(iteration):
			ret = self._reFractal.sub(transcribe, ret)
		self.__data = ret

	def execute(self, theta: float=0, drawCallback=None, drawCallBufferSize: int=25):
		pos = (0, 0)
		stack = []
		drawStack = []
		for c in self.__data:
			if c in ['F', 'A']:
				newpos = polar2cart(self.delta, theta + self.dAngle, pos)
				if drawCallback:
					drawStack.extend([pos, newpos])
				pos = newpos
			elif c == 'f':
				pos = polar2cart(self.delta, theta + self.dAngle, pos)
			elif c == 'B':
				newpos = polar2cart(-self.delta, theta + self.dAngle, pos)
				if drawCallback:
					drawStack.extend([pos, newpos])
				pos = newpos
			elif c == 'b':
				pos = polar2cart(-self.delta, theta + self.dAngle, pos)
			elif c == '+':
				theta += self.dAngle
			elif c == '-':
				theta -= self.dAngle
			elif c == '[':
				stack.append((theta, pos))
			elif c == ']':
				theta, pos = stack.pop()

			if drawCallback and len(drawStack) > drawCallBufferSize:
				drawCallback(drawStack)
				drawStack = []

		# the remaining calls
		if drawCallback and len(drawStack):
			drawCallback(drawStack)

class ExampleFractalWindow():
	def __init__(self):
		core.set_vsync(False)
		core.set_style_window_padding(0, 0)

		self.__iteration = 3
		# load the data blob

		root = path.dirname(path.realpath(__file__))
		with open(f'{root}/fractal.json', 'r') as data:
			self.__fractalData = OrderedDict(json.load(data))
		self.__fractalKeys = [k for k in self.__fractalData.keys()]
		d = self.__fractalKeys[0]
		self.__fractal = Fractal(**self.__fractalData[d])
		size = core.get_main_window_size()

		with simple.window("MainWindow"):
			with simple.group("Controls"):
				core.add_input_int("Iteration", width=120, min_value=2, max_value=40, min_clamped=True, max_clamped=True,
					default_value=self.__iteration, callback=self.__cbIterationValue)
				simple.tooltip("Iteration", "How many times to re-run the pattern parser with the \
					previous runs output. Increasing this directly increases computation time.")

				with simple.group("Controls-Angle"):
					core.add_input_float("Angle", width=120, default_value=self.__fractal.dAngle, callback=self.__cbAngleValue)
					simple.tooltip("Angle", "Degrees the turtle will turn either positive or negative, when issued such commands.")
					core.add_same_line()
					core.add_checkbox("AngleAnimate", default_value=False, label="Animate")
					core.add_input_float("AngleStep", width=120, default_value=.002, step=0.001, step_fast=0.01)
					simple.tooltip("AngleStep", "Amount the animator will step through the angle.")

				core.add_input_float("Length", width=120, default_value=self.__fractal.delta, callback=self.__cbDeltaValue)
				simple.tooltip("Length", "Relative distance, forward or backward, the turtle will take when commanded.")
			core.add_same_line()
			core.add_listbox("power", label='', items=self.__fractalKeys, callback=self.__cbFractalType)
			core.add_drawing("Canvas", width=size[0] * 2, height=size[1] * 2)
		core.set_resize_callback(self.__resize)
		core.set_render_callback(self.__render)
		self.__refresh()

	def __cbFractalType(self, sender, data):
		d = core.get_value(sender)
		d = self.__fractalKeys[d]
		self.__fractal = Fractal(**self.__fractalData[d])
		core.set_value("Angle", self.__fractal.dAngle)
		self.__refresh()

	def __cbIterationValue(self, sender, data):
		iteration = core.get_value(sender)
		if iteration == self.__iteration:
			return
		core.set_value(sender, iteration)
		self.__iteration = iteration
		self.__refresh()

	def __cbAngleValue(self, sender, data):
		angle = core.get_value(sender) % 360
		core.set_value(sender, angle)
		self.__fractal.dAngle = angle
		self.__refresh(False)

	def __cbDeltaValue(self, sender, data):
		delta = max(min(20, core.get_value(sender)), .1)
		core.set_value(sender, delta)
		self.__fractal.delta = delta
		self.__refresh(False)

	def __cbFractalDraw(self, pointArray: list):
		color = [255, 255, 255, 255]
		thickness = math.log(40 / self.__iteration) * (5 / self.__fractal.dAngle)
		size = core.get_main_window_size()
		center = (size[0] * 0.5, size[1] * 0.5)
		points = [(int(x[0] + center[0]), int(x[1] + center[1])) for x in pointArray]
		core.draw_polyline("Canvas", points, color, thickness=thickness)

	def __resize(self):
		self.__refresh(False)

	def __refresh(self, full=True):
		core.clear_drawing("Canvas")
		if full:
			self.__fractal.parse(iteration=self.__iteration)
		self.__fractal.execute(drawCallback=self.__cbFractalDraw, drawCallBufferSize=500)

	def __render(self):
		# check if something is set to "animate"
		# x = core.get_value("AngleAnimate")
		if not core.get_value("AngleAnimate"):
			return
		step = core.get_value("AngleStep")
		self.__fractal.dAngle += step
		self.__refresh(False)
# ==============================================================================
if __name__ == "__main__":
	ExampleFractalWindow()
	core.start_dearpygui(primary_window="MainWindow")
