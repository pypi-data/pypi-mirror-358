#include "encoder/rs2id/rs2id.h"
#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

template <typename T>
void bind_rs2id(py::module& m, const std::string& class_name) {
  py::class_<RS2ID<T>, RSID<T>>(m, class_name.c_str())
      .def(py::init<>())  // Default constructor

      // Bind rs2id function
      .def(
          "rs2id",
          [](RS2ID<T>& self, const std::vector<T>& message, T tag_pos, T tag_pos_in,
             py::array_t<T> exp_arr, py::array_t<T> log_arr, py::array_t<T> exp_arr_in,
             py::array_t<T> log_arr_in, uint16_t gf_exp) {
            // Convert numpy arrays to raw pointers
            py::buffer_info exp_info = exp_arr.request();
            py::buffer_info log_info = log_arr.request();
            py::buffer_info exp_in_info = exp_arr_in.request();
            py::buffer_info log_in_info = log_arr_in.request();

            if (exp_info.ndim != 1 || log_info.ndim != 1 || exp_in_info.ndim != 1 ||
                log_in_info.ndim != 1) {
              throw std::runtime_error(
                  "exp_arr, log_arr, exp_arr_in, and log_arr_in must be 1-dimensional arrays");
            }

            T* exp_ptr = static_cast<T*>(exp_info.ptr);
            T* log_ptr = static_cast<T*>(log_info.ptr);
            T* exp_in_ptr = static_cast<T*>(exp_in_info.ptr);
            T* log_in_ptr = static_cast<T*>(log_in_info.ptr);

            return self.rs2id(message, tag_pos, tag_pos_in, exp_ptr, log_ptr, exp_in_ptr,
                              log_in_ptr, gf_exp);
          },
          "Perform RS2ID encoding", py::arg("message"), py::arg("tag_pos"), py::arg("tag_pos_in"),
          py::arg("exp_arr"), py::arg("log_arr"), py::arg("exp_arr_in"), py::arg("log_arr_in"),
          py::arg("gf_exp"));
}

PYBIND11_MODULE(idcodes_rs2id, m) {
  m.doc() = "Pybind11 bindings for RS2ID class";  // Optional module docstring

  try {
    py::module_::import("idcodes.idcodes_gf");
  } catch (const py::error_already_set& e) {
    throw std::runtime_error("Failed to import 'idcodes.idcodes_gf': " + std::string(e.what()));
  }

  // Bind RS2ID for different template types
  bind_rs2id<uint8_t>(m, "RS2ID_U8");
  bind_rs2id<uint16_t>(m, "RS2ID_U16");
  bind_rs2id<uint32_t>(m, "RS2ID_U32");
  bind_rs2id<uint64_t>(m, "RS2ID_U64");
}
