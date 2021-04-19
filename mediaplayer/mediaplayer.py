"""."""

import time
from os import path, listdir
import threading
import ffmpeg
import numpy as np
from dearpygui import core, simple

# to hold the current frames decoded from FFMPEG
_BUFFER = []

class Process(threading.Thread):
	def __init__(self, buffer, height, width):
		threading.Thread.__init__(self)
		self.__height = height
		self.__width = width
		self.__buffer = buffer

	def run(self):
		out, _ = (
			ffmpeg
			.input(self.__buffer)
			.output('pipe:', format='rawvideo', pix_fmt='rgba')
			.run(capture_stdout=True)
		)

		global _BUFFER
		_BUFFER = (
			np
			.frombuffer(out, np.uint8)
			.reshape([-1, self.__height, self.__width, 4])
		)

class ExampleMediaplayer():
	def __init__(self):

		self.__last = -1

		self.__targetFPS = 30

		# playhead position
		self.__head = 0.

		# playback stopped
		self.__direction = 0.

		# looping on
		self.__loop = True

		# thread that is "streaming" the video
		self.__thread = None

		self.__frameCount = self.__width = self.__height = 0

		self.__root = path.dirname(path.realpath(__file__))

		core.set_style_item_spacing(1, 1)
		core.set_style_frame_padding(0, 0)
		core.get_style_window_padding(0, 0)
		width = 740
		height = 680
		core.set_main_window_size(width, height)

		with simple.window("MainWindow"):
			core.add_drawing("Canvas", width=width, height=height)

		w = 50
		h = 20
		with simple.window("Media Bar", autosize=True, no_collapse=True, no_close=True, no_scrollbar=True):
			with simple.group("Browser"):
				core.add_listbox("Listing", label='', items=[], callback=self.__itemChange)

			with simple.group("Shuttle"):
				core.add_button("Shuttle#Browse", width=w, height=h,
					label="...",
					callback=lambda: core.select_directory_dialog(callback=self.__browser))
				core.add_button("Shuttle#Front", width=w, height=h,
					label='|<',
					callback=lambda: self.__seek(0))
				core.add_same_line()
				core.add_button("Shuttle#Backwards", width=w, height=h,
					label='<-',
					callback=lambda: self.__play(-1))
				core.add_same_line()
				core.add_button("Shuttle#Forwards", width=w, height=h,
					label='->',
					callback=lambda: self.__play(1))
				core.add_same_line()
				core.add_button("Shuttle#End", width=w, height=h,
					label='>|',
					callback=lambda: self.__seek(-1))
				core.add_same_line()
				core.add_color_button("Shuttle#Loop", [50, 50, 227, 255], width=w, height=h,
					callback=self.__loopToggle)
				core.add_same_line()
				core.add_text("ShuttleFPS")
				core.add_drag_float("MediabarHead", label="", width=w * 5 + 5, callback=self.__cbSeek)

		core.set_render_callback(self.__render)
		core.set_mouse_wheel_callback(self.__mouseWheel)
		core.set_exit_callback(self.__close)
		self.__scanDir()

	def __close(self):
		if self.__thread:
			while self.__thread.is_alive():
				self.__thread.join()
				time.sleep(0.1)
		core.stop_dearpygui()

	def __itemChange(self, sender, data):
		idx = core.get_value(sender)
		val = core.get_item_configuration("Listing")["items"][idx]
		self.__threadRestart(val)

	def __browser(self, sender, data):
		self.__root = data[0]
		self.__scanDir()

	def __scanDir(self):
		ret = []
		for f in listdir(self.__root):
			full = f"{self.__root}/{f}"
			if path.isfile(full):
				for x in ['.mp4', '.avi']:
					if f.lower().endswith(x):
						ret.append(f)
						break

		core.configure_item("Listing", items=ret)
		if len(ret) > 0:
			self.__threadRestart(ret[0])

	def __threadRestart(self, filename: str):
		core.clear_drawing("Canvas")
		self.__play(0)
		self.__head = 0
		fp = f"{self.__root}/{filename}"
		probe = ffmpeg.probe(fp)
		video_info = next(stream for stream in probe['streams'] if stream['codec_type'] == 'video')
		self.__width = int(video_info['width'])
		self.__height = int(video_info['height'])
		self.__frameCount = int(video_info['nb_frames'])

		global _BUFFER
		_BUFFER = [[0, 0, 0, 0] * self.__width * self.__height] * self.__frameCount

		# kill the old if there...
		if self.__thread:
			self.__thread._stop()
		self.__thread = Process(fp, self.__width, self.__height)
		self.__thread.start()

	def __mouseWheel(self, sender, data):
		self.__direction = 0
		self.__head += (data * (24. / self.__targetFPS))
		self.__renderFrame()

	def __render(self):
		delta = core.get_delta_time()
		fps = 1. / delta

		ratio = self.__targetFPS / fps
		core.set_value('ShuttleFPS', int(fps))
		core.set_value('MediabarHead', self.__head)
		if self.__direction == 0:
			return

		# adjust the frame(s) to playback? based on last frametime?
		# for now, just play a single "frame"
		self.__head += (ratio * self.__direction)
		self.__renderFrame()

	def __renderFrame(self):
		# looping?
		if self.__head < 0:
			if self.__loop:
				self.__head += self.__frameCount
			else:
				self.__head = 0
				self.__play(0)
				return
		elif self.__head > self.__frameCount:
			if self.__loop:
				self.__head -= self.__frameCount
			else:
				self.__head = self.__frameCount
				self.__play(0)
				return

		idx = int(self.__head)
		if self.__last == idx:
			return
		self.__last = idx
		frame = _BUFFER[idx]
		core.add_texture("temp", frame, self.__width, self.__height)
		core.draw_image("Canvas", "temp", [0, 0], pmax=[self.__width, self.__height])

	def __loopToggle(self):
		"""Toggle looping."""
		self.__loop = not self.__loop
		# core.configure_item("Shuttle#Loop", label=['--', 'OO'][self.__loop])
		green = [30, 227, 30, 255]
		red = [227, 30, 30, 255]
		core.configure_item("Shuttle#Loop", color=[red, green][self.__loop])

	def __play(self, direction):
		"""Continue playback from head index in <- / -> direction.

		Direction can be negative for reverse playback, and can be
		greater than 1 or fractional, or stopped (0).
		"""
		if direction != 0:
			core.configure_item("Shuttle#Forwards", label='||')
			core.set_item_callback("Shuttle#Forwards", callback=lambda: self.__play(0))
		else:
			core.configure_item("Shuttle#Forwards", label='->')
			core.set_item_callback("Shuttle#Forwards", callback=lambda: self.__play(1))
		self.__direction = direction

	def __cbSeek(self, sender, data):
		value = core.get_value(sender)
		self.__seek(value)

	def __seek(self, value):
		"""Find frame `value`."""
		if value < 0:
			value = self.__frameCount - 1
		self.__head = max(0, min(value, self.__frameCount - 1))
		self.__direction = 0
		self.__renderFrame()
# ==============================================================================
if __name__ == "__main__":
	ExampleMediaplayer()
	core.start_dearpygui(primary_window="MainWindow")
