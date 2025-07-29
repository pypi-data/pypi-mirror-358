#include "encoder/rsid/rsid.h"
#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

template <typename T>
void bind_rsid(py::module& m, const std::string& class_name) {
  py::class_<RSID<T>, GF<T>>(m, class_name.c_str())
      .def(py::init<>())  // Default constructor

      // Bind rsid function
      .def(
          "rsid",
          [](RSID<T>& self, const std::vector<T>& message, T tag_pos, py::array_t<T> exp_arr,
             py::array_t<T> log_arr, uint16_t gf_exp) {
            // Convert numpy arrays to raw pointers
            py::buffer_info exp_info = exp_arr.request();
            py::buffer_info log_info = log_arr.request();

            if (exp_info.ndim != 1 || log_info.ndim != 1) {
              throw std::runtime_error("exp_arr and log_arr must be 1-dimensional arrays");
            }

            T* exp_ptr = static_cast<T*>(exp_info.ptr);
            T* log_ptr = static_cast<T*>(log_info.ptr);

            return self.rsid(message, tag_pos, exp_ptr, log_ptr, gf_exp);
          },
          "Perform RSID encoding", py::arg("message"), py::arg("tag_pos"), py::arg("exp_arr"),
          py::arg("log_arr"), py::arg("gf_exp"))

      // Bind rsid_upto_gf2x16 function
      .def(
          "rsid_upto_gf2x16",
          [](RSID<T>& self, const std::vector<T>& message, T tag_pos, py::array_t<T> exp_arr,
             py::array_t<T> log_arr, uint32_t gf_size) {
            // Convert numpy arrays to raw pointers
            py::buffer_info exp_info = exp_arr.request();
            py::buffer_info log_info = log_arr.request();

            if (exp_info.ndim != 1 || log_info.ndim != 1) {
              throw std::runtime_error("exp_arr and log_arr must be 1-dimensional arrays");
            }

            T* exp_ptr = static_cast<T*>(exp_info.ptr);
            T* log_ptr = static_cast<T*>(log_info.ptr);

            return self.rsid_upto_gf2x16(message, tag_pos, exp_ptr, log_ptr, gf_size);
          },
          "Perform RSID encoding for GF sizes up to 2^16", py::arg("message"), py::arg("tag_pos"),
          py::arg("exp_arr"), py::arg("log_arr"), py::arg("gf_size"))

      // Bind rsid_upto_gf2x64 function
      .def("rsid_upto_gf2x64", &RSID<T>::rsid_upto_gf2x64,
           "Perform RSID encoding for GF sizes up to 2^64", py::arg("message"), py::arg("tag_pos"),
           py::arg("gf_exp"));
}

PYBIND11_MODULE(idcodes_rsid, m) {
  m.doc() = "Pybind11 bindings for RSID class";  // Optional module docstring

  try {
    py::module_::import("idcodes.idcodes_gf");
  } catch (const py::error_already_set& e) {
    throw std::runtime_error("Failed to import 'idcodes.idcodes_gf': " + std::string(e.what()));
  }

  // Bind RSID for different template types
  bind_rsid<uint8_t>(m, "RSID_U8");
  bind_rsid<uint16_t>(m, "RSID_U16");
  bind_rsid<uint32_t>(m, "RSID_U32");
  bind_rsid<uint64_t>(m, "RSID_U64");
}
