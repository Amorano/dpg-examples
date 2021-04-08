"""."""

from dearpygui import core, simple

class ExampleFPS():
	def __init__(self):
		# turn off the sync to measure FPS
		core.set_vsync(False)
		self.__vsync = False

		with simple.window("main"):
			with simple.group("group", width=150):
				core.add_label_text("FPS")
				core.add_button("vsync", label="Toggle V-Sync On", callback=self.__toggleVsync)
				core.set_item_color("vsync", core.mvGuiCol_Button, (200, 96, 96, 255))

		core.set_render_callback(self.__render)

		# maximum average the last XX ticks...
		self.__avgCountMax = 240
		self.__avg = []

	def __toggleVsync(self):
		self.__vsync = not self.__vsync
		core.set_vsync(self.__vsync)
		self.__avg = []
		label = "Toggle V-Sync Off" if self.__vsync else "Toggle V-Sync On"
		core.configure_item("vsync", label=label)
		color = (96, 200, 96, 255) if self.__vsync else (200, 96, 96, 255)
		core.set_item_color("vsync", core.mvGuiCol_Button, color)

	def __render(self):
		delta = 1. / core.get_delta_time()
		self.__avg.append(delta)

		# average over X items
		count = len(self.__avg)
		if count > self.__avgCountMax:
			self.__avg.pop(0)

		# trim to a few significance
		avg = int(sum(self.__avg) / count * 1000)
		core.set_value("FPS", avg / 1000.)

if __name__ == "__main__":
	ExampleFPS()
	core.start_dearpygui(primary_window="main")
