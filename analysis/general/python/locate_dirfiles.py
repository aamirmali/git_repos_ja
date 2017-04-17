#!/usr/bin/env python
"""
Module for locating dirfiles by their '.extra_data.p' file
"""
import os
import glob
import pickle
# stupid python... __not__ method should be a thing
from operator import not_ as negate
# I'm so sorry... of course I don't mean it python! I love you!

#DATA_ROOT = os.path.realpath(os.path.join(os.environ['MAS_DATA'], '..'))
DATA_ROOT = os.path.realpath('/data/cryo/')
GLOB_SEARCH_STR = os.path.join(DATA_ROOT, '*', '*', '.extra_data.p')

BACKUP_SEARCH_STR = os.path.join(DATA_ROOT, '*', '*', '.extra_data_backup.p')

def unique_files(file_list):
	"""
	file_list will contain duplicates from sym links.
	This removes sym-link induced duplicates.
	"""
	unique_list = set()
	for f in file_list:
		unique_list.add(os.path.realpath(f))
	return list(unique_list)

def get_all_extra_data_paths():
	file_list = glob.glob(GLOB_SEARCH_STR)
	return unique_files(file_list)

#def get_all_backup_data_paths():
#	file_list = glob.glob(BACKUP_SEARCH_STR)
#	return unique_files(file_list)
def diff_dicts(d1, d2):
	"""
	Return how the dictionaries differ
	"""
	keys = list(set(d1.keys()).union(d2.keys()))
	vals = {}
	for k in keys:
		if not d1.has_key(k):
			vals[k] = (None, d2[k])
		elif not d2.has_key(k):
			vals[k] = (d1[k], None)
		elif d1[k] != d2[k]:
			vals[k] = (d1[k], d2[k])	
		else:
			pass
	return vals

def diff_backup_and_current_data():
	"""
	If backup and current extra data differ,
	will show path, and the discrepancy
	"""	
	for p in get_all_extra_data_paths():
		dirfile = os.path.realpath(os.path.dirname(p))
		backup_p = os.path.join(dirfile, '.extra_data_backup.p')
		data = pickle.load(file(p, 'r'))
		backup = pickle.load(file(backup_p, 'r'))
		diff = diff_dicts(data, backup)
		if diff != {}:
			print '%s: %s' % (dirfile, diff,)

def try_convert_to_numeric(raw_val):
	"""
	First attempt to convert to int, then float.
	If both are impossible, return arg unchanged.
	"""
	try:
		val = int(raw_val)
	except ValueError:
		pass
	else:
		return val
	try:
		val = float(raw_val)
	except ValueError:
		pass
	else:
		return val
	return raw_val


def update_pickles():
	"""
	This will go through all extra data pickles,
	and try to convert values to numerics if possible.
	"""
	dict_by_path = dict([(f, pickle.load(file(f, 'r')),) for f in get_all_extra_data_paths()])
	for f in dict_by_path:
		d = dict_by_path[f]
		# Copy original dictionary just in case this fucks up:
		new_fname = os.path.join(os.path.split(f)[0], '.extra_data_backup.p')
		pickle.dump(d, file(new_fname, 'w'))
		# Now do the conversion:
		for k in d:
			if type(d[k]) is str:
				d[k] = try_convert_to_numeric(d[k])
		pickle.dump(d, file(f, 'w'))

def filter_by_value(val, verbose=True):
	"""
	Returns paths where some extra data has the value
	matching the passed arg. Useful if you can't remember
	whether the key is 'scan_group_name', 'raster_group_name',
	or just plain old 'group_name'.
	Default setting is to print out information about what key
	has associated value stored with it. Setting verbose=False
	will stop the function from barfing on your screen.
	"""
	if verbose:
		print '<dirfile-path>: <key> = <value>'
		print '-------------------------------'
	extra_data_files = get_all_extra_data_paths()
	dict_by_path = dict([(f, pickle.load(file(f, 'r')),) for f in extra_data_files])
	matches = []
	for f in dict_by_path:
		d = dict_by_path[f]
		for k in d:
			if d[k] == val:
				dirfile = os.path.split(f)[0]
				if verbose:
					print '%s: %s = %s' % (dirfile, k, d[k],)
				matches.append(dirfile)
	if len(matches) == 0:
		print 'no matching dirfiles found'
	return matches

def filter_all(**kwargs):
	"""
	Returns list of paths for dirfiles which have the ".extra_data.p" pickle,
	and for which that pickle has all required keys and values.

	For example, calling:
	$ filter_all(raster_group_name="jimi")
	will give you list of paths to all dirfiles with raster_group_name as jimi.
	$ filter_all(scan_type='raster')
	would give all raster scans.
	"""
	extra_data_files = get_all_extra_data_paths()
	dict_by_path = dict([(f, pickle.load(file(f, 'r')),) for f in extra_data_files])
	paths = []
	for f in dict_by_path:
		d = dict_by_path[f]
		if len(filter(negate, [d.has_key(k) and d[k] == kwargs[k] for k in kwargs])) == 0:
			paths.append(os.path.split(f)[0])
	return paths

def show_all_extra_data(*args, **kwargs):
	"""
	Prints out a list of what extra data is "out there".
	Will list available keys, and all associated values.
	This function might help for knowing what to search against,
	or help you keep unique-valued fields unique-valued, if that makes sense.

	You can specify specific extra data keys on the command line, and you will
	only see their values.

	If you would like a dictionary returned with the printed data,
	supply kwarg return_data (any value)
	"""
	extra_data_files = get_all_extra_data_paths()
	dicts = dict([(f, pickle.load(file(f, 'r')),) for f in extra_data_files])
	keys = set()
	for f in dicts:
		keys = keys.union(dicts[f].keys())	
	keys = list(keys)
	values = {} # you can get rid of this guy... originally for returning during debugging.
	for k in keys:
		if len(args) != 0 and k not in args:
			continue
		values[k] = set()
		for i in dicts:
			if dicts[i].has_key(k):
				values[k].add(dicts[i][k])
		values[k] = list(values[k])
		if not kwargs.has_key('silent'):
			print 'Keyword "%s" values:' % k
			for v in values[k]:
				print '    %s' % str(v)
			print
	if kwargs.has_key('return_data'):
		return values

def show_dirfile_extra_data(dirfile_path, *args):
	"""
	Given path to dirfile, will print out the
	extra data associated with that dirfile.
	"""
	d = pickle.load(file(os.path.join(dirfile_path, '.extra_data.p'), 'r'))
	if len(args) == 0:
		for k in d:
			print '%s: %s' % (k, str(d[k]),)
		return # simply so the next for loop isn't embedded in an else clause?

	for arg in args:
		if d.has_key(arg):
			print '%s: %s' % (arg, str(d[arg]),)
		else:
			print '%s: key not found' % arg

'''
def delete_key(key):
	"""
	Remove a certain key from all data.
	Very dangerous!!!
	Useful if you were goofing around way back when,
	and want to cover your tracks.
	"""
	vals = show_all_extra_data(key, return_data=True, silent=True)[key]

	for val in vals:
		dirfiles = filter_all(**{key: val})
		for dirfile in dirfiles:
			fname = os.path.join(dirfile, '.extra_data.p')
			extra_data = pickle.load(file(fname, 'r'))
			# Backup the pickle, just in case:
			new_fname = os.path.join(dirfile, '.extra_data_backup.p')
			pickle.dump(extra_data, file(new_fname, 'w'))
			# now remove piece of data:
			extra_data.pop(key)
			pickle.dump(extra_data, file(fname, 'w'))
'''	

def get_raster_scans():
	return filter_all(scan_type='raster')

def get_raster_scan_group(group_name):
	return filter_all(raster_group_name=group_name)

