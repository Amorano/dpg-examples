"""."""

from dearpygui import core, simple

class ExampleEvents():
	def __init__(self):
		# tracks all the dpg mvKey_ constants
		self.__keymap = {}
		for const in dir(core):
			if const.startswith('mvKey_'):
				c = getattr(core, const)
				self.__keymap[c] = {'name': const, 'val': 0}

		core.set_main_window_size(750, 480)

		with simple.window("main"):
			with simple.group("press"):
				...
			core.add_same_line()

			with simple.group("down"):
				...
			core.add_same_line()

			with simple.group("release"):
				...

		core.set_key_press_callback(self.__press)
		core.set_key_down_callback(self.__down)
		core.set_key_release_callback(self.__release)
		core.set_render_callback(lambda s, d: self.__render())

	def __press(self, s, d):
		self.__keymap[d]['val'] = 1

	def __down(self, s, d):
		self.__keymap[d]['val'] = 2

	def __release(self, s, d):
		self.__keymap[d]['val'] = 4

	def __render(self):
		for x in ["press", "down", "release"]:
			kid = f"{x}-kid"
			if core.does_item_exist(kid):
				core.delete_item(kid)
			with simple.group(kid, parent=x, width=250):
				core.add_text(f'{x}-text', default_value=' ')

		for k, v in self.__keymap.items():
			if v['val'] == 1:
				core.add_text(v['name'], parent="press-kid")
			if v['val'] == 2:
				core.add_text(v['name'], parent="down-kid")
			if v['val'] == 4:
				core.add_text(v['name'], parent="release-kid")
				self.__keymap[k]['val'] = 0

if __name__ == "__main__":
	ExampleEvents()
	core.start_dearpygui(primary_window="main")
