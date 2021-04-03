"""."""

from dearpygui import core, simple

class ExampleTemplate():
	def __init__(self):
		core.set_style_item_spacing(1, 1)
		core.set_style_window_padding(0, 0)
		core.set_main_window_size(690, 450)
		with simple.window("main"):
			core.add_drawing("canvas")
		core.set_resize_callback(self.__resize)
		core.set_render_callback(self.__render)

	def __resize(self):
		...

	def __render(self):
		...

if __name__ == "__main__":
	ExampleTemplate()
	core.start_dearpygui(primary_window="main")
