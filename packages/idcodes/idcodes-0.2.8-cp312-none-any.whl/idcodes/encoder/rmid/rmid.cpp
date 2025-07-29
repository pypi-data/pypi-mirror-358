#include "encoder/rmid/rmid.h"
#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

template <typename T>
void bind_rmid(py::module& m, const std::string& class_name) {
  py::class_<RMID<T>, GF<T>>(m, class_name.c_str())
      .def(py::init<>())  // Default constructor

      // Bind rmid function
      .def(
          "rmid",
          [](RMID<T>& self, const std::vector<T>& message, T tag_pos, T rm_order,
             py::array_t<T> exp_arr, py::array_t<T> log_arr, uint16_t gf_exp) {
            // Convert numpy arrays to raw pointers
            py::buffer_info exp_info = exp_arr.request();
            py::buffer_info log_info = log_arr.request();

            if (exp_info.ndim != 1 || log_info.ndim != 1) {
              throw std::runtime_error("exp_arr and log_arr must be 1-dimensional arrays");
            }

            T* exp_ptr = static_cast<T*>(exp_info.ptr);
            T* log_ptr = static_cast<T*>(log_info.ptr);

            return self.rmid(message, tag_pos, rm_order, exp_ptr, log_ptr, gf_exp);
          },
          "Evaluate Reed-Muller multivariable polynomial", py::arg("message"), py::arg("tag_pos"),
          py::arg("rm_order"), py::arg("exp_arr"), py::arg("log_arr"), py::arg("gf_exp"))

      // Bind generate_monomials function
      .def(
          "generate_monomials",
          [](RMID<T>& self, T rm_order, const std::vector<T>& eval_point_rm, T k_rm,
             py::array_t<T> exp_arr, py::array_t<T> log_arr, uint16_t gf_exp) {
            // Convert numpy arrays to raw pointers
            py::buffer_info exp_info = exp_arr.request();
            py::buffer_info log_info = log_arr.request();

            if (exp_info.ndim != 1 || log_info.ndim != 1) {
              throw std::runtime_error("exp_arr and log_arr must be 1-dimensional arrays");
            }

            T* exp_ptr = static_cast<T*>(exp_info.ptr);
            T* log_ptr = static_cast<T*>(log_info.ptr);

            return self.generate_monomials(rm_order, eval_point_rm, k_rm, exp_ptr, log_ptr, gf_exp);
          },
          "Generate monomials for Reed-Muller encoding", py::arg("rm_order"),
          py::arg("eval_point_rm"), py::arg("k_rm"), py::arg("exp_arr"), py::arg("log_arr"),
          py::arg("gf_exp"));
}

PYBIND11_MODULE(idcodes_rmid, m) {
  m.doc() = "Pybind11 bindings for RMID class";  // Optional module docstring

  try {
    py::module_::import("idcodes.idcodes_gf");
  } catch (const py::error_already_set& e) {
    throw std::runtime_error("Failed to import 'idcodes.idcodes_gf': " + std::string(e.what()));
  }

  // Bind RMID for different template types
  bind_rmid<uint8_t>(m, "RMID_U8");
  bind_rmid<uint16_t>(m, "RMID_U16");
  bind_rmid<uint32_t>(m, "RMID_U32");
  bind_rmid<uint64_t>(m, "RMID_U64");
}
