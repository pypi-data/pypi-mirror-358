#include "encoder/sha256id/sha256id.h"
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

template <typename T>
void bind_sha256id(py::module& m, const std::string& class_name) {
  py::class_<SHA256ID<T>>(m, class_name.c_str())
      .def(py::init<>())  // Default constructor

      // Bind sha256id function
      .def("sha256id", &SHA256ID<T>::sha256id, "Compute SHA256ID", py::arg("data"),
           py::arg("gf_exp"));
}

PYBIND11_MODULE(idcodes_sha256id, m) {
  m.doc() = "Pybind11 bindings for SHA256ID class";  // Optional module docstring

  // Bind SHA256ID for different template types
  bind_sha256id<uint8_t>(m, "SHA256ID_U8");
  bind_sha256id<uint16_t>(m, "SHA256ID_U16");
  bind_sha256id<uint32_t>(m, "SHA256ID_U32");
  bind_sha256id<uint64_t>(m, "SHA256ID_U64");
}
