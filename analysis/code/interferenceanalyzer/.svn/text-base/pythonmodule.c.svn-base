/*This file implements the intanalyzer Python module. It serves as an interface
between Python and interferenceanalyzer.c, which does the actual mathematical
calculations.*/
#include <Python.h>
#include "numpy/arrayobject.h"
#include <complex.h>
#include "interferenceanalyzer.h"
static const int NDIM=3; //most arrays are n x 3
//state of the interference analyzer
static int nsources=0;
static double** source_locs=NULL;
static complex** source_amps=NULL;

//function declarations
static void** create_2D_arr(int len,int width,int size);
static void free_2D_arr(void** arr, int len);
static PyObject* 
intanalyzer_set_sources(PyObject *self, PyObject *args);
static PyObject* intanalyzer_calculate(PyObject* self, PyObject *args);

static void** create_2D_arr(int len,int width,int size) {
  /*Helper function that returns a 2D array of length len and width width.
   The elements are size bytes. Returns NULL to indicate a memory error.*/
  int i=0;
  void** arr= malloc(len*sizeof(void*));
  if (arr==NULL) return NULL;
  for (i=0; i < len; i++) {
    arr[i]=malloc(width*size);
    if (arr[i]==NULL) {
      //free previously allocated memory
      free_2D_arr(arr,i);
      free(arr);
      return NULL;
    }
  }
  return arr;
}
static void free_2D_arr(void** arr, int len) {
  /*Frees the 2D array arr, which must have length len.*/
  int i=0;
  for (i=0; i < len; i++) {
    free(arr[i]);
  }
  free(arr);
}

//dictionary of methods that Python can call
static PyMethodDef AnalyzerMethods[] ={
  {"set_sources",intanalyzer_set_sources,METH_VARARGS,
   "Initialize with sources"},
  {"calc",intanalyzer_calculate,METH_VARARGS,"calculate for given locations"},
  {NULL,NULL,0,NULL}
};


static PyObject* 
intanalyzer_set_sources(PyObject *self, PyObject *args) {
  /*Sets the light sources. Arguments must be in this order: source locations,
    as a nx3 array, and source amplitudes as a complex nx3 array. Returns
    Py_None if successfull, and NULL for failure. Sets state variables
    nsources, source_locs, and source_amps.*/

  //if previous data exists, get rid of it
  if (source_locs != NULL) {
    assert(nsources!=0);
    free_2D_arr((void**)source_locs,nsources);
    source_locs=NULL;
  }
  if (source_amps != NULL) {
    assert(nsources!=0);
    free_2D_arr((void**)source_amps,nsources);
    source_amps=NULL;
  }
  nsources=0;
  int i;
  int j;
  PyArrayObject* sources; //source locations
  PyArrayObject* amps; //amplitudes of sources
  double** c_sources; //C array corresponding to sources
  complex** c_amps; //C array corresponding to amplitudes
  if (!PyArg_ParseTuple(args,"O!O!",&PyArray_Type,&sources,&PyArray_Type,
			&amps)) return NULL;
  if (sources==NULL) return NULL;
  if (amps==NULL) return NULL;
  if (amps->nd != 2 || amps->dimensions[1] != NDIM || 
      amps->descr->type_num!=NPY_CDOUBLE) {
    PyErr_SetString(PyExc_ValueError,"amplitude array dimensions must be nx3,"\
		    "of type complex float");
    return NULL;
  }
  if (amps->dimensions[0] == 0) {
    PyErr_SetString(PyExc_ValueError,"amplitudes array has no data!");
    return NULL;
  }
  if (sources->nd != 2 || sources->dimensions[1]!=NDIM ||
      sources->descr->type_num != NPY_DOUBLE) {
    PyErr_SetString(PyExc_ValueError,"sources array dimensions must be nx3,"\
		    "of type float");
    return NULL;
  }
  if (sources->dimensions[0]==0) {
    PyErr_SetString(PyExc_ValueError,"sources array has no data!");
    return NULL;
  }
  if (sources->dimensions[0] != amps->dimensions[0]) {
    PyErr_SetString(PyExc_ValueError,"sources array not of same length as"\
		    "amplitudes array!");
    return NULL;
  }
  //now convert sources array to C 2D array
  int n=sources->dimensions[0];
  c_sources=(double**) create_2D_arr(n,NDIM,sizeof(double));
  if (c_sources==NULL) return PyErr_NoMemory();
  for (i=0; i < n; i++) {
    for (j=0; j < NDIM; j++) {
      c_sources[i][j]=
	*(double*)(sources->data+i*sources->strides[0]+j*sources->strides[1]);
    }
  }
  c_amps=(complex**) create_2D_arr(n,NDIM,sizeof(complex));
  if (c_amps==NULL) {
    free_2D_arr((void**)c_sources, n);
    return PyErr_NoMemory();
  }
  for (i=0; i < n; i++) {
    for (j=0; j < NDIM; j++) {
      Py_complex curr=
	*(Py_complex*) (amps->data+i*amps->strides[0]+j*amps->strides[1]);
      c_amps[i][j]=curr.real+curr.imag*I;
    }
  }
  nsources=n;
  source_locs=c_sources;
  source_amps=c_amps;
  Py_RETURN_NONE;
}


static PyObject* intanalyzer_calculate(PyObject* self, PyObject* args) {
  /*This function calculates interference amplitudes for the given locations.
    The first argument should be a nx3 array of locations for which the
    amplitudes are calculated. The second argument is the wavenumber. Returns
    an nx3 array of amplitudes if calculation is successful; otherwise, returns
    NULL. Uses state variables nsources, source_locs, and source_amps.*/

  if (nsources==0) {
    PyErr_SetString(PyExc_ValueError,"no sources have been added!");
    return NULL;
  }
  PyArrayObject* locs;
  double** c_locs;
  double wavenum;
  if (!PyArg_ParseTuple(args,"O!d",&PyArray_Type,&locs,&wavenum)) return NULL;
  if (locs->nd != 2 || locs->dimensions[1] != NDIM || 
      locs->descr->type_num!=NPY_DOUBLE) {
    PyErr_SetString(PyExc_ValueError,"locations array dimensions must be nx3,"\
		    "of type float");
    return NULL;
  }
  if (locs->dimensions[0]==0) {
    PyErr_SetString(PyExc_ValueError,"locations array has no data!");
    return NULL;
  }  
  int nlocs=locs->dimensions[0];
  c_locs=(double**) create_2D_arr(nlocs,NDIM,sizeof(double));
  if (c_locs==NULL) return PyErr_NoMemory();
  int i;
  int j;
  for (i=0; i < nlocs; i++) {
    for (j=0; j < NDIM; j++) {
      c_locs[i][j]=
	*(double*)(locs->data+i*locs->strides[0]+j*locs->strides[1]);
    }
  }
  double** c_final_amps=(double**) create_2D_arr(nlocs,NDIM,sizeof(double));
  if (c_final_amps==NULL) {
    //must clean up previously allocated mem
    free_2D_arr((void**)c_locs,nlocs);
    return PyErr_NoMemory();
  }
  intanalyzer_interfere_all(nsources,source_locs,source_amps,wavenum,
			    nlocs,c_locs,c_final_amps);
  //prepare python array to return
  npy_intp dims[2]={nlocs,NDIM};
  PyArrayObject* final_amps=(PyArrayObject*) 
    PyArray_SimpleNew(2,dims,NPY_DOUBLE);
  if (final_amps==NULL) {
    free_2D_arr((void**)c_locs,nlocs);
    free_2D_arr((void**)c_final_amps,nlocs);
    return NULL;
  }
  double* data=(double*) final_amps->data;
  for (i=0; i < nlocs; i++) {
    for (j=0; j < NDIM; j++) {
      data[i*NDIM+j]=c_final_amps[i][j];
    }
  }
  free_2D_arr((void**)c_locs,nlocs);
  free_2D_arr((void**)c_final_amps,nlocs);
  return PyArray_Return(final_amps);
}


PyMODINIT_FUNC initintanalyzer(void)
{
  (void)Py_InitModule("intanalyzer",AnalyzerMethods);
  import_array();
}
