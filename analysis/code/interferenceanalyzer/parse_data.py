import numpy as np
import intanalyzer
import matplotlib.pyplot as plt
from matplotlib import ticker
def read_data(filename):
    with open(filename) as f:
        first_line=f.readline()
        num_x=int(first_line.split()[0])
        num_y=int(first_line.split()[1])
        x_coors=np.empty(num_x)
        y_coors=np.empty(num_y)
        for i in range(num_x):
            line=f.readline()
            x_coors[i]=float(line)/100
        for i in range(num_y):
            line=f.readline()
            y_coors[i]=float(line)/100
        #now, make a list of all the tuples that follow
        all_E_fields=[]
        line=f.readline()
        while line!='':
            line_vals=line.split()
            for element in line_vals:
                real=eval(element)
                efield=real[0]+1j*real[1]
                all_E_fields.append(efield)
            line=f.readline()
        num_sources=num_x*num_y
        source_locs=np.empty((num_sources,3))
        source_amps=np.zeros((num_sources,3),dtype=complex)
        tot_counter=0
        out_counter=0
        #load all source locations from x_coors and y_coors, and all amplitudes
        #from all_E_fields
        for i in range(num_x):
            for j in range(num_y):
                source_index=i*num_y+j
                source_locs[source_index][0]=x_coors[i]
                source_locs[source_index][1]=y_coors[j]
                source_locs[source_index][2]=0
                source_amps[source_index][0]=all_E_fields[source_index*3]
                source_amps[source_index][1]=all_E_fields[source_index*3+1]
                source_amps[source_index][2]=all_E_fields[source_index*3+2]
#                source_amps[source_index][0]=0.1
#                source_amps[source_index][1]=0
#                source_amps[source_index][2]=0
                tot_counter+=1
                if x_coors[i]**2+y_coors[j]**2 > 0.125*0.125:
                    out_counter+=1
                    source_amps[source_index][0]=0
                    source_amps[source_index][1]=0
                    source_amps[source_index][2]=0
#                print x_coors[i],y_coors[j],source_amps[source_index][0]
#                source_amps[source_index][0]=1
#                source_amps[source_index][1]=0
#                source_amps[source_index][2]=0
        return (source_locs,source_amps)


def analyze(): 
    ret=read_data('zcon.dat')
    source_locs=ret[0]
    source_amps=ret[1]

    #hack
    hacky_arr_x=np.ones((301,301))
    hacky_arr_y=np.ones((301,301))
    hacky_arr_z=np.ones((301,301))
    hacky_arr_t=np.ones((301,301))
    for i in range(len(source_locs)):
        x_pixel=(source_locs[i][0]+0.15)*1000
        y_pixel=(source_locs[i][1]+0.15)*1000
        x_pixel=int(round(x_pixel))
        y_pixel=int(round(y_pixel))
#        print x_pixel,y_pixel
        final_amplitude=source_amps[i][0]**2+source_amps[i][1]**2+source_amps[i][2]**2
        final_amplitude=np.sqrt(final_amplitude)
        hacky_arr_x[y_pixel][x_pixel]=np.abs(source_amps[i][0])
        hacky_arr_y[y_pixel][x_pixel]=np.abs(source_amps[i][1])
        hacky_arr_z[y_pixel][x_pixel]=np.abs(source_amps[i][2])
        hacky_arr_t[y_pixel][x_pixel]=final_amplitude


    append_ver=np.zeros((1000,301))
    print "trial",hacky_arr_x.shape
    append_hor=np.zeros((2301,1000))
    hacky_arr_x=np.vstack((append_ver,hacky_arr_x))
    hacky_arr_x=np.vstack((hacky_arr_x,append_ver))
    hacky_arr_x=np.hstack((append_hor,hacky_arr_x))
    hacky_arr_x=np.hstack((hacky_arr_x,append_hor))
    print hacky_arr_x.shape
    """
    plt.title("X")
    plt.imshow(hacky_arr_x,interpolation='nearest')
    plt.colorbar()
    plt.figure()
    
    plt.title("Y")
    plt.imshow(hacky_arr_y)
    plt.colorbar()
    plt.figure()

    plt.title("Z")
    plt.imshow(hacky_arr_z)
    plt.colorbar()
    plt.figure()

    plt.title("Total")
    plt.imshow(hacky_arr_t)
    plt.colorbar()
    plt.figure()
    plt.show()
    """
    fourier=np.fft.fft2(hacky_arr_x)
    plt.imshow(np.log10(np.abs(fourier)),interpolation='nearest')
    plt.colorbar()
    plt.figure()
    plt.show()

    #end hack

    intanalyzer.set_sources(source_locs,source_amps)
    det_locs=[]
    width=1.
    height=1.
    xres=50
    yres=50
    z=10
    true_x_off=0.19
    true_y_off=-0.00776
    x_offset=true_x_off*z - float(width)/2
    y_offset=true_y_off*z - float(height)/2
    freq=145e9
    c=3e8
    wavenum=2*np.pi*freq/c
    for i in range(0,xres):
        for j in range(0,yres):
            x=float(i)*width/xres + x_offset
            y=float(j)*height/yres + y_offset
            det_locs.append([x,y,z])
    det_locs=np.array(det_locs)
    result=intanalyzer.calc(det_locs,wavenum)
    two_d_result=np.zeros((yres,xres))
    for i in range(0,xres):
        for j in range(0,yres):
            val=result[i*yres+j]
            two_d_result[j][i]=np.sqrt(val[0]**2+val[1]**2+val[2]**2)
#            two_d_result[j][i]=val[2]
    plt.imshow(two_d_result,interpolation='nearest')
    #convert to angular scale
    convert_x=width/xres/z * 180/np.pi
    convert_y=height/yres/z * 180/np.pi
    def x_format_func(x,i):
        return x*convert_x
    def y_format_func(y,i):
        return y*convert_y
    ax=plt.subplot(111)
    x_formatter=ticker.FuncFormatter(x_format_func)
    y_formatter=ticker.FuncFormatter(y_format_func)
    ax.xaxis.set_major_formatter(x_formatter)
    ax.yaxis.set_major_formatter(y_formatter)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(1./convert_x))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(1./convert_y))
    plt.colorbar()
    plt.show()
