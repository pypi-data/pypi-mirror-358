#include "encoder/rsid/rsid.h"
#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <stdexcept>

namespace py = pybind11;

template <typename T>
void bind_rsid(py::module& m, const std::string& class_name) {
  py::class_<RSID<T>, GF<T>>(m, class_name.c_str())
      .def(py::init<>(), R"pbdoc(
          Default constructor for RSID class.
      )pbdoc")
      .def(
          "rsid",
          [](RSID<T>& self, const std::vector<T>& message, T tag_pos, uint16_t gf_exp) {
            if (message.empty())
              throw std::invalid_argument("Input message vector must not be empty");
            if (gf_exp < 1 || gf_exp > 64)
              throw std::invalid_argument("gf_exp must be in [1, 64]");
            return self.rsid(message, tag_pos, gf_exp);
          },
          R"pbdoc(
               Perform RSID encoding. Uses LUTs for GF(2^n) with n<=16, and carryless multiplication for n>16.

               Args:
                   message (list[int]): Input message vector (not empty).
                   tag_pos (int): Tag position.
                   gf_exp (int): Exponent for GF(2^n), must be in [1, 64].

               Returns:
                   int: RSID tag value.

               Raises:
                   ValueError: If message is empty or gf_exp is out of range.
           )pbdoc",
          py::arg("message"), py::arg("tag_pos"), py::arg("gf_exp"))
      .def(
          "rsid_upto_gf2x16",
          [](RSID<T>& self, const std::vector<T>& message, T tag_pos, uint32_t gf_size) {
            if (message.empty())
              throw std::invalid_argument("Input message vector must not be empty");
            if (gf_size < 2 || gf_size > (1ULL << 16))
              throw std::invalid_argument("gf_size must be in [2, 65536]");
            // Use instance lookup tables via public instance getter methods
            const T* exp_ptr = self.get_exp_arr().data();
            const T* log_ptr = self.get_log_arr().data();
            return self.rsid_upto_gf2x16(message, tag_pos, exp_ptr, log_ptr, gf_size);
          },
          R"pbdoc(
               Evaluate RSID tag for GF sizes <= 2^16 using internal LUTs.

               Args:
                   message (list[int]): Input message vector (not empty).
                   tag_pos (int): Tag position.
                   gf_size (int): Size of the Galois Field, must be in [2, 65536].

               Returns:
                   int: RSID tag value.

               Raises:
                   ValueError: If message is empty or gf_size is out of range.
           )pbdoc",
          py::arg("message"), py::arg("tag_pos"), py::arg("gf_size"))
      .def(
          "rsid_upto_gf2x64",
          [](RSID<T>& self, const std::vector<T>& message, uint64_t tag_pos, uint16_t gf_exp) {
            if (message.empty())
              throw std::invalid_argument("Input message vector must not be empty");
            if (gf_exp < 17 || gf_exp > 64)
              throw std::invalid_argument("gf_exp must be in [17, 64]");
            return self.rsid_upto_gf2x64(message, tag_pos, gf_exp);
          },
          R"pbdoc(
               Perform RSID encoding for GF sizes up to 2^64 using carryless multiplication.

               Args:
                   message (list[int]): Input message vector (not empty).
                   tag_pos (int): Tag position.
                   gf_exp (int): Exponent for GF(2^n), must be in [17, 64].

               Returns:
                   int: RSID tag value.

               Raises:
                   ValueError: If message is empty or gf_exp is out of range.
           )pbdoc",
          py::arg("message"), py::arg("tag_pos"), py::arg("gf_exp"));
}

PYBIND11_MODULE(idcodes_rsid, m) {
  m.doc() = "Pybind11 bindings for RSID class";
  try {
    py::module_::import("ecidcodes.idcodes_gf");
  } catch (const py::error_already_set& e) {
    throw std::runtime_error("Failed to import 'ecidcodes.idcodes_gf': " + std::string(e.what()));
  }
  bind_rsid<uint8_t>(m, "RSID_U8");
  bind_rsid<uint16_t>(m, "RSID_U16");
  bind_rsid<uint32_t>(m, "RSID_U32");
  bind_rsid<uint64_t>(m, "RSID_U64");
}
