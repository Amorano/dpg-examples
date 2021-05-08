"""Shows plot updates from dynamic data."""

import random
import threading
from time import sleep
from dearpygui import core, simple

_COUNT = 5
_MAXHISTORY = 100
_HEIGHT = int(640 / _COUNT)
_TICKRATE = .04

def fakeItTillYouMakeIt():
	while 1:
		for idx in range(_COUNT):
			plot = f"plot-{idx}"
			value = core.get_value(plot)
			# any data will do
			r = random.random() * 12 + 60
			value.append(r)
			# Do not over cache
			if len(value) > _MAXHISTORY:
				value.pop(0)
			core.set_value(plot, value)
		sleep(_TICKRATE)

def startup():
	with simple.window("main"):
		for idx in range(_COUNT):
			core.add_simple_plot(f"plot-{idx}", height=_HEIGHT, label=' ', maxscale=100., value=[50] * _COUNT)

		# replace this source of "data" with your own static or dynamic source.
		d = threading.Thread(name='daemon', target=fakeItTillYouMakeIt, daemon=True)
		d.start()

	core.start_dearpygui(primary_window="main")

startup()
