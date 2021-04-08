"""."""

from random import choice
from dearpygui import core, simple

_FIRST = ['Dear', 'Discover', 'Deer', 'Beer', 'Dynamic', 'Immediate', 'Fast', 'Quick', 'Discord', 'Splendid', 'Beautiful', 'Super', 'Rich', 'Quaint', 'Open', 'Wicked', 'Modern', 'Fancy', 'Helpful', 'Fantastic', 'Alert', 'Nice', 'Determined', 'Magnificent', 'Elegant', ]
_SECOND = ['Python', 'Information', 'Pragmatic', 'Control', 'Response', 'Engineering', 'Delivery', 'Device', 'Connection', 'Software', 'Computer', 'System', 'Programming', 'Pixel', 'Technology', 'Programable', 'Development', 'Progam', 'User', 'Prime', 'Test']
_THIRD = ['GUI', 'UI', 'UX', 'Graphics', 'Interface', 'Production', 'Forge', 'Creator', 'Sketch', 'Render', 'Dream', 'Pilot', 'Editor', 'Kit', 'API']

class ExampleGenerate():
	def __init__(self):
		core.set_style_item_spacing(29, 4)
		core.set_style_window_padding(0, 0)
		core.set_main_window_size(1920, 1080)

		self.__column = 7
		self.__row = 58

		with simple.window("main"):
			with simple.group("test", width=187):
				core.add_button("THE DPG HERO WE NEED...", callback=self.__generate)

			for c in range(self.__column):
				core.add_same_line()
				with simple.group(f"col-{c}", width=187):
					x = c * self.__row
					for r in range(self.__row):
						core.add_text(str(x + r), default_value=" ")

	def __generate(self):
		for c in range(self.__column):
			x = c * self.__row
			for r in range(self.__row):
				name = f"{choice(_FIRST)} {choice(_SECOND)} {choice(_THIRD)}"
				core.set_value(str(x + r), name)

if __name__ == "__main__":
	ExampleGenerate()
	core.start_dearpygui(primary_window="main")
