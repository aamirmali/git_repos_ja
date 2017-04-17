import numpy as np
import matplotlib.pyplot as plt


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
    def __init__(self, data, db_bias, Rsh, filtgain=1218., dac_bits=14, M_ratio=8.5, Rfb=15166., db_bits=16, Rdetb=518., fb_DAC_volts=1.0, db_DAC_volts=2.5):
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
        self.Ites_fbDAC=fb_DAC_volts/filtgain/2**dac_bits/M_ratio/Rfb
        self.Ibias_dbDAC=db_DAC_volts/2**db_bits/Rdetb
    def find_fb_offset(self,index_normal=20):
        fb=self.data[0:index_normal]
        db=self.db_bias[0:index_normal]
        fb_slope=np.diff(fb)
        fit=np.polyfit(db,fb,1)
        return fit
    def IV_calib(self, index_normal=20):
        slope,offset=self.find_fb_offset(index_normal)
        Ites=(self.data-offset)*self.Ites_fbDAC
        Ibias=self.db_bias*self.Ibias_dbDAC
        Vtes=self.Rsh*(Ibias-Ites)
        Rtes=Vtes/Ites
        Ptes=Ites*Vtes
        return Ites, Vtes, Rtes, Ptes,Ibias
    def resp(self, index_normal=20):
        Ites,Vtes,Rtes,Ptes,Ibias=self.IV_calib(index_normal)
        Ibias=self.db_bias*self.Ibias_dbDAC
        dIbias_dItes=(Ibias[1]-Ibias[0])/np.diff(Ites)
        resp=self.Rsh*Ites[1:]*dIbias_dItes
        return resp
    def alpha(self, G, To, index_normal=20):
        Ites,Vtes,Rtes,Ptes,Ibias=self.IV_calib(index_normal)
        alpha=-1/(self.resp(index_normal)/Vtes[1:]+1)*G*To/Ptes[1:]
        return alpha
    def Lin(self,index_normal=20):
        Ites,Vtes,Rtes,Ptes,Ibias=self.IV_calib(index_normal)
        Lin=-1/(self.resp(index_normal)/Vtes[1:]+1)
        return Lin
    def detbias_dac_to_Ibias(self,tbias_dac):
        tbias=tbias_dac*self.Ibias_dbDAC
        return tbias
    def inflection_point(self, index_normal):
        Ites,Vtes,Rtes,Ptes,Ibias=self.IV_calib(index_normal)
        dItes=np.diff(Ites)
        index=np.where(dItes > 0)[0][0]
        bias_dac=self.db_bias[index]
        return bias_dac
