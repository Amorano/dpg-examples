"""."""

import os
import json
from dearpygui import core, simple

class ExamplePersistence():
	def __init__(self):
		core.set_style_item_spacing(1, 1)
		core.set_style_window_padding(0, 0)
		core.enable_docking(shift_only=False, dock_space=True)
		core.set_main_window_size(690, 450)

		root = os.path.dirname(__file__)
		self.__configFile = f'{root}/config.json'

		with simple.window("main"):
			with simple.group("test", width=200):
				core.add_button("button1")

		core.add_window()
		with simple.window("floaty", ):
			with simple.group("test", width=200):
				core.add_button("button1")

		core.set_exit_callback(self.__exit)
		self.__configLoad()

	def __configLoad(self):
		try:
			with open(self.__configFile, 'r') as fp:
				data = json.load(fp)
		except FileNotFoundError as _:
			...
		else:
			for ctrl, config in data.items():
				print(ctrl)
				core.configure_item(ctrl, **config)

	def __configSave(self):
		blob = {}
		for ctrl in core.get_all_items():
			if ctrl.endswith('##standard') or ctrl in ['filedialog']:
				continue
			blob[ctrl] = core.get_item_configuration(ctrl)

		with open(self.__configFile, 'w') as fp:
			json.dump(blob, fp, sort_keys=True, indent=4)

	def __exit(self):
		self.__configSave()

if __name__ == "__main__":
	ExamplePersistence()
	core.start_dearpygui(primary_window="main")
