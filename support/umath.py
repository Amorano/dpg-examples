"""."""

import numpy as np
from PIL import Image
from dearpygui import core

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
