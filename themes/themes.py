"""."""

import json
from os import path
from dearpygui import core, simple

class ThemeManager():
	def __init__(self, theme=None, root=None):
		self.__current = theme
		self.__load(root)
		self.apply(theme or self.__current)

	def __load(self, root=None):
		self.__theme = {}
		if root is None:
			root = path.dirname(path.realpath(__file__))

		with open(f'{root}/theme.json') as fp:
			self.__theme = json.load(fp)

		# default
		k = [k for k in self.__theme]
		theme = k[0] if len(k) else None
		self.apply(theme)

	def __str__(self):
		size = len(self.__theme.keys())
		return f"[{self.__current}] {size} themes"

	@property
	def current(self):
		"""Selected theme's data blob."""
		return self.__theme[self.__current]

	@property
	def themes(self):
		return sorted(self.__theme.keys())

	def apply(self, who):
		theme = self.__theme.get(who, None)
		if theme is None:
			print(f"no theme: {who}")
			return

		overall = theme.get("theme", None)
		if overall:
			core.set_theme(theme=overall)

		# thing is what category, cmd is cmd, const == color const for v[0]
		# func == extend function with data...
		for thing, cmd, func, const in [
			# ("font", "add_additional_font", False, False),
			("style", "set_style_", True, False),
			("color", "set_theme_item", False, True),
		]:
			for k, v in theme.get(thing, {}).items():
				meth = f"{cmd}{k}" if func else cmd
				try:
					meth = getattr(core, meth)
				except Exception as _:
					print(f"no function: {meth}")
					continue

				if const:
					nv = f"mvGuiCol_{k}"
					try:
						nv = getattr(core, nv)
					except Exception as _:
						print(f"no constant: {nv}")
						continue
					v = [nv] + [int(c * 255) for c in v]

				if isinstance(v, (list, tuple)):
					meth(*v)
				else:
					meth(v)
		self.__current = who

class ExampleThemes():
	def __init__(self):
		core.set_style_item_spacing(1, 1)
		core.set_style_window_padding(0, 0)

		self.__themeMgr = ThemeManager()

		with simple.window("main"):

			with simple.group("theme", width=170):
				themes = self.__themeMgr.themes
				core.add_listbox("themes", label="", items=themes, num_items=len(themes), callback=self.__themeChange)

			core.add_same_line()
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

	def __themeChange(self, sender):
		idx = core.get_value(sender)
		theme = self.__themeMgr.themes[idx]
		self.__themeMgr.apply(theme)

if __name__ == "__main__":
	ExampleThemes()
	core.start_dearpygui(primary_window="main")
