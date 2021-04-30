"""Threaded progress bar widget."""

import random
from queue import Queue
from threading import Thread
from dearpygui import core, simple

class ThreadProgress(Thread):
	def __init__(self, progressBar, queue, callback=None):
		super().__init__()
		self.daemon = True
		self.__q = queue
		self.__progressBar = progressBar
		self.__callback = callback

	def run(self):
		while self.is_alive:
			val, overlay = self.__q.get()
			if val is None:
				break
			core.configure_item(self.__progressBar.guid, overlay=overlay)
			core.set_value(self.__progressBar.guid, val)

		if self.__callback:
			self.__callback()

class ProgressBar():
	_index = 0
	def __init__(self, parent, guid=None, callback=None, **kw):

		guid = guid or self.__class__.__name__
		self.__guid = f'{parent}-{guid}.{ProgressBar._index}'
		self.__idGroup = f"{self.__guid}-group"
		ProgressBar._index += 1

		self.__callback = callback
		self.__worker = None
		self.__q = Queue()
		self.__value = 0

		width, _ = core.get_item_rect_size(parent)
		width = int(width)
		kw['width'] = kw.get('width', width)
		kw['show'] = kw.get('show', False)
		kw.pop('parent', None)
		with simple.group(self.__idGroup, width=width, parent=parent):
			core.add_progress_bar(self.__guid, **kw)

	@property
	def progress(self):
		return self.__value

	@progress.setter
	def progress(self, val):
		self.__value = val
		data = f'{round(val * 100)}%'
		if val < 0:
			val = 0
		if val > 1.:
			val = None
		self.__q.put((val, data))

	@property
	def guid(self):
		return self.__guid

	def start(self):
		simple.show_item(self.__guid)
		self.__worker = ThreadProgress(self, self.__q, callback=lambda: self.__callback(self.__guid))
		self.__worker.start()

	def reset(self):
		self.__value = 0

class Window():
	def __init__(self):
		core.set_main_window_size(720, 540)
		with simple.window("main"):
			with simple.group("group"):
				core.add_button("thread", label='Add Thread', callback=lambda s, d: self.__buttonThread())

		self.__bars = {}
		core.set_render_callback(lambda s, d: self.__render())
		core.set_resize_callback(lambda s, d: self.__resize())

	def __resize(self):
		width, _ = core.get_main_window_size()
		core.configure_item('thread', width=width)
		for b in self.__bars:
			core.configure_item(b, width=width)

	def __render(self):
		for t in self.__bars:
			r = random.random() * 0.006
			self.__bars[t].progress += r

	def __buttonThread(self):
		for _ in range(5):
			pb = ProgressBar("main", "progress", callback=self.__cleanup)
			self.__bars[pb.guid] = pb
			pb.start()

	def __cleanup(self, pb):
		del self.__bars[pb]
		core.delete_item(f'{pb}-group')

	def start(self):
		core.start_dearpygui(primary_window="main")

if __name__ == "__main__":
	w = Window()
	w.start()
