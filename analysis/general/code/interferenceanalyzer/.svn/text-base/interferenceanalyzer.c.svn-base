#include <stdio.h>
#include <stdlib.h>
#include <complex.h>
#include <math.h>

void intanalyzer_interfere(int nsources, double** source_locations, 
			   complex** source_amplitudes, double wavenumber, 
			   double* location,double* final_amp){
  /*This function finds the interference amplitudes at one point.  nsources is
   the number of sources, source_locations is a 2D array with the (x,y,z)
   coordinates of the sources, and source_amplitudes contains the complex
   amplitudes.  wavenumber is 2*pi/lambda, and location contains the (x,y,z)
   coordinates of the location for which the interference pattern should be
   calculated. The result is stored in final_amp: the 0th element is the
   amplitude in the x direction, the 1st in the y, and the 2rd in the z.*/
  complex x_sum=0;
  complex y_sum=0;
  complex z_sum=0;
  int i;
  for (i=0; i<nsources; i++){
    //Declaring displacements/
    double x_displacement = location[0]-source_locations[i][0];
    double y_displacement = location[1]-source_locations[i][1];
    double z_displacement = location[2]-source_locations[i][2];
    double distance_squared = x_displacement*x_displacement + 
      y_displacement*y_displacement+z_displacement*z_displacement;
    double distance = sqrt(distance_squared);
    //Deleting projection source_amplitudes along the direction of displacement.
    complex inner_product = x_displacement*source_amplitudes[i][0] +
      y_displacement*source_amplitudes[i][1] +
      z_displacement*source_amplitudes[i][2];
    complex projection_coefficient=inner_product/distance_squared;
    complex x_transverse_amplitude=source_amplitudes[i][0] -
      projection_coefficient*x_displacement;
    complex y_transverse_amplitude=source_amplitudes[i][1] -
      projection_coefficient*y_displacement;
    complex z_transverse_amplitude=source_amplitudes[i][2] - 
      projection_coefficient*z_displacement;
    //Implementing inverse_square_law.
    x_transverse_amplitude=x_transverse_amplitude/distance_squared;
    y_transverse_amplitude=y_transverse_amplitude/distance_squared;
    z_transverse_amplitude=z_transverse_amplitude/distance_squared;
    //Implementing additional phases
    complex wave_phase = cexp(I*(distance*wavenumber));
    x_sum=x_sum+x_transverse_amplitude*wave_phase;
    y_sum=y_sum+y_transverse_amplitude*wave_phase;
    z_sum=z_sum+z_transverse_amplitude*wave_phase;
  }
  //Finding final amplitude
  final_amp[0]=sqrt(creal(x_sum*conj(x_sum)));
  final_amp[1]=sqrt(creal(y_sum*conj(y_sum)));
  final_amp[2]=sqrt(creal(z_sum*conj(z_sum)));
}

void intanalyzer_interfere_all(int nsources, double** source_locations,
				   complex** source_amplitudes, 
				   double wavenumber, int nlocs,
				   double** locations,double** all_final_amps){
  /*This function finds the interference pattern at many different points.
   nlocs is the number of locations for which the pattern is to be calculated,
  and locations holds the coordinates of those locations.  For each location,
  intanalyzer_interfere is called, so refer to its docs for an explanation of
  nsources, source_locations, source_amplitdes, and wavenumber. The result is
  stored in all_final_amps, where all_final_amps[i] represents the x,y,z
  components of the amplitude at locations[i].*/
  int i;
  for (i=0; i<nlocs; i++){
    intanalyzer_interfere(nsources, source_locations, source_amplitudes, 
			  wavenumber, locations[i],all_final_amps[i]);
  }
}
