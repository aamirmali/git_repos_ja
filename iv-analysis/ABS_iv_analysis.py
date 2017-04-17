import numpy as np
import argparse
import iv
import filehandler as fh
from clean_timestream import Clean
from ABS_param import ABS_param

parser=argparse.ArgumentParser(description= 'analyses the ABS array ivs, generates a .out2 ', formatter_class=argparse.ArgumentDefaultsHelpFormatter,fromfile_prefix_chars='@')

parser.add_argument('filename', type=str,help='filename to analyze, expects a .run and a .out file exist')

parser.add_argument('-savedir', type=str , default='',help='save directory of .out2 file')
args=parser.parse_args()


filename=args.filename
ABS=ABS_param()
savedir=args.savedir

#print '\n'
#print filename
data=fh.get_mce_data(filename,row_col=True)
db_bias=np.genfromtxt(filename+'.bias',skiprows=1)
target_bias_DAC_array=fh.IV_data_to_arr(filename+'.out','rec_biases')
#print target_bias_DAC_array

target_index_array=np.zeros([ABS.num_rows,ABS.num_cols])
Ibias_array=np.zeros([ABS.num_rows,ABS.num_cols])
Ites_array=np.zeros([ABS.num_rows,ABS.num_cols])
Vtes_array=np.zeros([ABS.num_rows,ABS.num_cols])
Rtes_array=np.zeros([ABS.num_rows,ABS.num_cols])
Ptes_array=np.zeros([ABS.num_rows,ABS.num_cols])
resp_array=np.zeros([ABS.num_rows,ABS.num_cols])
PRn_array=np.zeros([ABS.num_rows,ABS.num_cols])
inf_tr_array=np.zeros([ABS.num_rows,ABS.num_cols])
inf_sc_array=np.zeros([ABS.num_rows,ABS.num_cols])
resp_fit_array=np.zeros([ABS.num_rows,ABS.num_cols])
tau_factor_fit_array=np.zeros([ABS.num_rows,ABS.num_cols])


for col in np.arange(ABS.num_cols):
    Rsh=ABS.Rshunt_cols[col]
    bias_line=ABS.bias_lines[col]
    target_bias_DAC=target_bias_DAC_array[bias_line]
    for row in np.arange(ABS.num_rows):
#        print 'col=',col,'row=',row
        data_tes=data[row,col,:]
        if np.median(np.diff(data_tes[0:ABS.index_normal])) > 0:
            data_tes=data_tes*-1
        clean=Clean()
        data_tes=clean.data_fix_jumps(data_tes)
        tes=iv.IV(data=data_tes,db_bias=db_bias,Rsh=Rsh,filtgain=ABS.filtgain,Rfb=ABS.Rfb,Rdetb=ABS.Rdetb, index_normal=ABS.index_normal, dac_bits=ABS.dac_bits, M_ratio=ABS.M_ratio, db_bits=ABS.db_bits, fb_DAC_volts=ABS.fb_DAC_volts, db_DAC_volts=ABS.db_DAC_volts)

        Ibias_target=tes.detbias_dac_to_Ibias(target_bias_DAC)
        target_index_center=np.where(tes.Ibias < Ibias_target)[0][0]
        if target_index_center > len(tes.Ibias)-ABS.num/2:
            target_index_center=len(tes.Ibias)-ABS.num/2

        target_index=np.arange(ABS.num)+target_index_center-ABS.num/2
        target_index_array[row,col]=target_index_center


        Ites_array[row,col]=np.median(tes.Ites[target_index])
        Vtes_array[row,col]=np.median(tes.Vtes[target_index])
        Rtes_array[row,col]=np.median(tes.Rtes[target_index])
        Ptes_array[row,col]=np.median(tes.Ptes[target_index])
        Ibias_array[row,col]=np.median(tes.Ibias[target_index])
        
        Rnormal=np.median(tes.Rtes[0:ABS.index_normal])
        PRn_array[row,col]=np.median(tes.Rtes[target_index]/Rnormal) 
        resp_array[row,col]=np.median(tes.resp[target_index])

        inf_tr_array[row,col]=tes.inf_tr
        inf_sc_array[row,col]=tes.inf_sc

        tr_fit=tes.fit_transition(plot=False)
        resp_fit_array[row,col]=np.mean(tr_fit[0][target_index])
        tau_factor_fit_array[row,col]=np.mean(tr_fit[1][target_index])


savefilename=savedir+filename.split('/')[-1]+'.out2'
#print savefilename
f=open(savefilename,'w')
fh.printout('target_index',np.int0(target_index_array),f)
fh.printout('Ibias_(uA)',np.round(Ibias_array*1e6,1),f)
fh.printout('Ites_(uA)',np.round(Ites_array*1e6,1),f)
fh.printout('Vtes_(nV)',np.round(Vtes_array*1e9,1),f)
fh.printout('Rtes_(mOhms)',np.round(Rtes_array*1e3,1),f)
fh.printout('Ptes_(pW)',np.round(Ptes_array*1e12,1),f)
fh.printout('PRn',np.round(PRn_array*1e2,0),f)
fh.printout('resp',np.round(resp_array*1e9,1),f)
fh.printout('inf_tr',np.int0(inf_tr_array),f)
fh.printout('inf_sc',np.int0(inf_sc_array),f)
fh.printout('resp_fit',np.round(resp_fit_array*1e9,1),f)
fh.printout('tau_factor_fit',np.round(tau_factor_fit_array,3),f)
f.close()
