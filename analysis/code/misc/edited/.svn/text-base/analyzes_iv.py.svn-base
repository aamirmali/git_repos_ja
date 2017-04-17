from optparse import OptionParser
import os, sys, time
import numpy as np
from mce_data import MCEFile
import find_good_ivs
import array_ABS_cfg as config
import matplotlib.pyplot as plt
class adict:
    '''This class provides a convenient way of storing and accessing detector
    parameters. It stores every specified parameter--for instance, "ok"--in
    a n_row * n_col grid of the appropriate data type. At the end of
    initialization, "ok" would be a key in self.keys, and self.ok would be a
    n_row by n_col array filled with zeros.'''
    keys=[]
    
    def __init__(self, keys=None, types=None, shape=None):
        '''For every key in keys: (1) adds said key to self.keys, and
        (2) creates an attribute with name key and shape shape, with the
        datatype being the type in types with the same index as key. This
        attribute is an array filled with zeros.'''
        self.keys = []
        if keys != None:
            for k, t in zip(keys,types):
                setattr(self, k, np.zeros(shape, dtype=t))
                self.keys.append(k)

    def add_item(self, index, source):
        '''For every key in the dictionary source, sets attribute in self
        with name key such that its element at index has value
        source["key"].'''

        for k, v in source.iteritems():
            if k in self.keys:
                getattr(self,k)[index] = v
                
class runfile_block:
    """
    Write (especially) numpy arrays to a runfile-block file.
    """
    fout=None
    
    def __init__(self, filename, mode='w'):
        self.fout = open(filename, mode)

    def __del__(self):
        self.close()

    def write_scalar(self, key, value, format='%s'):
        self.fout.write(('<%s> '+format+'\n') % (key, value))

    def write_vector(self, key, value, format='%.6f'):
        _value = ' '.join([format % x for x in value])
        self.write_scalar(key, _value)
    
    def write_array(self, key, value, format='%.6f'):
        for c in range(value.shape[1]):
            self.write_vector(key % c, value[:,c], format)

    def close(self):
        if self.fout != None:
            self.fout.close()
        self.fout


def unwrap(data, period):
    ddata = data[...,1:] - data[...,:-1]
    ups = (ddata >  period/2).nonzero()
    dns = (ddata < -period/2).nonzero()
    for r, c, i in zip(*ups):
        data[r, c, i+1:] -= period
    for r, c, i in zip(*dns):
        data[r, c, i+1:] += period

def loadArrayParams(array_name=None):
    if array_name == None:
        array_name = open('/data/cryo/array_id').readline().strip()

    params = {'array': array_name,
              'source_file': filename}
    schema = [
        ('float', True,  ['Rfb', 'M_ratio', 'default_Rshunt', 'per_Rn_bias',
                          'bias_DAC_volts', 'bias_DAC_bits',
                          'fb_DAC_volts', 'fb_DAC_bits']),
        ('int',   True,  ['ncut_lim', 'use_srdp_Rshunt', 'n_bias_lines', 'bias_step']),
        ('float', False, ['fb_normalize', 'per_Rn_cut', 'psat_cut', 'good_shunt_range',
                          'Rbias_arr', 'Rbias_cable']),
        ('int',   False, ['bias_lines']),
        ]
    for dtype, single, keys in schema:
        for k in keys:
            value=config.__dict__[k]
            params[k]=value
            if single==False:
                params[k]=np.array(params[k])
    return params

def read_ascii(filename, data_start=0, comment_chars=[]):
    data = []
    for line in open(filename):
        w = line.split()
        if len(w) == 0 or w[0][0] in comment_chars: continue
        data.append([float(x) for x in w])
    return np.array(data).transpose()

#
# Main IV analysis routine
#

def analyze_IV_curve(bias, fb, deriv_thresh=5e-6):
    results = {'ok': False}
    n = bias.shape[0]
    i = 0
    dy = fb[1:] - fb[:-1]
    span = 12
    trans_start, transend = None, None
    # Look at all places where the derivative is negative.
    neg_idx = (dy[:-span]<0).nonzero()[0]
    # Find the first stable such point.
    for i in neg_idx:
        if np.median(dy[i:i+span]) <= 0:
            trans_start = i
            break
    else:
        return results
    # Look for large derivatives (transition) sc?
    big_idx = (dy[i:-span] > deriv_thresh).nonzero()[0] + i
    for i in big_idx:
        if np.median(dy[i:i+span]) > deriv_thresh:
            transend = i
            break
    else:
        transend=fb.shape[0]-1
#        return results

#    print trans_start,transend,bias[trans_start],bias[transend]
    trans_bias = bias[trans_start]
    normal_idx = ((bias > trans_bias+0.2)* (bias < trans_bias + 0.8)* \
                   (np.arange(n) <= n*3/4)).nonzero()[0]
    ok = len(normal_idx) > 1
    if not ok:
        return results
    results = dict(zip(['ok', 'trans_start', 'trans_end', 'trans_bias'],
                       [ok, trans_start, transend, trans_bias]))
    # Fit normal branch
    normfit = np.polyfit(bias[normal_idx], fb[normal_idx], 1)
    Rnorm, offset = normfit
    results.update(zip(['norm_offset', 'Rnorm', 'norm_idx0', 'norm_idx1'], \
                           [offset, Rnorm, min(normal_idx), max(normal_idx)]))
    # Fit super-conducting branch iff it exists
    if transend != fb.shape[0]-1:
        superfit = np.polyfit(bias[transend:], fb[transend:], 1)
        results.update(zip(['super_offset', 'Rsuper', 'super_idx0', 'super_idx1'],
                           [superfit[1], superfit[0], transend, fb.shape[0]-1]))

    return results

def plot_hists_to_file(cols,percent_Rns,Psats,percent_range,Psat_range,
                       filename,title_suffix=None,verbose=True):
    #Plots histograms of saturation power and percentage Rn values for all
    #detectors in cols, if the length of cols is non-zero. percent_Rns and
    #Psats are n_row*n_col arrays, filename is the destination file, and the
    #titles of the histograms are 'Psats for '+title_suffix and '%Rns for
    #'+title_suffix. If title_suffix is None, it is assigned to
    #'cols'+list of columns in cols. verbose indicates whether any errors should
    #be printed.
    plt.gcf().clear()
    if len(cols)==0: return
    if title_suffix==None:
        title_suffix='cols'
        for col in cols:
            title_suffix=title_suffix+' '+str(col)
    assert(percent_Rns.shape==Psats.shape)
    nrows=percent_Rns.shape[0]
    #collect all data
    all_Psats=[]
    all_percent_Rns=[]
    for col in cols:
        for row in range(0,nrows):
            Psat=Psats[row][col]
            percent_Rn=percent_Rns[row][col]
            if Psat>Psat_range[0] and Psat<Psat_range[1]:
                all_Psats.append(Psat)
            if percent_Rn>percent_range[0] and percent_Rn<percent_range[1]:
                all_percent_Rns.append(percent_Rn)
    plt.subplot(211)
    if len(all_Psats)!=0:
        plt.hist(all_Psats,range=Psat_range)
    elif verbose:
        print "These cols have no valid Psat data:",cols
    plt.title("Psats for "+title_suffix)
    plt.subplot(212)
    if len(all_percent_Rns)!=0:
        plt.hist(all_percent_Rns,range=percent_range)
    elif verbose:
        print "These cols have no valid %Rn data:",cols
    plt.title("%Rns for "+title_suffix)
    plt.savefig(filename)


def plot_linegraphs_to_file(filepattern,col,curr_row,end_row,
                            v_tes,i_tes,iv_data,rows_per_file):
    #Plots I-V and R-P for detectors in column col and rows curr_row
    #to end_row, including curr_row but not end_row. Save result to
    #filepattern%(curr_row/rows_per_file). V and I must be 3D arrays,
    #and the x axis runs from 0 to iv_data.super_idx0[row,col]
    formatset=['b','g','r','c','m','y','k','b--','g--','r--',
           'c--','m--','y--','k--','b-+','g-+','r-+','c-+','m-+',
           'y-+','k-+','b-^','g-^','r-^','c-^']
    pos_in_formatset=0
    plt.gcf().clear()
    for row in range(curr_row,end_row):
        idx=np.arange(0,iv_data.super_idx0[row,col])
        label='r'+str(row)+'c'+str(col)            
        #First, plot I vs. V
        plt.subplot(211)
        voltages=v_tes[row,col,idx]
        currents=i_tes[row,col,idx]
        format=formatset[pos_in_formatset]
        pos_in_formatset=(pos_in_formatset+1)%len(formatset)
        plt.plot(voltages,currents,format,label=label)

        #Now plot resistance vs. power
        plt.subplot(212)
        powers=v_tes[row,col,idx]*i_tes[row,col,idx]
        #factor of 1000 converts from Ohm to mOhm
        resistances=1000*v_tes[row,col,idx]/i_tes[row,col,idx]
        plt.plot(powers,resistances,format,label=label)

    plt.subplot(211).axis('tight')
    plt.title("Current (uA) vs. Voltage (uV)")
    plt.subplot(212).axis('tight')
    plt.title("Resistance (mOhm) vs. Power (pW)")
    #set legend column number, and remove annoying frame
    num_plots=end_row-curr_row
    ncols_legend=num_plots/8 #max 8 rows per legend col
    if num_plots%8!=0:
        ncols_legend+=1
    legend=plt.subplot(211).legend(ncol=ncols_legend)
    legend.get_frame().set_visible(False)
    legend=plt.subplot(212).legend(ncol=ncols_legend)
    legend.get_frame().set_visible(False)
    #write figure to file
    file_suffix=curr_row/rows_per_file
    plt.savefig(filepattern%file_suffix)

# Some basic MCE data
MCE_params = {
    'periods': {1: 2**19, 9: 2**24, 10: 2**28},
    'filtered': {1: 0, 9: 1, 10: 1},
    'filter_gains': {1: 1., 9: 1216., 10: 1216.}
    }

#
# Main
#

t0 = time.time()

o = OptionParser(usage="%prog [options] [iv_filename]")
o.add_option('--plot-dir', default=None,
             help='destination for graphs. Default is filename+_data')
o.add_option('--verbosity', default=2, type='int',
             help='give value from 0 to 2, inclusive')
o.add_option('--rf-file', default=None,
             help='destination .out file, or "none" to not generate. Default is filename+.out')
o.add_option('--bad-file',default=None,
             help='destination .bad file, or "none" to not generate. Default is filename+.bad')
o.add_option('--array', default=None,
             help='name of array. Default is value in /data/cryo/array_id.')
o.add_option('--with-rshunt-bug',action="store_true",
             help='simulate bug in IDL version')
o.add_option('--rows-per-file',default=11,type='int',
             help='number of rows per file for I-V and R-P plots')
opts, args = o.parse_args()

if len(args) != 1:
    o.error('Give exactly 1 IV filename.')

# Source data
filename = args[0]

# Destination for plots
if opts.plot_dir == None:
    opts.plot_dir = filename + '_data'
if opts.plot_dir == 'none':
    opts.plot_dir = None
else:
    if not os.path.exists(opts.plot_dir):
        os.makedirs(opts.plot_dir)

# Runfile output
if opts.rf_file == None:
    opts.rf_file = filename + '.out'
if opts.rf_file == 'none':
    opts.rf_file = None
if opts.bad_file==None:
    opts.bad_file=filename+'.bad'
if opts.bad_file=='none':
    opts.bad_file=None

# Load data and properties
filedata = MCEFile(filename)

if opts.array == None:
    opts.array = filedata.runfile.Item('FRAMEACQ','ARRAY_ID',array=False).strip()

# Load array description
ar_par = loadArrayParams(array_name=opts.array)

# Adjust...
ar_par['Rbias_arr'] += ar_par['Rbias_cable']  # Include cable
ar_par['Rfb'] += 50.                          # Include 50 ohms from RC

if ar_par['use_srdp_Rshunt']:
    ar_par['jshuntfile'] = os.getenv('MAS_SCRIPT')+'/srdp_data/'+ar_par['array']+ \
                           '/johnson_res.dat.C%02i'

# DAC <-> V conversions
dfb_ddac = ar_par['fb_DAC_volts'] / 2**ar_par['fb_DAC_bits']
dbias_ddac = ar_par['bias_DAC_volts'] / 2**ar_par['bias_DAC_bits']

data_mode = filedata.runfile.Item('HEADER','RB rc1 data_mode',type='int',array=False)
filtgain = MCE_params['filter_gains'][data_mode]
period = MCE_params['periods'][data_mode]

# Load, unwrap, rescale data to SQ1 FB DAC units.
data = filedata.Read(row_col=True).data
data_cols = np.array(filedata._NameChannels(row_col=True)[1])

unwrap(data, period)
unwrap(data, period/2)
data *= ar_par['fb_normalize'][data_cols].reshape(1,-1,1) / filtgain

# The size of the problem
n_row, n_col, n_pts = data.shape

# Read bias values
raw_bias = read_ascii(filename+'.bias', comment_chars=['<', '#'])[0]
if raw_bias.shape[0] != n_pts:
    raise RuntimeError, 'weird .bias file'

# Read shunt data
Rshunt = np.zeros((n_row, n_col))
if ar_par['use_srdp_Rshunt']:
    for c in range(n_col):
        sd = read_ascii(ar_par['jshuntfile']%c, comment_chars=['#'])
        rows, Rs = sd[0].astype('int'), sd[1]
        Rshunt[rows, c] = Rs

shunts_ok = (ar_par['good_shunt_range'][0] < Rshunt) * \
    (Rshunt < ar_par['good_shunt_range'][1])

Rshunt[~shunts_ok] = ar_par['default_Rshunt']
# AR3 exception (puke)
if ar_par['array'] == 'AR3':
    Rshunt[(col >= 24)*~shunts_ok] = 0.0007

# To volts
bias = raw_bias * dbias_ddac
fb = data * dfb_ddac

trans_start_index = np.zeros((n_row, n_col), dtype='int')
transend_index = np.zeros((n_row, n_col), dtype='int')
iv_ok = np.zeros((n_row, n_col), dtype='bool')
bias_offsets = np.zeros((n_row, n_col), dtype='float')
Rnorm = np.zeros((n_row, n_col), dtype='float')
span = 12


iv_results = {}

# Translation table for per-det results
keys = ['ok',
        'norm_offset', 'norm_idx0', 'norm_idx1', 'R_norm',
        'super_offset', 'super_idx0', 'super_idx1', 'R_super',
        'psat',
]
dtypes = ['bool',
          'float', 'int', 'int', 'float',
          'float', 'int', 'int', 'float',
          'float',
]

iv_data = adict(keys, dtypes, (n_row, n_col))
iv_checker=find_good_ivs.CheckIvs(filename,verbose=False)
is_off=np.zeros((n_row,n_col),dtype=int)
is_darksquid=np.zeros((n_row,n_col),dtype=int)
is_incomplete=np.zeros((n_row,n_col),dtype=int)
is_ramping=np.zeros((n_row,n_col),dtype=int)
is_undefined=np.zeros((n_row,n_col),dtype=int)
is_good=np.zeros((n_row,n_col),dtype=int)
badfile_buffer=''
for c in range(n_col):
    for r in range(n_row):
        iv_checker.iv_good(r,c)
        status=iv_checker.iv_statuses[r][c]

        if status=='good':
            is_good[r,c]=1
            det = analyze_IV_curve(bias, fb[r,c])
        else:
            det={'ok':False}
            badfile_buffer+='row '+str(r)+' col '+str(c)+' '+status+'\n'
            if status=='off':
                is_off[r,c]=1
            elif status=='darksquid':
                is_darksquid[r,c]=1
            elif status=='incomplete':
                is_incomplete[r,c]=1
            elif status=='ramping':
                is_ramping[r,c]=1
            elif status=='undefined':
                is_undefined[r,c]=1
            else:
                #should only happen if there's a typo
                assert(False)
        iv_data.add_item((r, c), det)
#        if det['ok']:
#            iv_data.add_item((r,c),det)
if opts.bad_file!=None:
    with open(opts.bad_file,'w') as f:
        f.write(badfile_buffer)
ok_rc = zip(*iv_data.ok.nonzero())
# Useful numbers
M_ratio, Rfb = ar_par['M_ratio'], ar_par['Rfb']
Rbias = ar_par['Rbias_arr'][ar_par['bias_lines'][data_cols]]  # per-column
            
# Remove offset from feedback data and convert to TES current (uA)
di_dfb = (1./50) / (1/Rfb+1/50.) / (-M_ratio*Rfb)
i_tes = 1e6 * di_dfb * (fb - iv_data.norm_offset.reshape(n_row, n_col, 1))

# Compute v_tes (uV) from bias voltage and i_tes
v_tes = 1e6 * Rshunt.reshape(n_row, n_col,1)* \
    (bias.reshape(1,1,-1)/Rbias.reshape(1,-1,1) - i_tes*1e-6)

# Recompute R_normal, saturation power
R = v_tes / i_tes
for r, c in ok_rc:
    i0, i1 = iv_data.norm_idx0[r,c], iv_data.norm_idx1[r,c]+1
    iv_data.R_norm[r,c] = R[r,c,i0:i1].mean()

perRn = R / iv_data.R_norm.reshape(n_row,n_col,1)
for r, c in ok_rc:
    norm_region = (perRn[r,c,:iv_data.super_idx0[r,c]] > 0.5).nonzero()[0]
    if norm_region.shape[-1] == 0:
        continue
    i0 = norm_region.max()
    iv_data.psat[r,c] = v_tes[r,c,i0] * i_tes[r,c,i0]

# Evaluate set points at target bias
def get_setpoints(perRn, idx, target):
    setpoints = np.zeros(perRn.shape[:2], dtype='int')
    for r, c in ok_rc:
        upper_region = (perRn[r,c,:idx[r,c]] > target).nonzero()[0]
        if upper_region.shape[-1] == 0:
            continue
        setpoints[r,c] = upper_region.max()
    return setpoints

# Bias choice; lo, choice, hi
setpoints = np.array([
        get_setpoints(perRn, iv_data.super_idx0, ar_par['per_Rn_bias']),
        get_setpoints(perRn, iv_data.super_idx0, 0.2),
        get_setpoints(perRn, iv_data.super_idx0, 0.8),
        ])

# Convert to DAC values
setpoints_dac = raw_bias[setpoints]

# Choose a bias for each bias line.
n_lines = ar_par['n_bias_lines']
bias_lines = ar_par['bias_lines'][data_cols] % n_lines
bias_points_dac = np.zeros(n_lines, dtype='float')
for line in range(n_lines):
    select = (bias_lines==line).reshape(1, n_col) * iv_data.ok
    dac = setpoints_dac[0,select]
    select = (dac>0)*(dac < 20000)
    bias_points_dac[line] = np.median(dac[select])

# Round.
bstep = ar_par['bias_step']
bias_points_dac = (bias_points_dac/bstep).round().astype('int')*bstep

# Evaluate perRn of each det at the chosen bias point
bias_points_dac_ar = bias_points_dac[bias_lines].reshape(1,n_col)
set_data = adict(
    ['index', 'perRn', 'v_tes', 'i_tes', 'p_tes', 'resp', 'keep_rec'],
    [int, float, float, float, float, float, bool],
    (n_row, n_col))

for r,c in ok_rc:
    i = (raw_bias <= bias_points_dac[bias_lines[c]]).nonzero()[0]
    if len(i) == 0: continue
    set_data.index[r,c] = i[0]
    set_data.perRn[r,c] = perRn[r,c,i[0]]
    set_data.v_tes[r,c] = v_tes[r,c,i[0]]
    set_data.i_tes[r,c] = i_tes[r,c,i[0]]

set_data.p_tes = set_data.v_tes*set_data.i_tes

# Responsivity
if opts.with_rshunt_bug:
    # Simulate bug in IDL version
    Rshunt_eff = Rshunt[:,n_col-1:]
else:
    Rshunt_eff = Rshunt

set_data.resp = -di_dfb*dfb_ddac * 1e-6*set_data.v_tes * \
    (1 - Rshunt_eff/set_data.perRn/iv_data.R_norm)
set_data.resp[~iv_data.ok] = 0.

# Cutting, cutting.

ok = iv_data.ok
p, r = set_data.p_tes[ok], set_data.perRn[ok]
p0,p1 = ar_par['psat_cut']
r0,r1 = ar_par['per_Rn_cut']

set_data.keep_rec[ok] = (p0<p)*(p<p1)*(r0<r)*(r<r1)

#
# Report
#

if opts.verbosity >= 2:
    print 'Good normal branches found in each column:'
    for c in range(n_col):
        print 'Column %2i = %4i' % (c, iv_data.ok[:,c].sum())

if opts.verbosity >= 1:
    if opts.with_rshunt_bug:
        print 'Rshunt bug is in!.'
        print
    print 'Recommended biases for target of %10.4f Rn' % ar_par['per_Rn_bias']
    for l in range(n_lines):
        print 'Line %2i = %6i' % (l, bias_points_dac[l])
    print
    print 'Cut limits at recommended biases:'
    print '%% R_n   %10.6f %10.6f' % (r0,r1)
    print 'Po (pW) %10.6f %10.6f' % (p0, p1)
    print
    print 'Total good normal branches              =  %4i' % iv_data.ok.sum()
    print 'Number of detectors within cut limits   =  %4i' % np.sum(set_data.keep_rec)

#
# Runfile block !
#


if opts.rf_file != None:
    if opts.verbosity >= 1:
        print 'Writing runfile block to %s' % opts.rf_file
    rf_out = runfile_block(opts.rf_file)
    rf_out.write_scalar('IV','')
    rf_out.write_scalar('iv_file', filename)
    rf_out.write_scalar('target_percent_Rn', 100*ar_par['per_Rn_bias'], '%i')
    rf_out.write_vector('bias_resistances_used', ar_par['Rbias_arr'], '%.3f')
    rf_out.write_vector('rec_biases', bias_points_dac, '%i')
    rf_out.write_vector('cut_per_Rn', ar_par['per_Rn_cut'], '%.6f')
    rf_out.write_vector('cut_bias_power(pW)', ar_par['psat_cut'], '%6f')
    rf_out.write_scalar('iv_curves_found', iv_data.ok.sum(), '%i')
    rf_out.write_scalar('detectors_within_cut', set_data.keep_rec.sum(), '%i')
    rf_out.write_array('Responsivity(W/DACfb)_C%i', set_data.resp, '%0.5e')
    rf_out.write_array('Percentage_Rn_C%i', set_data.perRn, '%.6f')
    rf_out.write_array('Bias_Power(pW)_C%i', set_data.p_tes, '%.5f')
    rf_out.write_array('Bias_Voltage(uV)_C%i', set_data.v_tes, '%.6f')
    rf_out.write_array('cut_rec_C%i', (~set_data.keep_rec).astype('int'), '%i')
    rf_out.write_array('is_off_C%i',is_off,'%i')
    rf_out.write_array('is_darksquid_C%i',is_darksquid,'%i')
    rf_out.write_array('is_incomplete_C%i',is_incomplete,'%i')
    rf_out.write_array('is_ramping_C%i',is_ramping,'%i')
    rf_out.write_array('is_undefined_C%i',is_undefined,'%i')
    rf_out.write_array('is_good_C%i',is_good,'%i')
    rf_out.write_scalar('/IV','')
    rf_out.close()
    
#
# Plot :P
#


if opts.plot_dir != None:
    if opts.verbosity >= 1:
        print 'Plotting (%8.3f)' % (time.time() - t0)

    #Before plotting line graphs, check whether opts.rows_per_file is valid
    if opts.rows_per_file<=0:
        print "Can't plot",opts.rows_per_file,"rows per file! Defaulting to 8."
        opts.rows_per_file=8
    elif opts.rows_per_file > n_row:
        print str(opts.rows_per_file)+" is more than the number of rows!"
        print "Defaulting to "+str(n_row)+", the number of rows"
        opts.rows_per_file=n_row
    #Begin plotting, by calling plot_to_file
    for col in range(0,n_col):
        curr_row=0
        filepattern=os.path.join(opts.plot_dir,'IV_plots_C%02i_%%02i.png'%col)
        while curr_row < n_row:
            end_row = curr_row + opts.rows_per_file
            if end_row > n_row:
                end_row = n_row
            plot_linegraphs_to_file(filepattern,col,curr_row,end_row,
                                    v_tes,i_tes,iv_data,
                                    opts.rows_per_file)
            curr_row = end_row
            
    #Now plot histograms
    #First, plot hist of all data
    filename=os.path.join(opts.plot_dir,'hist_all.png')
    plot_hists_to_file(range(n_col),set_data.perRn,set_data.p_tes,
                       config.per_Rn_cut,config.psat_cut,
                       filename,title_suffix='all cols',verbose=True)
    #now, figure out which cols to plot for each bias line
    cols_for_bias_lines=[[] for i in range(config.n_bias_lines)]
    if len(config.bias_lines) != n_col:
        print "bias_lines in config file is of incorrect length"
        sys.exit(1)
    for i in range(n_col):
        bias_line=config.bias_lines[i]
        if bias_line >= config.n_bias_lines:
            print "Invalid bias line in config file's bias_lines!"
            sys.exit(1)
        cols_for_bias_lines[bias_line].append(i)
    #now, plot hist for each bias line
    for i in range(config.n_bias_lines):
        filename_suffix='hist_biasline%02i.png'%i
        filename=os.path.join(opts.plot_dir,filename_suffix)
        plot_hists_to_file(cols_for_bias_lines[i],set_data.perRn,
                           set_data.p_tes,config.per_Rn_cut,config.psat_cut,
                           filename,verbose=False)

if opts.verbosity >= 1:
    print 'Analysis complete (%8.3f)' % (time.time() - t0)

