import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.simplefilter('ignore',np.RankWarning)

class IV:
    ''' Calibrates and analyses a single IV'''
    data=None
    '''raw IV output data for a single channel'''
    db_bias=None
    '''Applied detector bias in raw DAC units '''
    Rsh=None
    '''shunt resistor value'''
    filtgain=None
    '''gain if butterworth filter'''
    dac_bits=None
    '''number of bits of fb dac '''
    M_ratio=None
    '''Mutual inductance ration, i.e factor to convert changes in detector current to changes in fb current '''
    Rfb=None
    '''Resistance of SQ1 feedback, includes 50ohm resistor on board, resistor on backplane (15K?), and resistance of wires.'''
    db_bits=None
    '''number of bits of the detector bias '''
    Rdetb=None
    '''Resistance of detector bias line, includes 200 Ohm resistor on board, 200Ohm resiston on backplane, and resistance of lines '''
    fb_DAC_volts=None
    '''Max voltage range of fb DAC '''
    db_DAC_volts=None
    '''Max voltage range of detector bias DAC '''
    def __init__(self, data=None, db_bias=None, Rsh=None, filtgain=None, dac_bits=None, M_ratio=None, Rfb=None, db_bits=None, Rdetb=None, fb_DAC_volts=None, db_DAC_volts=None,index_normal=None):
        self.data=data
        self.db_bias=db_bias
        self.Rsh=Rsh
        self.filtgain=filtgain
        self.dac_bits=dac_bits
        self.M_ratio=M_ratio
        self.Rfb=Rfb
        self.db_bits=db_bits
        self.Rdetb=Rdetb
        self.fb_DAC_volts=fb_DAC_volts
        self.db_DAC_volts=db_DAC_volts
        self.index_normal=index_normal
        self.Ites_fbDAC=fb_DAC_volts/filtgain/2**dac_bits/M_ratio/Rfb
        self.Ibias_dbDAC=db_DAC_volts/2**db_bits/Rdetb
        self.Ites,self.Vtes,self.Rtes,self.Ptes,self.Ibias=self.IV_calib()
        self.dIbias_dItes=self.dIbias_dItes()
        self.resp=self.resp()
        self.Lin=self.Lin()
        self.tau_factor=self.tau_factor()
        self.inf_tr,self.inf_sc=self.find_transition_end_points()
        self.Rn=self.calc_Rn()
        self.Psat_inter=self.calc_Psat_inter(self.Rn)
        self.Psat=self.calc_Psat(self.Rn)

    def find_fb_offset(self):
        fb=self.data[0:self.index_normal]
        db=self.db_bias[0:self.index_normal]
        fb_slope=np.diff(fb)
        fit=np.polyfit(db,fb,1)
        return fit
    def IV_calib(self):
        slope,offset=self.find_fb_offset()
        Ites=(self.data-offset)*self.Ites_fbDAC
        Ibias=self.db_bias*self.Ibias_dbDAC
        Vtes=self.Rsh*(Ibias-Ites)
        Rtes=Vtes/Ites
        Ptes=Ites*Vtes
        return Ites, Vtes, Rtes, Ptes,Ibias
    def dIbias_dItes(self):
        dIbias_dItes=(self.Ibias[1]-self.Ibias[0])/np.diff(self.Ites)
        return dIbias_dItes
    def resp(self):
        resp=self.Rsh*self.Ites[1:]*self.dIbias_dItes
        return resp
    def Lin(self):
        '''Lin/(1+beta)'''
        Lin=-1/(self.resp/self.Vtes[1:]+1)
        return Lin
    def alpha(self, G, To):
        '''alpha/(1+beta)'''
        alpha=self.Lin*G*To/self.Ptes[1:]
        return alpha
    def tau_factor(self):
        '''tau_eff/tau, tau=C/G '''
        tau_factor=1+((self.Ibias[1:]/self.Ites[1:]-2)*self.dIbias_dItes**-1)
        return tau_factor
    def detbias_dac_to_Ibias(self,target_bias_dac):
        target_bias=target_bias_dac*self.Ibias_dbDAC
        return target_bias
    def inflection_point(self):
        dItes=np.diff(self.Ites)
        index=np.where(dItes > 0)[0][0]
        bias_dac=self.db_bias[index]
        return bias_dac
    def low_pass(self, x, dn, a):
        y=np.zeros(len(x))
        alpha=dn/(a+dn)
        y[0]=x[0]
        for i in np.arange(len(x)-1)+1:
            y[i]=alpha*x[i]+(1-alpha)*y[i-1]
        return y
    def run_median(self,x,num):
        y=np.zeros(len(x))
        for i in np.arange(len(x)):
            if i<num:
                y[i]=np.median(x[0:i+num])
            elif i> len(x)-num:
                y[i]=np.median(x[i-num:-1])
            else:
                y[i]=np.median(x[i-num:i+num])
        return y

    def run_mean(self,x,num):
        y=np.zeros(len(x))
        for i in np.arange(len(x)):
            if i<num:
                y[i]=np.mean(x[0:i+num])
            elif i> len(x)-num:
                y[i]=np.mean(x[i-num:-1])
            else:
                y[i]=np.mean(x[i-num:i+num])
        return y
    def find_transition_end_points(self,thresh_tr=1e-8,buff=10):
        dItes=np.diff(self.Ites)
        inf_tr,inf_sc=0,len(dItes)
        inf_tr_array=buff+np.where(dItes[buff:] > thresh_tr)[0]
        if len(inf_tr_array) < 11:
            return inf_tr,inf_sc
        for i in np.arange(len(inf_tr_array)):
            if inf_tr_array[i]+buff > len(dItes)-1:
                return inf_tr,inf_sc
            if np.median(dItes[inf_tr_array[i]:inf_tr_array[i]+buff]) > thresh_tr:
                inf_tr=inf_tr_array[i]+buff
                break
        inf_sc_array=inf_tr+np.where(dItes[inf_tr:] == 0)[0] # because cleaning sets to zero big sc jump
        if len(inf_sc_array) < 11:
            return inf_tr,inf_sc
        for i in np.arange(len(inf_sc_array)):
            if inf_sc_array[i]+buff > len(dItes)-1:
                return inf_tr,inf_sc
            if np.median(dItes[inf_sc_array[i]:inf_sc_array[i]+buff]) < thresh_tr:
                inf_sc=inf_sc_array[i]
                break
        return inf_tr,inf_sc



    def fit_transition(self, poly_order=6,plot=False):
        inf_tr,inf_sc=self.find_transition_end_points()
        if inf_sc > inf_tr:
            z=np.polyfit(self.Ibias[inf_tr:inf_sc],self.Ites[inf_tr:inf_sc],poly_order)
        else:
            resp=np.zeros(len(self.Ibias))
            tau_factor=np.zeros(len(self.Ibias))
            return resp,tau_factor
        Ites_func=np.poly1d(z)
        dItes_dIbias_func=np.poly1d(np.polyder(z))
        resp=self.Rsh*Ites_func(self.Ibias)*dItes_dIbias_func(self.Ibias)**-1
        tau_factor=1+((self.Ibias/Ites_func(self.Ibias)-2)*dItes_dIbias_func(self.Ibias))
        if plot == True:
            tau_factor_filt=self.low_pass(self.tau_factor[inf_tr:inf_sc],1.,10.)
            tau_factor_run_median=self.run_median(self.tau_factor[inf_tr:inf_sc],20.)
            tau_factor_run_mean=self.run_mean(self.tau_factor[inf_tr:inf_sc],20.)
            z_tau=np.polyfit(self.Ibias[inf_tr:inf_sc],tau_factor_filt,poly_order)
            tau_factor_func=np.poly1d(z_tau)
            fig=plt.figure(1001)
            ax1=fig.add_subplot(311)
            ax1.plot(self.Rtes,self.Ites)
            ax1.plot(self.Rtes[inf_tr:inf_sc],self.Ites[inf_tr:inf_sc])
            ax1.plot(self.Rtes[inf_tr:inf_sc],Ites_func(self.Ibias[inf_tr:inf_sc]))
            ax1.set_xlabel("Rtes")
            ax1.set_ylabel("Ites")

            ax2=fig.add_subplot(312)
            resp0=self.resp
            ax2.plot(self.Rtes[inf_tr:inf_sc],resp0[inf_tr:inf_sc])
            ax2.plot(self.Rtes[inf_tr:inf_sc],resp[inf_tr:inf_sc])
            ax2.set_xlabel("Rtes")
            ax2.set_ylabel("Resp W/A")

            ax3=fig.add_subplot(313)
            ax3.plot(self.Ibias[inf_tr:inf_sc],tau_factor[inf_tr:inf_sc])
#            ax3.plot(self.Ibias[inf_tr:inf_sc],self.tau_factor[inf_tr:inf_sc])
            ax3.plot(self.Ibias[inf_tr:inf_sc],tau_factor_run_median)
            ax3.plot(self.Ibias[inf_tr:inf_sc],tau_factor_run_mean)
#            ax3.plot(self.Ibias[inf_tr:inf_sc],tau_factor_filt)
            ax3.plot(self.Ibias[inf_tr:inf_sc],tau_factor_func(self.Ibias[inf_tr:inf_sc]))
            ax3.set_xlabel("Ibias (A)")
            ax3.set_ylabel("tau factor")

            plt.show()
        return resp, tau_factor

    def fit_params(self, poly_order=6):
        inf_tr,inf_sc=self.inf_tr,self.inf_sc
        if inf_sc > inf_tr:
            z=np.polyfit(self.Ibias[inf_tr:inf_sc],self.Ites[inf_tr:inf_sc],poly_order)
        else:
            z=np.zeros(poly_order+1)
        return z
    def calc_Rn(self):
        if self.inf_tr > 2:
            Rn=np.mean(self.Rtes[0:self.inf_tr/2])
        else:
            Rn=0
        return Rn
    def calc_Psat(self, Rn, PRn=0.8):
        if self.inf_sc > self.inf_tr:
            index_Psat=np.where(self.Rtes[self.inf_tr:self.inf_sc]/Rn < PRn)[0]
        else:
            index_Psat =[]

        if len(index_Psat) == 0:
            Psat=0
        else:
            Psat=self.Ptes[self.inf_tr:self.inf_sc][index_Psat[0]]
#        print "Psat 80%Rn=", Psat
        return Psat
    def calc_Psat_inter(self, Rn, PRn_min=0.75, PRn_max=0.85):
        if self.inf_sc > self.inf_tr:
            PRn_trans=self.Rtes[self.inf_tr:self.inf_sc]/Rn
            index_Psat=np.where(np.logical_and(PRn_trans > PRn_min,PRn_trans < PRn_max))
        else:
            index_Psat =[]

        if len(index_Psat) == 0:
            Psat=0
        else:
#            print index_Psat
#            print self.Ptes[self.inf_tr:self.inf_sc][index_Psat]
            Psat=np.median(self.Ptes[self.inf_tr:self.inf_sc][index_Psat])
#            print self.Ptes[self.inf_tr:self.inf_sc][index_Psat]
#            print 'Psat= ',Psat
        return Psat
