#include "encoder/gf/gf.h"
#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

template <typename T>
void bind_gf(py::module& m, const std::string& class_name) {
  py::class_<GF<T>>(m, class_name.c_str())
      .def(py::init<>())  // Default constructor

      .def("get_exp_arr", &GF<T>::get_exp_arr)
      .def("get_log_arr", &GF<T>::get_log_arr)
      .def("get_exp_arr_in", &GF<T>::get_exp_arr_in)
      .def("get_log_arr_in", &GF<T>::get_log_arr_in)

      // Bind generate_gf_outer
      .def("generate_gf_outer", &GF<T>::generate_gf_outer, "Generate outer GF table",
           py::arg("gf_exp"))

      // Bind generate_gf_inner
      .def("generate_gf_inner", &GF<T>::generate_gf_inner, "Generate inner GF table",
           py::arg("gf_exp"))

      // Bind save_outer_table
      .def("save_outer_table", &GF<T>::save_outer_table, "Save outer GF table to file",
           py::arg("gf_size"))

      // Bind save_inner_table
      .def("save_inner_table", &GF<T>::save_inner_table, "Save inner GF table to file",
           py::arg("gf_size"))

      // Bind bit_shift_mul
      .def("bit_shift_mul", &GF<T>::bit_shift_mul, "Perform bit-shift multiplication", py::arg("a"),
           py::arg("b"), py::arg("field_gen_poly"), py::arg("msb_mask"))

      // Bind gf_mul with numpy array support
      .def(
          "gf_mul",
          [](GF<T>& self, T a, T b, py::array_t<T> exp_arr, py::array_t<T> log_arr,
             uint32_t gf_size) {
            // Convert numpy arrays to raw pointers
            py::buffer_info exp_info = exp_arr.request();
            py::buffer_info log_info = log_arr.request();

            if (exp_info.ndim != 1 || log_info.ndim != 1) {
              throw std::runtime_error("exp_arr and log_arr must be 1-dimensional arrays");
            }

            T* exp_ptr = static_cast<T*>(exp_info.ptr);
            T* log_ptr = static_cast<T*>(log_info.ptr);

            return self.gf_mul(a, b, exp_ptr, log_ptr, gf_size);
          },
          "Perform GF multiplication", py::arg("a"), py::arg("b"), py::arg("exp_arr"),
          py::arg("log_arr"), py::arg("gf_size"))

      // Bind initialize_gf with numpy array support
      .def(
          "initialize_gf",
          [](GF<T>& self, py::array_t<T> exp_arr, py::array_t<T> log_arr, uint16_t gf_exp) {
            // Convert numpy arrays to raw pointers
            py::buffer_info exp_info = exp_arr.request();
            py::buffer_info log_info = log_arr.request();

            if (exp_info.ndim != 1 || log_info.ndim != 1) {
              throw std::runtime_error("exp_arr and log_arr must be 1-dimensional arrays");
            }

            T* exp_ptr = static_cast<T*>(exp_info.ptr);
            T* log_ptr = static_cast<T*>(log_info.ptr);

            self.initialize_gf(exp_ptr, log_ptr, gf_exp);
          },
          "Initialize GF tables", py::arg("exp_arr"), py::arg("log_arr"), py::arg("gf_exp"))

      // Bind carryless_mul_fast
      .def("carryless_mul_fast", &GF<T>::carryless_mul_fast, "Perform carryless multiplication",
           py::arg("a"), py::arg("b"), py::arg("gf_exp"));
}

PYBIND11_MODULE(idcodes_gf, m) {
  m.doc() = "Pybind11 bindings for GF class";  // Optional module docstring

  // Bind GF for different template types
  bind_gf<uint8_t>(m, "GF_U8");
  bind_gf<uint16_t>(m, "GF_U16");
  bind_gf<uint32_t>(m, "GF_U32");
  bind_gf<uint64_t>(m, "GF_U64");
}
