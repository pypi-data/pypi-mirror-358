#include "encoder/gf/gf.h"
#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <cstdint>
#include <stdexcept>

namespace py = pybind11;

template <typename T>
void bind_gf(py::module& m, const std::string& class_name) {
  py::class_<GF<T>>(m, class_name.c_str())
      .def(py::init<>(), R"pbdoc(
          Default constructor for GF class.
      )pbdoc")

      .def("get_exp_arr", &GF<T>::get_exp_arr, R"pbdoc(
          Get the exponential lookup table for the outer Galois Field.

          Returns:
              list: Exponential lookup table as a Python list.
      )pbdoc")
      .def("get_log_arr", &GF<T>::get_log_arr, R"pbdoc(
          Get the logarithmic lookup table for the outer Galois Field.

          Returns:
              list: Logarithmic lookup table as a Python list.
      )pbdoc")
      .def("get_exp_arr_in", &GF<T>::get_exp_arr_in, R"pbdoc(
          Get the exponential lookup table for the inner Galois Field.

          Returns:
              list: Exponential lookup table for inner GF as a Python list.
      )pbdoc")
      .def("get_log_arr_in", &GF<T>::get_log_arr_in, R"pbdoc(
          Get the logarithmic lookup table for the inner Galois Field.

          Returns:
              list: Logarithmic lookup table for inner GF as a Python list.
      )pbdoc")

      .def(
          "generate_gf_outer",
          [](GF<T>& self, uint16_t gf_exp) {
            if (gf_exp < 1 || gf_exp > 64)
              throw std::invalid_argument("gf_exp must be in [1, 64]");
            self.generate_gf_outer(gf_exp);
          },
          R"pbdoc(
               Generate lookup tables for the outer Galois Field.

               Args:
                   gf_exp (int): Exponent for GF(2^n), must be in [1, 64].

               Raises:
                   ValueError: If gf_exp is out of range.
           )pbdoc",
          py::arg("gf_exp"))

      .def(
          "generate_gf_inner",
          [](GF<T>& self, uint16_t gf_exp) {
            if (gf_exp < 2 || gf_exp > 64 || gf_exp % 2 != 0)
              throw std::invalid_argument("gf_exp for inner GF must be even and in [2, 64]");
            self.generate_gf_inner(gf_exp);
          },
          R"pbdoc(
               Generate lookup tables for the inner Galois Field.

               Args:
                   gf_exp (int): Even exponent for GF(2^n), must be in [2, 64].

               Raises:
                   ValueError: If gf_exp is not even or out of range.
           )pbdoc",
          py::arg("gf_exp"))

      .def(
          "save_outer_table",
          [](GF<T>& self, int gf_size) {
            if (gf_size <= 0)
              throw std::invalid_argument("gf_size must be positive");
            self.save_outer_table(gf_size);
          },
          R"pbdoc(
               Save the outer GF lookup tables to a file.

               Args:
                   gf_size (int): Size of the Galois Field, must be positive.

               Raises:
                   ValueError: If gf_size is not positive.
           )pbdoc",
          py::arg("gf_size"))

      .def(
          "save_inner_table",
          [](GF<T>& self, int gf_size) {
            if (gf_size <= 0)
              throw std::invalid_argument("gf_size must be positive");
            self.save_inner_table(gf_size);
          },
          R"pbdoc(
               Save the inner GF lookup tables to a file.

               Args:
                   gf_size (int): Size of the Galois Field, must be positive.

               Raises:
                   ValueError: If gf_size is not positive.
           )pbdoc",
          py::arg("gf_size"))

      .def(
          "bit_shift_mul",
          [](GF<T>& self, T a, T b, T field_gen_poly, T msb_mask) {
            // No special validation, but you can add checks if needed
            return self.bit_shift_mul(a, b, field_gen_poly, msb_mask);
          },
          R"pbdoc(
               Perform manual carryless multiplication using bit-shifts.

               Args:
                   a: First operand.
                   b: Second operand.
                   field_gen_poly: Field generator polynomial.
                   msb_mask: Most significant bit mask.

               Returns:
                   Result of the carryless multiplication.
           )pbdoc",
          py::arg("a"), py::arg("b"), py::arg("field_gen_poly"), py::arg("msb_mask"))

      .def(
          "gf_mul",
          [](GF<T>& self, T a, T b, py::array_t<T> exp_arr, py::array_t<T> log_arr,
             uint32_t gf_size) {
            py::buffer_info exp_info = exp_arr.request();
            py::buffer_info log_info = log_arr.request();

            if (exp_info.ndim != 1 || log_info.ndim != 1) {
              throw std::invalid_argument("exp_arr and log_arr must be 1-dimensional arrays");
            }
            if (exp_info.size < static_cast<ssize_t>(gf_size) ||
                log_info.size < static_cast<ssize_t>(gf_size)) {
              throw std::invalid_argument(
                  "exp_arr and log_arr must have at least gf_size elements");
            }

            T* exp_ptr = static_cast<T*>(exp_info.ptr);
            T* log_ptr = static_cast<T*>(log_info.ptr);

            return self.gf_mul(a, b, exp_ptr, log_ptr, gf_size);
          },
          R"pbdoc(
              Perform GF multiplication using provided lookup tables.

              Args:
                  a: First operand.
                  b: Second operand.
                  exp_arr: 1D numpy array for exponential lookup table (length >= gf_size).
                  log_arr: 1D numpy array for logarithmic lookup table (length >= gf_size).
                  gf_size: Size of the Galois Field.

              Returns:
                  Result of the multiplication in GF.

              Raises:
                  ValueError: If exp_arr or log_arr are not 1-dimensional or too small.
          )pbdoc",
          py::arg("a"), py::arg("b"), py::arg("exp_arr"), py::arg("log_arr"), py::arg("gf_size"))

      .def(
          "initialize_gf",
          [](GF<T>& self, py::array_t<T> exp_arr, py::array_t<T> log_arr, uint16_t gf_exp) {
            py::buffer_info exp_info = exp_arr.request();
            py::buffer_info log_info = log_arr.request();

            if (exp_info.ndim != 1 || log_info.ndim != 1) {
              throw std::invalid_argument("exp_arr and log_arr must be 1-dimensional arrays");
            }

            T* exp_ptr = static_cast<T*>(exp_info.ptr);
            T* log_ptr = static_cast<T*>(log_info.ptr);

            self.initialize_gf(exp_ptr, log_ptr, gf_exp);
          },
          R"pbdoc(
              Initialize GF lookup tables in-place.

              Args:
                  exp_arr: 1D numpy array for exponential lookup table.
                  log_arr: 1D numpy array for logarithmic lookup table.
                  gf_exp: Exponent for GF(2^n).

              Raises:
                  ValueError: If exp_arr or log_arr are not 1-dimensional.
          )pbdoc",
          py::arg("exp_arr"), py::arg("log_arr"), py::arg("gf_exp"))

      .def(
          "carryless_mul_fast",
          [](GF<T>& self, T a, T b, T gf_exp) {
            // No special validation, but you can add checks if needed
            return self.carryless_mul_fast(a, b, gf_exp);
          },
          R"pbdoc(
               Perform carryless multiplication using hardware instructions (if available).

               Args:
                   a: First operand.
                   b: Second operand.
                   gf_exp: Exponent for GF(2^n).

               Returns:
                   Result of the carryless multiplication.
           )pbdoc",
          py::arg("a"), py::arg("b"), py::arg("gf_exp"));
}

// Explicit template instantiations for all used types
//template class GF<uint8_t>;
//template class GF<uint16_t>;
//template class GF<uint32_t>;
//template class GF<uint64_t>;

// Static member definitions for all used types
// exp_arr
//template <>
//std::vector<uint8_t> GF<uint8_t>::exp_arr;
//template <>
//std::vector<uint16_t> GF<uint16_t>::exp_arr;
//template <>
//std::vector<uint32_t> GF<uint32_t>::exp_arr;
//template <>
//std::vector<uint64_t> GF<uint64_t>::exp_arr;
//// log_arr
//template <>
//std::vector<uint8_t> GF<uint8_t>::log_arr;
//template <>
//std::vector<uint16_t> GF<uint16_t>::log_arr;
//template <>
//std::vector<uint32_t> GF<uint32_t>::log_arr;
//template <>
//std::vector<uint64_t> GF<uint64_t>::log_arr;
//// exp_arr_in
//template <>
//std::vector<uint8_t> GF<uint8_t>::exp_arr_in;
//template <>
//std::vector<uint16_t> GF<uint16_t>::exp_arr_in;
//template <>
//std::vector<uint32_t> GF<uint32_t>::exp_arr_in;
//template <>
//std::vector<uint64_t> GF<uint64_t>::exp_arr_in;
//// log_arr_in
//template <>
//std::vector<uint8_t> GF<uint8_t>::log_arr_in;
//template <>
//std::vector<uint16_t> GF<uint16_t>::log_arr_in;
//template <>
//std::vector<uint32_t> GF<uint32_t>::log_arr_in;
//template <>
//std::vector<uint64_t> GF<uint64_t>::log_arr_in;

PYBIND11_MODULE(idcodes_gf, m) {
  m.doc() = "Pybind11 bindings for GF class";
  bind_gf<uint8_t>(m, "GF_U8");
  bind_gf<uint16_t>(m, "GF_U16");
  bind_gf<uint32_t>(m, "GF_U32");
  bind_gf<uint64_t>(m, "GF_U64");
}
