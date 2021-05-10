"""."""

import math
from dearpygui import core, simple

class ExampleBreakoutGame():
	def __init__(self):
		core.set_main_window_size(720, 540)
		self.__width = 17
		self.__height = 7
		self.__total = self.__width * self.__height
		self.__board = {}
		size = core.get_main_window_size()
		self.__paddle = [size[0] * .475, size[1] * .85]
		self.__paddleSize = (80, 8)
		# x, y, angle (rads), speed
		self.__radius = 6
		self.__speed = 300
		self.__paddleSpeed = 1000
		self.__speedMax = self.__speed * 3
		self.__pos = (size[0] * .5, size[1] * .8, 0, -self.__speed)

		with simple.window("main"):
			with simple.group("scoreboard"):
				core.add_label_text("score")
				core.add_same_line()
				core.add_text("score-value")
				# core.add_same_line()
				core.add_label_text("time")
				core.add_same_line()
				core.add_text("time-value")
			core.add_drawing("canvas", width=size[0], height=size[1])
			core.draw_circle("canvas", size, self.__radius, (255, 255, 255, 255), fill=(128, 128, 128, 255), tag="ball")
			core.draw_rectangle("canvas",
				[self.__paddle[0] - self.__paddleSize[0], self.__paddle[1] - self.__paddleSize[1]],
				[self.__paddle[0] + self.__paddleSize[0], self.__paddle[1] + self.__paddleSize[1]],
				(255, 255, 255, 255), fill=(128, 128, 128, 255),
				tag="paddle"
			)

		core.set_resize_callback(self.__resize)
		core.set_render_callback(self.__render)
		core.set_key_down_callback(self.__keydown)
		core.set_mouse_wheel_callback(self.__mousewheel)

	def __render(self):
		delta = core.get_delta_time()
		# offset everyone the delta amount
		x, y, h, v = self.__pos
		size = core.get_main_window_size()
		x += (h * delta)
		y += (v * delta)

		x1 = x - self.__radius
		x2 = x + self.__radius
		y1 = y - self.__radius
		y2 = y + self.__radius

		# hit walls
		if x1 <= 10 or x2 >= size[0] - 10:
			h += (math.copysign(1, h) * 0.1 * self.__speed)
			h *= -1
		if y1 <= 50 or y2 >= size[1] - 100:
			v += (math.copysign(1, v) * 0.1 * self.__speed)
			v *= -1

		# hit paddle....
		if x > self.__paddle[0] - self.__paddleSize[0] and \
			x < self.__paddle[0] + self.__paddleSize[0] and \
			y > self.__paddle[1] - 1.5 * self.__paddleSize[1]:
				v *= -1

		# check bricks ??? all of them? ouch...
		for k, rect in self.__board.items():
			if x2 >= rect[0] and x1 <= rect[2] and y2 >= rect[1] and y1 <= rect[3]:
				px, py = k
				core.delete_draw_command("canvas", f"brick-{px}.{py}")
				del self.__board[k]
				v *= -1
				h += (math.copysign(1, h) * 0.1 * self.__speed)
				break

		core.modify_draw_command("canvas", "ball", center=[x, y])
		v = min(self.__speedMax, max(-self.__speedMax, v))
		h = min(self.__speedMax, max(-self.__speedMax, h))
		self.__pos = (x, y, h, v)

	def __mousewheel(self, sender, data):
		self.__move(data * 2)

	def __keydown(self, sender, data):
		key, _ = data
		if key == 65:
			self.__move(-1)
		if key == 68:
			self.__move(1)

	def __move(self, direction):
		x, y = self.__paddle
		delta = core.get_delta_time()
		x += direction * delta * self.__paddleSpeed
		# bounds
		size = core.get_main_window_size()
		if x < self.__paddleSize[0]:
			x = self.__paddleSize[0]
		if x > size[0] - self.__paddleSize[0]:
			x = size[0] - self.__paddleSize[0]
		pmin = [self.__paddle[0] - self.__paddleSize[0], self.__paddle[1] - self.__paddleSize[1]]
		pmax = [self.__paddle[0] + self.__paddleSize[0], self.__paddle[1] + self.__paddleSize[1]]
		core.modify_draw_command("canvas", "paddle", pmin=pmin, pmax=pmax)
		self.__paddle = (x, y)

	def __resize(self, sender, data):
		self.__reset()

	def __reset(self):
		for x in range(0, self.__width):
			for y in range(self.__height - 1, 0, -1):
				tag = f"brick-{x}.{y}"
				core.delete_draw_command("canvas", tag)

		size = core.get_main_window_size()
		core.configure_item("canvas", width=size[0], height=size[1])
		xstep = size[0] / self.__width
		# 60% of the board in "height" so we have some room
		ystep = (size[1] * .4) / self.__height
		self.__paddle = [size[0] * .475, size[1] * .85]
		scaleX = 0.01
		scaleY = 0.02
		yOffset = 50
		xOffset = 0
		self.__speed = 300
		self.__pos = (size[0] * .5, size[1] * .8, 0, -self.__speed)
		self.__board = {}
		for x in range(0, self.__width):
			for y in range(self.__height - 1, 0, -1):
				h = int(y / self.__height * 255)
				color = (h, h, h)
				x1 = int(x * xstep + xstep * scaleX) + xOffset
				x2 = int((x + 1) * xstep - xstep * scaleX) + xOffset
				y2 = int((y + 1) * ystep - ystep * scaleY) + yOffset
				y1 = int(y * ystep + ystep * scaleY) + yOffset
				core.draw_rectangle("canvas", (x1, y1), (x2, y2), color, fill=color, tag=f"brick-{x}.{y}")
				self.__board[(x, y)] = (x1, y1, x2, y2)

if __name__ == "__main__":
	ExampleBreakoutGame()
	core.start_dearpygui(primary_window="main")
