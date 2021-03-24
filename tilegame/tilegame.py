"""."""

from os import path, listdir
import numpy as np
from PIL import Image
from dearpygui import core, simple

def makeImage(imageFile: str, sliceX: int, sliceY: int):
	"""Slice an imagefile into X by Y chunks."""
	img = Image.open(imageFile).convert('RGBA')
	height = int(img.height / sliceY)
	width = int(img.width / sliceX)

	index = 0
	cap = sliceY * sliceX - 1
	for y in range(sliceY):
		y1 = y * height
		for x in range(sliceX):
			x1 = x * width

			tile = img.copy().crop((x1, y1, x1 + width, y1 + height))
			if index == cap:
				tile = Image.new('RGBA', (width, height))
			data = np.array(tile).ravel()
			core.add_texture(f"image-{index}", data, width, height)
			index += 1

class ExampleTileGame():
	def __init__(self):
		core.set_style_item_spacing(0, 0)
		core.set_style_window_padding(0, 0)

		self.__rows = 0
		self.__cap = 0
		self.__board = []
		self.__width = 0
		self.__height = 0

		self.__puzzles = {}
		root = path.dirname(path.realpath(__file__))
		for f in listdir(root):
			full = f"{root}/{f}"
			if not path.isfile(full) or not f.endswith('.png'):
				continue
			who, _ = path.splitext(f)
			self.__puzzles[who] = full
		keys = list(self.__puzzles.keys())
		self.__puzzle = self.__puzzles[keys[0]]

		with simple.window("MainWindow", autosize=True):
			with simple.group("Controls"):
				for d in [3, 5, 7]:
					core.add_same_line()
					core.add_button(f"{d} x {d}", width=120, height=50, callback=self.__clearBoard)
					core.add_same_line()
					core.add_dummy()
				core.add_same_line()
				core.add_button("Solve!", width=120, height=50, callback=self.__solve)
				core.add_same_line()
				items = [p for p in self.__puzzles.keys()]
				core.add_listbox("selection", items=items, callback=self.__imgChange)
		self.__clearBoard(self, 3)

	def __imgChange(self, sender, data):
		data = core.get_item_configuration(sender)
		idx = core.get_value(sender)
		puzzle = self.__puzzles[data['items'][idx]]
		if puzzle != self.__puzzle:
			self.__puzzle = puzzle
			self.__clearBoard(self, self.__rows, True)

	def __solve(self, sender, data):
		self.__board = np.arange(0, self.__rows * self.__rows)
		self._resize()

	def _resize(self):
		"""."""
		size = core.get_main_window_size()
		width = int(size[0] / self.__rows * .98)
		height = int(size[1] / self.__rows * .98)

		ratio = float(size[0]) / size[1]
		if size[1] > size[0]:
			ratio = float(size[1]) / size[0]
		self.__height = int(height * ratio * .575)
		self.__width = width
		self.__redraw()

	def __redraw(self):
		core.delete_item("Layout")
		with simple.group("Layout", parent="MainWindow"):
			for index, i in enumerate(self.__board):
				core.add_image_button(f"button-{i}", f"image-{i}",
					width=self.__width, height=self.__height,
					frame_padding=0, callback=self.__cbButtonMove)
				if (index + 1) % self.__rows != 0:
					core.add_same_line()

	def __clearBoard(self, sender, data, reset=False):
		"""."""
		label = None
		if isinstance(sender, str):
			label = core.get_item_configuration(sender)['label']

		dim = data or int(label.split(" ")[0])

		if self.__rows != dim or reset:
			makeImage(self.__puzzle, dim, dim)
			self.__cap = dim * dim - 1
			self.__board = np.arange(0, dim * dim)

		np.random.shuffle(self.__board)
		self.__rows = dim
		self._resize()

	def __cbButtonMove(self, sender, data):
		"""."""
		tile = int(sender.split('-')[1])
		alpha = np.where(self.__board == tile)[0][0]

		rowMin = int(alpha / self.__rows)
		rowMax = rowMin * self.__rows + self.__rows

		# n, e, s, w tests
		beta = alpha - self.__rows
		if beta >= 0 and self.__board[beta] == self.__cap:
			self.__board[alpha], self.__board[beta] = self.__board[beta], self.__board[alpha]
			return self._resize()

		beta = alpha + 1
		if beta < rowMax and self.__board[beta] == self.__cap:
			self.__board[alpha], self.__board[beta] = self.__board[beta], self.__board[alpha]
			return self._resize()

		beta = alpha + self.__rows
		if beta <= self.__cap and self.__board[beta] == self.__cap:
			self.__board[alpha], self.__board[beta] = self.__board[beta], self.__board[alpha]
			return self._resize()

		beta = alpha - 1
		if beta >= rowMin and self.__board[beta] == self.__cap:
			self.__board[alpha], self.__board[beta] = self.__board[beta], self.__board[alpha]
			return self._resize()

if __name__ == "__main__":
	ExampleTileGame()
	core.start_dearpygui(primary_window="MainWindow")
