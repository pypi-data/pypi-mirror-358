#include "encoder/sha1id/sha1id.h"
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

template <typename T>
void bind_sha1id(py::module& m, const std::string& class_name) {
  py::class_<SHA1ID<T>>(m, class_name.c_str())
      .def(py::init<>())
      .def("sha1id", &SHA1ID<T>::sha1id, "Compute SHA1ID", py::arg("data"), py::arg("gf_exp"));
}

PYBIND11_MODULE(idcodes_sha1id, m) {
  m.doc() = "Pybind11 bindings for SHA1ID class";  // Optional module docstring

  // Bind SHA1ID for different template types
  bind_sha1id<uint8_t>(m, "SHA1ID_U8");
  bind_sha1id<uint16_t>(m, "SHA1ID_U16");
  bind_sha1id<uint32_t>(m, "SHA1ID_U32");
  bind_sha1id<uint64_t>(m, "SHA1ID_U64");
}
