"""."""

import os
from dearpygui import core, simple

# hardcoded to windows bs...
_fontpath = 'c:/windows/fonts'
_fontnames = []
_fonts = {}
for x in os.listdir(_fontpath):
	if x.endswith('otf') or x.endswith('ttf'):
		path = os.path.join(_fontpath, x)
		x = x[:-4]
		_fontnames.append(x)
		_fonts[x] = path
		core.add_additional_font(path)

_fontnames = sorted(_fontnames)

class ExampleFonts():
	def __init__(self):
		core.set_style_frame_padding(3, 3)
		core.set_style_window_padding(3, 3)
		core.set_main_window_size(650, 450)
		core.set_global_font_scale(1.5)
		with simple.window("main", autosize=True):
			with simple.group("panel", width=210):
				count = max(22, len(_fontnames))
				core.add_input_text("regex", label='', default_value=" ")
				core.add_listbox("font", label='', items=_fontnames, num_items=count, width=210, callback=self.__changed)
			core.add_same_line()
			with simple.group("text"):
				core.add_text("Lorem ipsum dolor sit amet, consectetur adipiscing elit.\
				Phasellus in mollis mauris. Donec tempor felis eget libero accumsan sagittis.\
				Integer efficitur urna sed nibh auctor, non hendrerit libero pulvinar.\
				Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere\
				cubilia curae; In hac habitasse platea dictumst. Vestibulum consectetur,\
				sem vitae tristique rhoncus, sem ex maximus ligula, vitae egestas lorem libero\
				nec libero. Pellentesque habitant morbi tristique senectus et netus et malesuada\
				fames ac turpis egestas. Praesent gravida laoreet pharetra. Ut nec vulputate purus.\
				Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos\
				himenaeos. Maecenas malesuada neque vel ipsum imperdiet, et lobortis justo sollicitudin.", wrap=560)
		simple.show_style_editor()

	def __changed(self, sender, data):
		val = core.get_value(sender)
		val = _fontnames[val]
		val = _fonts[val]
		print(val)

if __name__ == "__main__":
	ExampleFonts()
	core.start_dearpygui(primary_window="main")
