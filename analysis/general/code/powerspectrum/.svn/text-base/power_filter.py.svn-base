import scipy.signal as sig
import matplotlib.pyplot as plt
import numpy as np
def calc_pow_response(b11,b12,b21,b22,k1,k2,freqs):
    """Calculates power response based on coefficients."""
    #numerator of both transfer functions is the same
    b=[1,2,1]
    #denominators of transfer functions aren't
    H1_a=np.array([1,b11,b12])
    H2_a=np.array([1,b21,b22])
    (w,freq_response_1)=sig.freqz(b,H1_a,worN=freqs)
    (w,freq_response_2)=sig.freqz(b,H2_a,worN=freqs)
    freq_response=freq_response_1*freq_response_2*2**(-k1)*2**(-k2)
    pow_response=freq_response*freq_response.conjugate()
    return pow_response.real

def calc_pow_response2(real_samp_freq,fcutoff,freqs):
    """Calculates power response based on sampling frequency and 3dB cutoff
    frequency"""
    wcrit=fcutoff/(real_samp_freq/2.)
    (b,a)=sig.iirfilter(4,wcrit,
                        btype='lowpass')
    (w,freq_response)=sig.freqz(b,a,worN=freqs)
    pow_response=(freq_response*freq_response.conjugate()).real
    return pow_response

def get_pow_response(type,n_points,eff_samp_freq,real_samp_freq=None,b11=None,
                   b12=None,b21=None,b22=None,k1=None,k2=None):
    """Gets the power response of the filter. If type=1 or type=2, k1 and k2
    are both set to zero; therefore, this function does NOT account for filter
    gain if type is not 255.

    type can be 1, 2, 3, or 255, and corresponds to fltr_type. n_points is the
    number of points to return in the filter response. eff_samp_freq is the
    cutoff frequency of the filter, and real_samp_freq is the actual sampling
    frequency. The rest of the parameters are properties of the filter.

    Returns an array representing the power response at n_points points between
    0 and pi*eff_samp_freq/real_samp_freq, inclusive."""
    if type==1:
        real_samp_freq=15151.
        fcutoff=122.226
    elif type==2:
        real_samp_freq=30000.
        fcutoff=75
    elif type==3:
        real_samp_freq=15151.
        fcutoff=60
    elif type==255:
        if real_samp_freq==None or b11==None or b12==None or b21==None or\
                b22==None or k1==None or k2==None:
            raise ValueError("One or more required parameters not specified")
    else:
        raise ValueError("Type must be 1,2,or 255")
    omega_upper=np.pi*eff_samp_freq/real_samp_freq
    freqs=np.linspace(0,omega_upper,n_points)
    if type!=255:
        response=calc_pow_response2(real_samp_freq,fcutoff,freqs)
    else:
        response=calc_pow_response(b11,b12,b21,b22,k1,k2,freqs)
#    plt.figure()
#    x=np.linspace(0,399./2,len(response))
#    plt.plot(x,response**2)
#    plt.figure()
#    plt.show()
    return response
