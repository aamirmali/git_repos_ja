#!/usr/bin/env python
"""
Module for maintaining the scrappy data tree.
"""

import sys
import os
import pickle
from functools import partial
from itertools import permutations

import locate_dirfiles
locate_dirfiles.update_pickles()

ROOT = '/home/abs/scrappy_data/'
QUEUE = os.path.join(ROOT, '.queue')
SUFFIX = 'dirfile'
ALL_DIRFILES = locate_dirfiles.filter_all()

def get_dirfile_name(dirfile_path):
	"""
	Split the dirfile path, return last part...
	pretty stupid, I guess
	"""
	real_path = os.path.realpath(dirfile_path)
	return os.path.split(real_path)[1]

def get_extra_data(dirfile_path):
	"""
	Returns extra_data as list of duples, not dictionary!
	"""
	p = os.path.join(dirfile_path, '.extra_data.p')
	d = pickle.load(file(p, 'r')).items()
	return d
ALL_EXTRA_DATA = [get_extra_data(dirfile) for dirfile in ALL_DIRFILES]
ALL_EXTRA_DATA_DICTS = map(dict, ALL_EXTRA_DATA)

def filter_match(filter_d, d):
	"""
	return True or False, depending on
	whether d matches the filter
	(has all keys/values of filter_d)
	"""
	for k in filter_d:
		if not d.has_key(k): return False
		elif d[k] != filter_d[k]: return False
	return True

def filter_all_extra_data(filter_d):
	"""
	Filter the ALL_EXTRA_DATA list by given filter
	dictionary, filter_d
	"""
	f = partial(filter_match, filter_d)
	return filter(f, ALL_EXTRA_DATA_DICTS)

def make_symlink(dirfile_src, key_dir, v, add_suffix=True):
	if add_suffix:
		link_name = '%s.%s' % (str(v), SUFFIX,)
	else:
		link_name = str(v)
	#print 'making symlink. dirfile_src: %s. key_dir: %s. val: %s' % (dirfile_src, key_dir, str(v))
	dest = os.path.join(key_dir, link_name)
	'''
	if os.path.islink(dest):
		if os.path.realpath(dest) == dirfile_src:
			return
		## Degenerates!	 (note that first link gets to stay?)
		## (on the way out...)
		val_dir = os.path.join(key_dir, str(v))
		if not os.path.isdir(val_dir):
			os.mkdir(val_dir)
		degenerate_dir = os.path.join(val_dir, 'degenerates')
		if not os.path.isdir(degenerate_dir):
			os.mkdir(degenerate_dir)
		dirfile_name = os.path.split(dirfile_src)[1]
		new_dest = os.path.join(degenerate_dir, dirfile_name)
		try:
			os.symlink(dirfile_src, new_dest)
		except OSError:
			#print 'could not create link: %s -> %s' % (new_dest, dirfile_src,)
			pass
	else:
		os.symlink(dirfile_src, dest)		
		'''
	if not os.path.islink(dest):
		os.symlink(dirfile_src, dest)		

def make_tree(dirfile_src, extra_data, root_dir, filter_d):
	"""
	Really only make section of tree for given dirfile.
	"""
	for kv_order in permutations(extra_data):
		# Take head of the ordering, vs tail:
		try:
			k,v = kv_order[0]
		except:
			continue
		tail = kv_order[1:]
		key_dir = os.path.join(root_dir, k)
		if not os.path.isdir(key_dir):
			os.mkdir(key_dir)

		# Check if dirfile is fully specified:
		fine_filter = filter_d.copy()
		fine_filter[k] = v
		filtered = filter_all_extra_data(fine_filter)
		if len(filtered) == 1:
			make_symlink(dirfile_src, key_dir, v)
			continue
		else:
			#dirfile_name = os.path.split(os.path.realpath(dirfile_src))[1]
			dirfile_name = get_dirfile_name(dirfile_src)
			make_symlink(dirfile_src, root_dir, dirfile_name, add_suffix=False)

		'''
		if tail == ():
			# At the end of the rope. Make symlink
			make_symlink(dirfile_src, key_dir, v)
		else:
		'''
		if len(tail) != 0:
			# Recurse
			val_dir = os.path.join(key_dir, str(v))
			if not os.path.isdir(val_dir):
				os.mkdir(val_dir)
			make_tree(dirfile_src, tail, val_dir, fine_filter)

def place_dirfile_in_tree(dirfile_path):
	extra_data = get_extra_data(dirfile_path)
	make_tree(dirfile_path, extra_data, ROOT, {})
	
	# Move pesky link made in root directory to 'all' directory.
	dirfile_name = get_dirfile_name(dirfile_path)
	all_dir = os.path.join(ROOT, 'all')
	root_link = os.path.join(ROOT, dirfile_name)
	new_link = os.path.join(all_dir, dirfile_name)
	if not os.path.isdir(all_dir):
		os.mkdir(all_dir)
	if os.path.islink(root_link):
		os.rename(root_link, new_link)

def insert_into_queue(dirfile):
	"""
	Save dirfile's path in .queue.
	"""
	if os.path.isfile(QUEUE):
		f = file(QUEUE, 'a')
	else:
		f = file(QUEUE, 'w')
	f.write('%s\n' % os.path.realpath(dirfile))
	f.close()

def process_queue():
	"""
	Place all queue'd dirfiles into tree.
	"""
	if not os.path.isfile(QUEUE):
		return
	dirfiles = file(QUEUE, 'r').read().split('\n')
	n = 1
	for dirfile in dirfiles:
		if os.path.isdir(dirfile): # very light error checking
			print '%i: %s' % (n, dirfile)
			place_dirfile_in_tree(dirfile)
			n += 1
	os.remove(QUEUE)

def main():
	n = 0
	for dirfile in ALL_DIRFILES:
		place_dirfile_in_tree(dirfile)
		n += 1
		print '%i: %s' % (n, dirfile)


