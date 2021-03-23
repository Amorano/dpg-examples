import dearpygui.core as core
import dearpygui.simple as simple

class ExampleCallbackMouseWheel():
	def __init__(self):
		self.__fontSize = 1.
		self.__fontSizeStep = .1
		self.__fontSizeRange = (.8, 15.)
		core.set_global_font_scale(self.__fontSize)
		core.set_theme("Cherry")
		core.set_main_window_size(960, 540)

		with simple.window("MainWindow", autosize=True):
			core.add_text("HELLO WORLD!")
		core.set_mouse_wheel_callback(self.__cbMouseWheel)

	def __cbMouseWheel(self, sender, data):
		max_value = max(self.__fontSizeRange[0], self.__fontSizeRange[1])
		min_value = min(self.__fontSizeRange[0], self.__fontSizeRange[1])
		self.__fontSize += (data * self.__fontSizeStep)
		self.__fontSize = max(min(self.__fontSize, max_value), min_value)
		print(self.__fontSize)
		core.set_global_font_scale(self.__fontSize)
# ==============================================================================
if __name__ == "__main__":
	ExampleCallbackMouseWheel()
	core.start_dearpygui(primary_window="MainWindow")
