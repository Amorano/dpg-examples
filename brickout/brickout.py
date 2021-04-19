"""."""

from dearpygui import core, simple

class ExampleBreakoutGame():
	def __init__(self):
		self.__width = 23
		self.__height = 11
		self.__total = self.__width * self.__height
		self.__board = {}
		size = core.get_main_window_size()
		self.__paddle = [960, size[1] * .85]
		self.__paddleSize = (80, 8)
		# x, y, angle (rads), speed
		_speed = 300
		self.__paddleSpeed = 500
		self.__pos = (size[0] * .5, size[1] * .8, _speed, -_speed)

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
			core.draw_circle("canvas", (960, 600), 7, (255, 255, 255, 255), fill=(128, 128, 128, 255), tag="ball")
			core.draw_rectangle("canvas",
				[self.__paddle[0] - self.__paddleSize[0], self.__paddle[1] - self.__paddleSize[1]],
				[self.__paddle[0] + self.__paddleSize[0], self.__paddle[1] + self.__paddleSize[1]],
				(255, 255, 255, 255), fill=(128, 128, 128, 255),
				tag="paddle"
			)

		core.set_render_callback(self.__render)
		core.set_key_down_callback(self.__keydown)
		core.set_mouse_wheel_callback(self.__mousewheel)
		self.__reset()

	def __render(self):
		delta = core.get_delta_time()
		# offset everyone the delta amount
		x, y, h, v = self.__pos
		x += (h * delta)
		y += (v * delta)
		size = core.get_main_window_size()
		# hit walls
		if x < size[0] * .025 or x > size[0] * .95:
			h *= -1
		if y < size[1] * .05:
			v *= -1
		# hit paddle....
		if x > self.__paddle[0] - self.__paddleSize[0] and \
			x < self.__paddle[0] + self.__paddleSize[0] and \
			y > self.__paddle[1] - 1.5 * self.__paddleSize[1]:
				v *= -1

		# check bricks ??? all of them? ouch...
		for k, rect in self.__board.items():
			if x > rect[0] and x < rect[2] and y > rect[1] and y < rect[2]:
				px, py = k
				core.delete_draw_command("canvas", f"brick-{px}.{py}")
				# which "directions" to reverse?
				# v *= -1
				# h *= -1
				# can only hit one at a time...
				break

		core.modify_draw_command("canvas", "ball", center=[x, y])
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

	def __reset(self):
		for i in core.get_all_items():
			if i.startswith("brick"):
				core.delete_draw_command("canvas", i)

		size = core.get_main_window_size()
		xstep = (size[0] * .95) / self.__width
		# 60% of the board in "height" so we have some room
		ystep = (size[1] * .4) / self.__height
		scaleX = 0.05
		scaleY = 0.1
		yOffset = 50
		self.__board = {}
		for x in range(0, self.__width):
			for y in range(self.__height - 1, 0, -1):
				h = int(y / self.__height * 255)
				color = (h, h, h)
				x1 = int(x * xstep + xstep * scaleX)
				x2 = int((x + 1) * xstep - xstep * scaleX)
				y2 = int((y + 1) * ystep - ystep * scaleY) + yOffset
				y1 = int(y * ystep + ystep * scaleY) + yOffset
				core.draw_rectangle("canvas", (x1, y1), (x2, y2), color, fill=color, tag=f"brick-{x}.{y}")
				self.__board[(x, y)] = (x1, y1, x2, y2)

if __name__ == "__main__":
	ExampleBreakoutGame()
	core.start_dearpygui(primary_window="main")
