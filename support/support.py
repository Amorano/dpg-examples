"""."""

from dearpygui import core

def children(parent, recurse=True):
	if not isinstance(parent, list):
		parent = [parent]

	ret = []
	for p in parent:
		omni = core.get_item_children(p)
		ret.extend(omni)
		if recurse:
			ret.extend(children(omni))
	return ret
