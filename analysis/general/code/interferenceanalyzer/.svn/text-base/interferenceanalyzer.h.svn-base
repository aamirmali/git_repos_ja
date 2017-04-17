/*This function finds the interference amplitudes at one point.  nsources is
  the number of sources, source_locations is a 2D array with the (x,y,z)
  coordinates of the sources, and source_amplitudes contains the complex
  amplitudes.  wavenumber is 2*pi/lambda, and location contains the (x,y,z)
  coordinates of the location for which the interference pattern should be
  calculated. The result is stored in final_amp: the 0th element is the
  amplitude in the x direction, the 1st in the y, and the 2rd in the z.*/
void intanalyzer_interfere(int nsources, double** source_locations, 
			   complex** source_amplitudes, double wavenumber, 
			   double* location,double* final_amp);


/*This function finds the interference pattern at many different points.  nlocs
   is the number of locations for which the pattern is to be calculated, and
   locations holds the coordinates of those locations.  For each location,
   intanalyzer_interfere is called, so refer to its docs for an explanation of
   nsources, source_locations, source_amplitdes, and wavenumber. The result is
   stored in all_final_amps, where all_final_amps[i] represents the x,y,z
   components of the amplitude at locations[i].*/
void intanalyzer_interfere_all(int nsources, double** source_locations,
			       complex** source_amplitudes, double
			       wavenumber, int nlocs, double** locations,
			       double** all_final_amps);
