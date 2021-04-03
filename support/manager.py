"""."""

import re
import json
import os.path
from dearpygui import core, simple

class UIManager():
	def __init__(self):
		self.__cache = {}
		self.__refreshCache()

	@property
	def cache(self):
		return self.__cache

	def __refreshCache(self):
		"""Retreive the DearPyGui item stack and categorize them according to type.

		This would typically be your manager's entry point, where it would cache the
		initial interface, and then provide a thin layer to track "new" controls or
		the removal of existing controls.

		This allows the cache to be in sync with the present UI state.
		"""
		self.__cache = {}
		for item in core.get_all_items():
			typ = core.get_item_type(item).replace('mvAppItemType::', '').lower()
			data = self.__cache.get(typ, [])
			data.append(item)
			self.__cache[typ] = data

	def filter(self, typ=None, ignoreBuiltin=True, **kw):
		"""Filter the DPG stack of controls for specific criteria.

		ignoreBuiltin will skip *..##standard control entries i.e. about##standard
		so as to ignore the included default windows.

		filtering on string fields uses full regex matching.
		"""
		exclude = ['aboutwindow', 'docwindow', 'stylewindow', 'debugwindow', 'metricswindow', 'filedialog'] \
			if ignoreBuiltin else []

		if typ:
			if not isinstance(typ, (list, set)):
				typ = [typ]
		else:
			typ = [k for k in self.__cache]
		category = [t for t in typ if t not in exclude and self.__cache.get(t, None)]

		# nothing to filter through...
		if len(category) == 0:
			return []

		ret = []
		for c in category:
			for ctrl in self.__cache[c]:
				items = core.get_item_configuration(ctrl)
				# if filter key not present in item config, pass filter...?
				passed = True
				for k, regex in kw.items():
					val = items.get(k, None)
					if not isinstance(val, str):
						continue

					try:
						regex = re.compile(regex, re.I)
					except re.error as _:
						passed = False
						break
					else:
						if regex.search(val) is None:
							passed = False
							break
				if passed:
					ret.append(ctrl)
		return ret


class ThemeManager():
	def __init__(self, theme=None, root=None):
		self.__current = theme
		if root is None:
			root = os.path.dirname(os.path.realpath(__file__))
			root = f'{root}/theme.json'
		self.__load(root)

		with simple.window("theme", autosize=True):
			themes = self.themes
			core.add_listbox("themes", label="",
				items=themes,
				num_items=len(themes),
				callback=self.__themeChange)

		self.apply(theme or self.__current)

	def __themeChange(self, sender):
		idx = core.get_value(sender)
		theme = self.themes[idx]
		self.apply(theme)

	def __load(self, root=None, clear=True):
		if clear:
			self.__theme = {}
		if root is None:
			root = os.path.dirname(os.path.realpath(__file__))

		with open(root) as fp:
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
