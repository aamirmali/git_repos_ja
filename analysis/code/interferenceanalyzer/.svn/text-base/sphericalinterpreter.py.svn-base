import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import ticker
import intanalyzer
import code.common.drawer as drawer
from code.common import exceptions
import gaussianfitter as gf

class SphericalInterpreter:


    distance=None
    theta_domain=np.array([])
    phi_domain=np.array([])
    x_amplitudes=np.array([])
    y_amplitudes=np.array([])
    z_amplitudes = np.array([])
    norm_squared = np.array([])
    """Gaussian model parameters in this order: max E^2, center phi, center
    theta, std phi, std theta, R^2. All angles in pixels, not degrees."""
    gauss_fit=np.array([])

    def __init__(self, method, args):
        try:
            self.set_domain_and_data(method, args)
            self.set_amplitudes(method, args)
            self.gauss_fit=gf.fitgaussian(self.norm_squared)
        except KeyError as error:
            raise KeyError ("One of the keys were not initialized\n" 
                            + str(error))
    
    def set_domain_and_data(self, method, args):
        if method == "raw_data":
            if args["size"][0]<=0 or args["size"][1]<=0:
                raise exceptions.StupidityError(
                    'Currently plotting a picture of nonpositive size.')
            theta_pixels=math.ceil((args["size"][0])*args["resolution"])
            phi_pixels=math.ceil(args["size"][1]*args["resolution"])
            theta_half_width=theta_pixels/(2.0*args["resolution"])
            phi_half_width=phi_pixels/(2.0*args["resolution"])
            theta_min = args["center"][0]-theta_half_width
            theta_max = args["center"][0]+theta_half_width
            phi_min = args["center"][1]-phi_half_width
            phi_max = args["center"][1]+phi_half_width
            theta_domain=np.linspace(theta_min, theta_max, theta_pixels, 
                                     endpoint=False)
            phi_domain=np.linspace(phi_min, phi_max, phi_pixels, 
                                   endpoint=False)
            distance = args["distance"]
        elif method == "npz_file":
            try:
                theta_domain = args["npz_dict"]['theta_domain']
                phi_domain = args["npz_dict"]['phi_domain']
                distance = args["npz_dict"]['distance'][0]
            except KeyError as error:
                raise KeyError ("The npz file does not have all the required"\
                                    " keys.\n" + str(error))
        else:
            raise ValueError ("the parameter 'method' is invalid.")
        self.theta_domain = theta_domain
        self.phi_domain = phi_domain
        self.distance = distance
    
    
    def set_amplitudes(self, method, args):
        if method == "raw_data":
            speed_of_light = 299792458.0
            wavelength = speed_of_light/args["frequency"]
            wavenumber = 2*np.pi/wavelength
            theta_pixels = self.theta_domain.size
            phi_pixels = self.phi_domain.size
            meshedgrid=np.meshgrid(self.theta_domain, self.phi_domain)
            unshaped_transposed_coor_array=np.radians(
                np.vstack((meshedgrid[0].flat, meshedgrid[1].flat)))
            unshaped_coor_array=(
                unshaped_transposed_coor_array.transpose(1,0))
            unshaped_cartesian_coor_array=(
                self.get_unshaped_cartesian_coor_array(
                    unshaped_coor_array))
            intanalyzer.set_sources(
                args["source_locations"], args["source_amplitudes"])
            unshaped_amplitudes=intanalyzer.calc(
                unshaped_cartesian_coor_array, wavenumber)
            x_amplitudes = unshaped_amplitudes[:,0].reshape(
                phi_pixels, theta_pixels)
            y_amplitudes = unshaped_amplitudes[:,1].reshape(
                phi_pixels, theta_pixels)
            z_amplitudes = unshaped_amplitudes[:,2].reshape(
                phi_pixels, theta_pixels)
            norm_squared = x_amplitudes**2 + y_amplitudes**2 + z_amplitudes**2
        elif method == "npz_file":
            try:
                x_amplitudes = args["npz_dict"]["x_amplitudes"]
                y_amplitudes = args["npz_dict"]["y_amplitudes"]
                z_amplitudes = args["npz_dict"]["z_amplitudes"]
                norm_squared = args["npz_dict"]["norm_squared"]
            except KeyError as error:
                raise KeyError ("The npz file does not have all the required"\
                                    " keys.\n" + str(error))
        self.x_amplitudes = x_amplitudes
        self.y_amplitudes = y_amplitudes
        self.z_amplitudes = z_amplitudes
        self.norm_squared = norm_squared


    def get_unshaped_cartesian_coor_array(self, spherical_coordinate_array):
        transposed_spherical_coordinate_array=(
            spherical_coordinate_array.transpose(1,0))
        transposed_cartesian_coordinate_array=(
            np.empty((3,spherical_coordinate_array.shape[0])))
        transposed_cartesian_coordinate_array[0]=(
            self.distance*np.cos(transposed_spherical_coordinate_array[0])
            *np.sin(transposed_spherical_coordinate_array[1]))
        transposed_cartesian_coordinate_array[1]=(
            self.distance*np.sin(transposed_spherical_coordinate_array[0]))
        transposed_cartesian_coordinate_array[2]=(
            self.distance*np.cos(transposed_spherical_coordinate_array[0])
            *np.cos(transposed_spherical_coordinate_array[1]))
        cartesian_coordinate_array=(
            transposed_cartesian_coordinate_array.transpose(1,0))
        return cartesian_coordinate_array    

    def draw_profile(self, axis):
        #draws cross section through maximum along either constant theta
        #or constant phi (axis=phi or axis=theta, respectively)
        plt.xlabel(axis)
        plt.ylabel("E^2")
        if self.gauss_fit==None:
            print "Can't draw profile; Gaussian fit did not succeed!"
            return
        if axis=='theta':
            phi=int(round(self.gauss_fit[1]))
            plt.title("Cross-section at phi="+str(self.phi_domain[phi])
                      +" deg")
            plt.plot(self.theta_domain,self.norm_squared[phi])
            
        elif axis=='phi':
            theta=int(round(self.gauss_fit[2]))
            plt.title("Cross-section at theta="+str(self.theta_domain[theta])
                      +" deg")
            plt.plot(self.phi_domain,self.norm_squared[:,theta])
        else:
            raise ValueError(axis+" is not a valid axis")
        
    def draw(self, array_name, limit=None):
        #array_name is what to draw: x Amplitudes, y Amplitudes, z Amplitudes
        xlabel='theta'
        ylabel='phi'
        colorbar_label=array_name
        def xformat(x, i):
            return self.theta_domain[x]
        def yformat(x, i):
            return self.phi_domain[x]
        theta_pixels = self.theta_domain.size
        phi_pixels = self.phi_domain.size
        if theta_pixels>=100:
            xtick_factor=int(theta_pixels/50)*5
        else:
            xtick_factor=5
        if phi_pixels>=100:
            ytick_factor=int(phi_pixels/50)*5
        else:
            ytick_factor=5
        if array_name == "x Amplitudes":
            drawer.draw_image(self.x_amplitudes, title=array_name, 
                              xlabel=xlabel, ylabel=ylabel, 
                              limit=limit, colorbar_label=colorbar_label)
            drawer.set_ticks(plt.gca(), xformat, yformat, 
                             xtick_factor, ytick_factor)
        elif array_name == "y Amplitudes":
            drawer.draw_image(self.y_amplitudes, title=array_name,
                              xlabel=xlabel, ylabel=ylabel, 
                              limit=limit, colorbar_label=colorbar_label)
            drawer.set_ticks(plt.gca(), xformat, yformat, 
                             xtick_factor, ytick_factor)
        elif array_name == "z Amplitudes":
            drawer.draw_image(self.z_amplitudes, title=array_name, 
                              xlabel=xlabel, ylabel=ylabel, 
                              limit=limit, colorbar_label=colorbar_label)
            drawer.set_ticks(plt.gca(), xformat, yformat, 
                             xtick_factor, ytick_factor)
        elif array_name == "Norm Squared":
            drawer.draw_image(self.norm_squared, title=array_name, 
                              xlabel=xlabel, ylabel=ylabel, 
                              limit=limit, colorbar_label=colorbar_label)
            drawer.set_ticks(plt.gca(), xformat, yformat, 
                             xtick_factor, ytick_factor)
        else:
            raise KeyError ("the parameter 'array_name' is invalid.")


    def to_analysis_file(self, filepath):
        meshed_domain=np.meshgrid(self.theta_domain, self.phi_domain)
        label = ['theta','phi','x Amplitude','y Amplitude','z Amplitude',
                 'Norm Squared']
        gaussfit_label="Gaussian fit (max E^2, theta(deg), phi(deg), std "\
            "theta, std phi, R^2):\n"
        if self.gauss_fit==None:
            g_params="fitting failed"
        else:
            max_Esqr=self.gauss_fit[0]
            theta_int=self.theta_domain[1]-self.theta_domain[0]
            theta=self.theta_domain[int(round(self.gauss_fit[2]))]
            theta_std=self.gauss_fit[4]*theta_int
            phi_int=self.phi_domain[1]-self.phi_domain[0]
            phi=self.phi_domain[int(round(self.gauss_fit[1]))]
            phi_std=self.gauss_fit[3]*phi_int
            R_sqr=self.gauss_fit[5]
            g_params="%.2e, %.1f, %.1f, %.2f, %.2f, %.3f"%(max_Esqr,theta,phi,
                                                           theta_std,phi_std,
                                                           R_sqr)
        analysis_array = np.dstack([meshed_domain[0], meshed_domain[1], 
                                    self.x_amplitudes, self.y_amplitudes, 
                                    self.z_amplitudes, self.norm_squared])
        with open(filepath, 'w') as analysis_file:
            np.set_printoptions(threshold=np.inf, linewidth=np.inf)
            analysis_file.write('distance: ' + str(self.distance) + 'm\n')
            analysis_file.write(gaussfit_label + str(g_params)+"\n")
            analysis_file.write(str(label) + '\n')
            analysis_file.write(str(analysis_array))
            #reverting to original options
            np.set_printoptions(threshold=1000, linewidth=75)

            
    def to_npz_file(self, filepath):
        distance_array = np.array([self.distance])
        np.savez(
            filepath, distance=distance_array, 
            theta_domain=self.theta_domain, phi_domain=self.phi_domain, 
            x_amplitudes=self.x_amplitudes, y_amplitudes=self.y_amplitudes, 
            z_amplitudes=self.z_amplitudes, norm_squared=self.norm_squared)
