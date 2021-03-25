"""."""

import math
import random
from dearpygui import core, simple

class ExamplePixelFire():
	def __init__(self):
		core.set_vsync(False)
		core.set_style_frame_padding(0, 0)

		self.__width = 60
		self.__height = 40
		self.__fire = [0] * (self.__height * self.__width)

		with simple.window("Controls", width=220, no_resize=True):
			core.add_slider_int("Width", width=150, default_value=self.__width, min_value=5, max_value=80, clamped=True)
			core.add_slider_int("Height", width=150, default_value=self.__height, min_value=5, max_value=50, clamped=True)

		with simple.window("MainWindow"):
			core.add_drawing("Canvas", width=1920, height=1080)
			color = (0, 0, 0, 255)
			for i in range(self.__width, self.__width * self.__height):
				core.draw_quad("Canvas", (0, 0), (0, 0), (0, 0), (0, 0), color, thickness=0, tag=f"quad-{i}")
		core.set_render_callback(self.__render)

	def __render(self):
		w = core.get_value("Width")
		h = core.get_value("Height")
		if w != self.__width or h != self.__height:
			for i in range(self.__width, self.__width * self.__height):
				core.delete_draw_command("Canvas", f"quad-{i}")

			self.__width = w
			self.__height = h
			for i in range(self.__width, self.__width * self.__height):
				core.draw_quad("Canvas", (0, 0), (0, 0), (0, 0), (0, 0), (0, 0, 0, 0), thickness=0, tag=f"quad-{i}")
			self.__fire = [0] * (self.__height * self.__width)

		for x in range(self.__width):
			self.__fire[x + self.__width] = random.random() * 255

		for y in range(self.__height - 1, 1, -1):
			for x in range(self.__width):
				i = y * self.__width + x
				w2 = (x + self.__width) % self.__width
				self.__fire[i] = math.floor((
					self.__fire[(y - 1) * self.__width + w2] +
					self.__fire[(y - 1) * self.__width + (x - 1 + self.__width) % self.__width] +
					self.__fire[(y - 2) * self.__width + w2] +
					self.__fire[(y - 1) * self.__width + (x + 1 + self.__width) % self.__width]) /
					4.34)

		ws, hs = core.get_main_window_size()
		xScale = ws / self.__width
		yScale = hs / self.__height

		for i in range(self.__width, self.__width * self.__height):
			kwarg = {}
			x1 = (i % self.__width) * xScale
			y1 = (self.__height - math.floor(i / self.__width)) * yScale
			kwarg['p1'] = (x1, y1)
			kwarg['p2'] = (x1 + xScale, y1)
			kwarg['p3'] = (x1 + xScale, y1 + yScale)
			kwarg['p4'] = (x1, y1 + yScale)

			r = self.__fire[i]
			g = int(self.__fire[i] * .2)
			kwarg['color'] = (r, g, 0, 255)
			kwarg['fill'] = (r, g, 0, 255)
			core.modify_draw_command("Canvas", f"quad-{i}", **kwarg)

if __name__ == "__main__":
	ExamplePixelFire()
	core.start_dearpygui(primary_window="MainWindow")
