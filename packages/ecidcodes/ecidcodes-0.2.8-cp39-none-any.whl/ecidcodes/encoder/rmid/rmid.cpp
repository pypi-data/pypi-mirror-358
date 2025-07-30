#include "encoder/rmid/rmid.h"
#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <stdexcept>

namespace py = pybind11;

template <typename T>
void bind_rmid(py::module& m, const std::string& class_name) {
  py::class_<RMID<T>, GF<T>>(m, class_name.c_str())
      .def(py::init<>(), R"pbdoc(
          Default constructor for RMID class.
      )pbdoc")
      .def(
          "rmid",
          [](RMID<T>& self, const std::vector<T>& message, T tag_pos, T rm_order, uint16_t gf_exp) {
            if (message.empty())
              throw std::invalid_argument("Input message vector must not be empty");
            if (gf_exp < 1 || gf_exp > 64)
              throw std::invalid_argument("gf_exp must be in [1, 64]");
            return self.rmid(message, tag_pos, rm_order, gf_exp);
          },
          R"pbdoc(
               Evaluate RMID tag for a given message using GF LUTs.

               Args:
                   message (list[int]): Input message vector (not empty).
                   tag_pos (int): Tag position.
                   rm_order (int): Reed-Muller monomial order.
                   gf_exp (int): Exponent for GF(2^n), must be in [1, 64].

               Returns:
                   int: RMID tag value.

               Raises:
                   ValueError: If message is empty or gf_exp is out of range.
           )pbdoc",
          py::arg("message"), py::arg("tag_pos"), py::arg("rm_order"), py::arg("gf_exp"))
      .def(
          "generate_monomials",
          [](RMID<T>& self, T rm_order, const std::vector<T>& eval_point_rm, T k_rm,
             uint16_t gf_exp) {
            if (eval_point_rm.empty())
              throw std::invalid_argument("eval_point_rm must not be empty");
            if (gf_exp < 1 || gf_exp > 64)
              throw std::invalid_argument("gf_exp must be in [1, 64]");
            return self.generate_monomials(rm_order, eval_point_rm, k_rm, gf_exp);
          },
          R"pbdoc(
              Generate monomials for Reed-Muller encoding.

              Args:
                  rm_order (int): Reed-Muller monomial order.
                  eval_point_rm (list[int]): Evaluation points (not empty).
                  k_rm (int): Parameter k_rm.
                  gf_exp (int): Exponent for GF(2^n), must be in [1, 64].

              Returns:
                  list[int]: Generated monomials.

              Raises:
                  ValueError: If eval_point_rm is empty or gf_exp is out of range.
          )pbdoc",
          py::arg("rm_order"), py::arg("eval_point_rm"), py::arg("k_rm"), py::arg("gf_exp"));
}

PYBIND11_MODULE(idcodes_rmid, m) {
  m.doc() = "Pybind11 bindings for RMID class";
  try {
    py::module_::import("ecidcodes.idcodes_gf");
  } catch (const py::error_already_set& e) {
    throw std::runtime_error("Failed to import 'ecidcodes.idcodes_gf': " + std::string(e.what()));
  }
  bind_rmid<uint8_t>(m, "RMID_U8");
  bind_rmid<uint16_t>(m, "RMID_U16");
  bind_rmid<uint32_t>(m, "RMID_U32");
  bind_rmid<uint64_t>(m, "RMID_U64");
}
