#include "encoder/rs2id/rs2id.h"
#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <stdexcept>

namespace py = pybind11;

template <typename T>
void bind_rs2id(py::module& m, const std::string& class_name) {
  // Bind RSID<T> base class first if not already bound
  py::class_<RS2ID<T>, RSID<T>>(m, class_name.c_str())
      .def(py::init<>(), R"pbdoc(
          Default constructor for RS2ID class.
      )pbdoc")
      .def(
          "rs2id",
          [](RS2ID<T>& self, const std::vector<T>& message, T tag_pos, T tag_pos_in,
             uint16_t gf_exp) {
            if (message.empty())
              throw std::invalid_argument("Input message vector must not be empty");
            if (gf_exp < 2 || gf_exp > 64 || gf_exp % 2 != 0)
              throw std::invalid_argument("gf_exp for RS2ID must be even and in [2, 64]");
            return self.rs2id(message, tag_pos, tag_pos_in, gf_exp);
          },
          R"pbdoc(
               Perform RS2ID encoding using internal GF tables.

               Args:
                   message (list[int]): Input message vector (not empty).
                   tag_pos (int): Tag position.
                   tag_pos_in (int): Inner tag position.
                   gf_exp (int): Even exponent for GF(2^n), must be in [2, 64].

               Returns:
                   int: RS2ID tag value.

               Raises:
                   ValueError: If message is empty or gf_exp is not even or out of range.
           )pbdoc",
          py::arg("message"), py::arg("tag_pos"), py::arg("tag_pos_in"), py::arg("gf_exp"));
}

PYBIND11_MODULE(idcodes_rs2id, m) {
  m.doc() = "Pybind11 bindings for RS2ID class";  // Optional module docstring

  try {
    py::module_::import("ecidcodes.idcodes_gf");
    py::module_::import("ecidcodes.idcodes_rsid");
  } catch (const py::error_already_set& e) {
    throw std::runtime_error("Failed to import 'ecidcodes.idcodes_gf': " + std::string(e.what()));
  }

  // Bind RS2ID for different template types
  bind_rs2id<uint8_t>(m, "RS2ID_U8");
  bind_rs2id<uint16_t>(m, "RS2ID_U16");
  bind_rs2id<uint32_t>(m, "RS2ID_U32");
  bind_rs2id<uint64_t>(m, "RS2ID_U64");
}
