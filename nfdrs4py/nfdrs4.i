%module nfdrs4_bindings

%{
#include "../lib/NFDRS4/include/deadfuelmoisture.h"
#include "../lib/NFDRS4/include/dfmcalcstate.h"
#include "../lib/NFDRS4/include/lfmcalcstate.h"
#include "../lib/NFDRS4/include/livefuelmoisture.h"
#include "../lib/NFDRS4/include/nfdrs4.h"
#include "../lib/NFDRS4/include/CNFDRSParams.h"
#include "../lib/NFDRS4/include/nfdrs4calcstate.h"
#include "../lib/utctime/include/utctime.h"
%}

%include "typemaps.i"
%include "std_vector.i"
%include "std_string.i"


#ifdef SWIGPYTHON
typedef float FP_STORAGE_TYPE;
typedef long time_t;

%typemap(out) DoubleArray * {
  int len = $1->length;
  $result = PyList_New(len);
  for (int i = 0; i < len; i++) {
    PyObject *val = PyFloat_FromDouble($1->arrayPtr[i]);
    PyList_SetItem($result, i, val);
  }
}
#endif

/* Now include each header you want SWIG to parse: */
%include "../lib/NFDRS4/include/deadfuelmoisture.h"
%include "../lib/NFDRS4/include/livefuelmoisture.h"
%include "../lib/NFDRS4/include/dfmcalcstate.h"
%include "../lib/NFDRS4/include/lfmcalcstate.h"
%include "../lib/NFDRS4/include/nfdrs4calcstate.h"
%include "../lib/NFDRS4/include/nfdrs4.h"
%include "../lib/NFDRS4/include/CNFDRSParams.h"
%include "../lib/utctime/include/utctime.h"