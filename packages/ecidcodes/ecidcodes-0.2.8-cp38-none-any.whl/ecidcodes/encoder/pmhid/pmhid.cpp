#include "encoder/pmhid/pmhid.h"
#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <stdexcept>

namespace py = pybind11;

template <typename T>
void bind_pmhid(py::module& m, const std::string& message) {
  py::class_<PMHID<T>>(m, message.c_str())
      .def(py::init<>(), R"pbdoc(
          Default constructor for PMHID class.
      )pbdoc")
      .def(
          "pmhid",
          [](PMHID<T>& self, py::array_t<T, py::array::c_style | py::array::forcecast> arr) {
            py::buffer_info info = arr.request();
            if (info.ndim != 1)
              throw std::invalid_argument("Input message must be a 1-dimensional array");
            if (info.size == 0)
              throw std::invalid_argument("Input message array must not be empty");
            auto ptr = static_cast<T*>(info.ptr);
            std::vector<T> message(ptr, ptr + info.shape[0]);
            return self.pmhid(message);
          },
          R"pbdoc(
              Compute PMHID for a message.

              Args:
                  message (numpy.ndarray): 1D array of message symbols (not empty).

              Returns:
                  int: PMHID value.

              Raises:
                  ValueError: If message is not 1-dimensional or is empty.
          )pbdoc",
          py::arg("message"));
}

PYBIND11_MODULE(idcodes_pmhid, m) {
  m.doc() = "Pybind11 bindings for PMHID class";
  bind_pmhid<uint8_t>(m, "PMHID_U8");
  bind_pmhid<uint16_t>(m, "PMHID_U16");
  bind_pmhid<uint32_t>(m, "PMHID_U32");
  bind_pmhid<uint64_t>(m, "PMHID_U64");
}
