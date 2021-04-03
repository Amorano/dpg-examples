"""."""

from dearpygui import core

def children(parent, recurse=True):
	if not isinstance(parent, list):
		parent = [parent]
	ret = []
	for p in parent:
		all = core.get_item_children(p)
		ret.extend(all)
		if recurse:
			ret.extend(children(all))
	return ret
