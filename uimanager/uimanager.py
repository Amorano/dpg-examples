"""."""

import re
from dearpygui import core, simple

def siblings(parent, recurse=True):
	if not isinstance(parent, list):
		parent = [parent]
	ret = []
	for p in parent:
		ret.extend(core.get_item_children(p))
		if recurse:
			ret.extend(siblings(p))
	return ret

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

class ExampleControlFilter():
	def __init__(self):
		core.set_style_item_spacing(1, 1)
		core.set_global_font_scale(1.8)
		with simple.window("main", autosize=True):
			with simple.group("buttons"):
				for x in range(1, 101):
					core.add_button(f"but-{x}", width=100, height=30)
					if x % 10 != 0:
						core.add_same_line()

			with simple.group("filter"):
				core.add_input_text("regex", default_value=".*", callback=self.__filter)

		# cache the existing interface...
		self.__im = InterfaceManager()
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
