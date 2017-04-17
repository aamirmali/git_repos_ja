import scipy.signal as sig
import matplotlib.pyplot as plt
import numpy as np


def freq_filter(data,fsample=399,fcrit='default',ftype='lowpass_butter',
                plot_data=False,plot_freq_response=False,plot_psd=False):
    """Filters the data. fsample is the sampling frequency. ftype is what type
    of filter to use: lowpass_butter, lowpass_bessel, or bandpass.  fcrit are
    the critical frequencies. It must be a float if ftype is lowpass_bessel, an
    array-like object of length 2 if ftype is lowpass_butter, and an array-
    like object of length 4 if ftype is bandpass, with the frequencies ordered
    from lowest to highest. plot_data, plot_freq_response, and plot_psd causes
    the function to plot the corresponding information. Returns the filtered
    data."""
    if ftype=='lowpass_butter':
        if fcrit=='default':
            fcrit=(20,30)
        wp=float(fcrit[0])/(fsample/2.)
        ws=float(fcrit[1])/(fsample/2.)
        (b,a)=sig.iirdesign(wp,ws,3,30,ftype='butter')
    if ftype=='lowpass_bessel':
        if fcrit=='default':
            fcrit=20
        ws=fcrit/(fsample/2.)
        (b,a)=sig.iirfilter(9,ws,btype='lowpass',ftype='bessel')
    if ftype=='bandpass':
        if fcrit=='default':
            fcrit=(5,8,11,14)
        wp=np.zeros(2,dtype='float')
        ws=np.zeros(2,dtype='float')
        ws[0]=fcrit[0]
        ws[1]=fcrit[3]
        wp[0]=fcrit[1]
        wp[1]=fcrit[2]
        wp /= fsample/2.
        ws /= fsample/2.
        (b,a)=sig.iirdesign(wp,ws,3,30,ftype='butter')
        
    filtered_data=sig.lfilter(b,a,data)
    if plot_data:
        plt.figure()
        plt.plot(data)
        plt.plot(filtered_data)
    if plot_freq_response:
        plt.figure()
        (w,h)=sig.freqz(b,a)
        h=np.abs(h)
        x=np.linspace(0,fsample/2.,len(w))
        plt.plot(x,h)
    if plot_psd:
        plt.figure()
        fourier_orig=np.fft.rfft(data).real
        psd_orig=fourier_orig*fourier_orig.conjugate()
        fourier_filt=np.fft.rfft(filtered_data).real
        psd_filt=fourier_filt*fourier_filt.conjugate()
        x=np.linspace(0,fsample/2.,len(psd_orig))
        plt.plot(x,psd_orig)
        plt.plot(x,psd_filt)
        plt.xlabel("Frequency(Hz)")
    return filtered_data

