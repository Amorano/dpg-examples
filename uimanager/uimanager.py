"""."""

# monkey patched imports...
import sys
import os.path
t = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(t)
from support import manager

import random
from dearpygui import core, simple

class ExampleControlFilter():
	def __init__(self):
		core.set_main_window_size(1040, 400)
		core.set_style_item_spacing(1, 1)
		core.set_global_font_scale(1.8)
		with simple.window("main", autosize=True):
			with simple.group("buttons"):
				for x in range(1, 101):
					but = ''.join([chr(65 + int(random.random() * 26)) for _ in range(3)])
					core.add_button(f"{but}-{x}", width=100, height=30)
					if x % 10 != 0:
						core.add_same_line()

			with simple.group("filter"):
				core.add_input_text("regex", default_value=".*", callback=self.__filter)

		# cache the existing interface...
		self.__im = manager.UIManager()
		self.__filter("regex")

	def __filter(self, sender):
		text = core.get_value(sender)
		ctrl = self.__im.filter(name=text)
		for controls in self.__im.cache.values():
			for v in controls:
				on = int(v in ctrl)
				try:
					core.set_item_color(v, core.mvGuiCol_Button, (255 * on, 128 * on, 64 * on, 128))
				except Exception as _:
					...

if __name__ == "__main__":
	ExampleControlFilter()
	core.start_dearpygui(primary_window="main")
