#include "pybind11/pybind11.h"

namespace py = pybind11;

float fn(float a, float b){
    return a + b;
}

PYBIND11_MODULE(pypearl, handle){
    handle.doc() = "Module Documentation";
    handle.def("float_add", &fn);
}