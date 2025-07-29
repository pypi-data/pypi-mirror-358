#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "idcodes.h"

namespace py = pybind11;

// Helper function to bind the IDCODES template for a given type
template <typename T>
void bind_idcodes(py::module& m, const std::string& class_name) {
  py::class_<IDCODES<T>>(m, class_name.c_str())
      .def(py::init<>())
      // Galois Field generation
      .def("generate_gf_outer", &IDCODES<T>::generate_gf_outer)
      .def("get_exp_arr", &IDCODES<T>::get_exp_arr)
      .def("get_log_arr", &IDCODES<T>::get_log_arr)
      .def("get_exp_arr_in", &IDCODES<T>::get_exp_arr_in)
      .def("get_log_arr_in", &IDCODES<T>::get_log_arr_in)
      .def("generate_gf_inner", &IDCODES<T>::generate_gf_inner)
      .def("save_outer_table", &IDCODES<T>::save_outer_table)

      .def("save_inner_table", &IDCODES<T>::save_inner_table)

      .def(
          "rsid",
          [](IDCODES<T>& self, const std::vector<T>& message, T tag_pos, py::array_t<T> exp_arr,
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
          [](IDCODES<T>& self, const std::vector<T>& message, T tag_pos, py::array_t<T> exp_arr,
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
      .def("rsid_upto_gf2x64", &IDCODES<T>::rsid_upto_gf2x64,
           "Perform RSID encoding for GF sizes up to 2^64", py::arg("message"), py::arg("tag_pos"),
           py::arg("gf_exp"))

      .def(
          "rs2id",
          [](IDCODES<T>& self, const std::vector<T>& message, T tag_pos, T tag_pos_in,
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
          py::arg("gf_exp"))

      .def(
          "rmid",
          [](IDCODES<T>& self, const std::vector<T>& message, T tag_pos, T rm_order,
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

      .def(
          "gf_mul",
          [](IDCODES<T>& self, T a, T b, py::array_t<T> exp_arr, py::array_t<T> log_arr,
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
          [](IDCODES<T>& self, py::array_t<T> exp_arr, py::array_t<T> log_arr, uint16_t gf_exp) {
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
      .def("carryless_mul_fast", &IDCODES<T>::carryless_mul_fast,
           "Perform carryless multiplication", py::arg("a"), py::arg("b"), py::arg("gf_exp"))

      // SHA hash-based IDs
      .def("sha1id", &IDCODES<T>::sha1id)
      .def("sha256id", &IDCODES<T>::sha256id)

      .def("generate_string_sequence", &IDCODES<T>::generate_string_sequence)
      .def("read_inputfile_sequence", &IDCODES<T>::read_inputfile_sequence)
      .def("string_to_numeric", &IDCODES<T>::string_to_numeric)
      .def("generate_message_vector", &IDCODES<T>::generate_message_vector)
      .def("generate_random_tag_pos", &IDCODES<T>::generate_random_tag_pos)
      .def("create_file", &IDCODES<T>::create_file)
      .def("read_file", &IDCODES<T>::read_file);
}

PYBIND11_MODULE(idcodes, m) {
  m.doc() = "Pybind11 bindings for IDCODES";  // Optional module docstring
  bind_idcodes<uint8_t>(m, "IDCODES_U8");
  bind_idcodes<uint16_t>(m, "IDCODES_U16");
  bind_idcodes<uint32_t>(m, "IDCODES_U32");
  bind_idcodes<uint64_t>(m, "IDCODES_U64");
}
