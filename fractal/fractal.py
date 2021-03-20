"""."""
import re
import math
import json
import os.path as path
from collections import OrderedDict
import dearpygui.core as core
import dearpygui.simple as simple
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
				core.add_input_int("Iteration", width=150, default_value=self.__iteration, callback=self.__cbIterationValue)
				core.add_input_float("Angle", width=150, default_value=self.__fractal.dAngle, callback=self.__cbAngleValue)
			core.add_same_line()
			core.add_listbox("power", label='', items=self.__fractalKeys, callback=self.__cbFractalType)
			core.add_drawing("Canvas", width=size[0] * 2, height=size[1] * 2)
		core.set_resize_callback(self.__resize)
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
		iteration = max(2, min(iteration, 10))
		core.set_value(sender, iteration)
		self.__iteration = iteration
		self.__refresh()

	def __cbAngleValue(self, sender, data):
		angle = core.get_value(sender) % 360
		core.set_value(sender, angle)
		self.__fractal.dAngle = angle
		self.__refresh()

	def __cbFractalDraw(self, pointArray: list):
		color = [255, 255, 255, 255]
		thickness = math.log(40 / self.__iteration) * (5 / self.__fractal.dAngle)
		size = core.get_main_window_size()
		center = (size[0] * 0.5, size[1] * 0.5)
		points = [(int(x[0] + center[0]), int(x[1] + center[1])) for x in pointArray]
		core.draw_polyline("Canvas", points, color, thickness=thickness)

	def __resize(self):
		self.__refresh()

	def __refresh(self):
		core.clear_drawing("Canvas")
		self.__fractal.delta = 20 - 8 * math.log(self.__iteration)
		self.__fractal.parse(iteration=self.__iteration)
		self.__fractal.execute(drawCallback=self.__cbFractalDraw, drawCallBufferSize=500)
# ==============================================================================
if __name__ == "__main__":
	core.set_vsync(False)
	core.set_style_window_padding(0, 0)
	ExampleFractalWindow()
	core.start_dearpygui(primary_window="MainWindow")
