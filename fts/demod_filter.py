import numpy as np
import matplotlib.pyplot as plt


class demod_filter:
    def __init__(self, freq_mod, freq_filter):
        self.fm=freq_mod
        self.f_filt=freq_filter

    def demod(self,data,samp_rate):
        num=len(data)
        theta=2*np.pi*np.arange(num)/samp_rate*self.fm
        demod=np.cos(theta)+1j*np.sin(theta)
        d=data*demod# demod step
        d_fft=np.fft.fft(d)# filter demod step
        fft_freq=np.fft.fftfreq(num,1./samp_rate)
        index_filter=np.where(np.abs(fft_freq) > self.f_filt)[0]
        d_fft[index_filter]=0# filter demod step
        d_filter=np.abs(np.fft.ifft(d_fft))# demod step
        return d_filter, d_fft


