#include "encoder/sha256id/sha256id.h"
#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <stdexcept>
namespace py = pybind11;

template <typename T>
void bind_sha256id(py::module& m, const std::string& class_name) {
  py::class_<SHA256ID<T>>(m, class_name.c_str())
      .def(py::init<>(), R"pbdoc(
          Default constructor for SHA256ID class.
      )pbdoc")
      .def(
          "sha256id",
          [](SHA256ID<T>& self, const std::vector<T>& data, uint16_t gf_exp) {
            if (data.empty())
              throw std::invalid_argument("Input data vector must not be empty");
            if (gf_exp < 1 || gf_exp > 64)
              throw std::invalid_argument("gf_exp must be in [1, 64]");
            return self.sha256id(data, gf_exp);
          },
          R"pbdoc(
               Compute SHA256ID for a message.

               Args:
                   data (list[int]): Input data vector (not empty).
                   gf_exp (int): Exponent for GF(2^n), must be in [1, 64].

               Returns:
                   int: SHA256ID value.

               Raises:
                   ValueError: If data is empty or gf_exp is out of range.
           )pbdoc",
          py::arg("data"), py::arg("gf_exp"));
}

PYBIND11_MODULE(idcodes_sha256id, m) {
  m.doc() = "Pybind11 bindings for SHA256ID class";
  bind_sha256id<uint8_t>(m, "SHA256ID_U8");
  bind_sha256id<uint16_t>(m, "SHA256ID_U16");
  bind_sha256id<uint32_t>(m, "SHA256ID_U32");
  bind_sha256id<uint64_t>(m, "SHA256ID_U64");
}
