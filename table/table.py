"""."""

import os
import re
import csv
from dearpygui import core, simple

class Excelsior():
	def __init__(self):
		# row header names to preserve for re-posting table on searching
		self.__headers = []
		# the rows to filter during a search
		self.__rows = []

		cwd = os.path.dirname(__file__)
		os.chdir(cwd)

		core.set_main_window_size(800, 750)
		with simple.window("main"):

			with simple.group("control"):
				core.add_button("load", callback=lambda: core.open_file_dialog(callback=self.__load, extensions='.csv'))
				core.add_input_text("filter", default_value=".*", callback=self.__tableRefresh)

			with simple.group("panel"):
				...

	def start(self):
		core.start_dearpygui(primary_window="main")

	def __tableRefresh(self):
		if core.does_item_exist("table"):
			core.delete_item("table")

		# build the data model so we can search it
		core.add_table("table", self.__headers, parent="panel")
		search = core.get_value("filter")
		search = re.compile(filter, re.I)
		for row in self.__rows:
			for cell in row:
				if search.search(cell):
					core.add_row("table", row)
					break

	def __load(self, sender, data):
		path = os.sep.join(data)
		with open(path, newline='') as f:
			data = csv.reader(f)
			while header := next(data):
				# skip blank rows in the CSV, first with headers...
				if ''.join(header) != '':
					break
			self.__headers = header
			self.__rows = [d for d in data]
			self.__tableRefresh()

if __name__ == "__main__":
	editor = Excelsior()
	editor.start()
