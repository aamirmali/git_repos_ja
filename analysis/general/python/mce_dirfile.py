"""
Module for retrieving data from dirfile
of mce data.
"""
import re
import os
import glob
import subprocess as sp
import numpy as np
import pygetdata as gd

tesdata_re = re.compile('.*tesdatar([0-9]{2})c([0-9]{2})$')
r_indx = 8
c_indx = 11

# Someday fill this out better
dtypes = {
	gd.INT16: np.int16,
	gd.INT32: np.int32,
	gd.FLOAT32: np.float32,
	gd.FLOAT64: np.float64,
}

# Hopefully this field is always written:
test_entry = 'tesdatar00c00'

def hk_frag_kludge(dirfile_path):
	"""
	Not proud of this.
	For some reason, cannot get nframes of dirfile
	while fragment is hanging around?
	Temporarily move dirfile's format file...
	"""
	sp.check_call(["cp", os.path.join(dirfile_path, "format"), os.path.join(dirfile_path, ".format")])
	orig_format_file = file(os.path.join(dirfile_path, '.format'), 'r')
	orig_format_lines = orig_format_file.readlines()
	orig_format_file.close()
	format_file = file(os.path.join(dirfile_path, 'format'), 'w')
	new_format_lines = filter(lambda L: not L.startswith("/INCLUDE"), orig_format_lines)
	format_file.writelines(new_format_lines)
	format_file.close()

def undo_hk_frag_kludge(dirfile_path):
	sp.check_call(["mv", os.path.join(dirfile_path, ".format"), os.path.join(dirfile_path, "format")])

def get_filt_name(field):
	""" Assumes field is raw data, like 'tesdatar12c21' """
	return 'filt_' + field[7:]

def get_row_col_from_field(field):
	r = int(field[r_indx:r_indx+2])
	c = int(field[c_indx:c_indx+2])
	return r, c

def get_num_row_col(fields):
	max_row = -1
	max_col = -1
	for field in fields:
		r, c = get_row_col_from_field(field)
		if r > max_row:
			max_row = r
		if c > max_col:
			max_col = c
	return max_row+1, max_col+1

def getdata(dirfile_path):
	"""
	Returns numpy array of shape
	(n_rows, n_cols, n_samples)
	of raw data from dirfile_path.
	Raw data is assumed to be of the
	form filt_r<row#>c<col#>
	"""
	df_files = glob.glob(os.path.join(dirfile_path, '*'))
	# No... don't do it... you are going to regret it...
	tes_data_fields = [os.path.split(field)[1] for field in filter(tesdata_re.match, df_files)]
	# Seriously, 10 seconds after writing that you can't figure out what it does. Asshole.
	num_row, num_col = get_num_row_col(tes_data_fields)
	dirfile = gd.dirfile(dirfile_path, gd.RDONLY)
	gd_data_type = dirfile.entry(test_entry).data_type;
#	num_samples = dirfile.nframes * dirfile.get_entry(test_entry).spf
	num_samples = len(dirfile.getdata(test_entry, gd_data_type, num_frames=dirfile.nframes))
#	print num_samples
	data = np.zeros((num_row, num_col, num_samples), dtype=dtypes[gd_data_type])
	for raw_field in tes_data_fields:
		r,c = get_row_col_from_field(raw_field)
		field = get_filt_name(raw_field)
		try:
			data[r,c,:] = dirfile.getdata(field, gd_data_type, num_frames=dirfile.nframes)
		except IndexError:
			print 'shape: ', np.shape(data)
			print '(r,c) = (%i,%i)' % (r, c,)
			raise IndexError

	return data
