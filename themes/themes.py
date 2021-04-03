"""."""

import sys
from os import path
# monkey patched imports...
t = path.join(path.dirname(__file__), "..")
sys.path.append(t)
from support import manager

from dearpygui import core, simple

class ExampleThemes():
	def __init__(self):
		core.set_style_item_spacing(1, 1)
		core.set_style_window_padding(0, 0)

		with simple.window("main"):
			with simple.group("controls", width=520):
				with simple.group("buttons"):
					for x in range(6):
						core.add_button(f"id-{x}", label=f"button {x}")
					core.add_color_button("bcolor", (196, 128, 155, 255))
					core.add_radio_button("radio")
					core.add_checkbox("checkbox")

				core.add_same_line()

				with simple.group("misc"):
					core.add_date_picker("date")

				with simple.group("text"):
					core.add_text("text")
					core.add_input_text("input_text", label="", default_value="Call me Ish-meal. Tasty like an ashen log.")
					core.add_label_text("label", label="", default_value="label")

				core.add_same_line()

				with simple.group("dropdown"):
					core.add_listbox("listbox", label="", items=(1, 2, 3))
					core.add_combo("combo", label="", items=(1, 2, 3))

				for x in ["float", "int"]:
					with simple.group(x):
						for what in ["add_drag_", "add_input_"]:
							for y in ['', 2, 3, 4]:
								n = f"{what}{x}{y}"
								cmd = getattr(core, n)
								cmd(n, label="", width=200)
					core.add_same_line()

		manager.ThemeManager()


if __name__ == "__main__":
	ExampleThemes()
	core.start_dearpygui(primary_window="main")
