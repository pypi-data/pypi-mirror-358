#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <stdexcept>
#include "idcodes.h"

namespace py = pybind11;

// Helper function to bind the IDCODES template for a given type
template <typename T>
void bind_idcodes(py::module& m, const std::string& class_name) {
  py::class_<IDCODES<T>>(m, class_name.c_str())
      .def(py::init<>())
      // Galois Field generation
      .def(py::init<>(), R"pbdoc(
          Default constructor for GF class.
      )pbdoc")

      .def("get_exp_arr", &IDCODES<T>::get_exp_arr, R"pbdoc(
          Get the exponential lookup table for the outer Galois Field.

          Returns:
              list: Exponential lookup table as a Python list.
      )pbdoc")
      .def("get_log_arr", &IDCODES<T>::get_log_arr, R"pbdoc(
          Get the logarithmic lookup table for the outer Galois Field.

          Returns:
              list: Logarithmic lookup table as a Python list.
      )pbdoc")
      .def("get_exp_arr_in", &IDCODES<T>::get_exp_arr_in, R"pbdoc(
          Get the exponential lookup table for the inner Galois Field.

          Returns:
              list: Exponential lookup table for inner GF as a Python list.
      )pbdoc")
      .def("get_log_arr_in", &IDCODES<T>::get_log_arr_in, R"pbdoc(
          Get the logarithmic lookup table for the inner Galois Field.

          Returns:
              list: Logarithmic lookup table for inner GF as a Python list.
      )pbdoc")

      .def(
          "generate_gf_outer",
          [](IDCODES<T>& self, uint16_t gf_exp) {
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
          [](IDCODES<T>& self, uint16_t gf_exp) {
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
          [](IDCODES<T>& self, int gf_size) {
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
          [](IDCODES<T>& self, int gf_size) {
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
          [](IDCODES<T>& self, T a, T b, T field_gen_poly, T msb_mask) {
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
          [](IDCODES<T>& self, T a, T b, py::array_t<T> exp_arr, py::array_t<T> log_arr,
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
          [](IDCODES<T>& self, py::array_t<T> exp_arr, py::array_t<T> log_arr, uint16_t gf_exp) {
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
          [](IDCODES<T>& self, T a, T b, T gf_exp) {
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
          py::arg("a"), py::arg("b"), py::arg("gf_exp"))

      .def(
          "rsid",
          [](IDCODES<T>& self, const std::vector<T>& message, T tag_pos, uint16_t gf_exp) {
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
          [](IDCODES<T>& self, const std::vector<T>& message, T tag_pos, uint32_t gf_size) {
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
          [](IDCODES<T>& self, const std::vector<T>& message, uint64_t tag_pos, uint16_t gf_exp) {
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
          py::arg("message"), py::arg("tag_pos"), py::arg("gf_exp"))

      .def(
          "rs2id",
          [](IDCODES<T>& self, const std::vector<T>& message, T tag_pos, T tag_pos_in,
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
          py::arg("message"), py::arg("tag_pos"), py::arg("tag_pos_in"), py::arg("gf_exp"))

      .def(
          "rmid",
          [](IDCODES<T>& self, const std::vector<T>& message, T tag_pos, T rm_order,
             uint16_t gf_exp) {
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

      // SHA hash-based IDs
      .def(
          "sha1id",
          [](IDCODES<T>& self, const std::vector<T>& data, uint16_t gf_exp) {
            if (data.empty())
              throw std::invalid_argument("Input data vector must not be empty");
            if (gf_exp < 1 || gf_exp > 64)
              throw std::invalid_argument("gf_exp must be in [1, 64]");
            return self.sha1id(data, gf_exp);
          },
          R"pbdoc(
               Compute SHA1ID for a message.

               Args:
                   data (list[int]): Input data vector (not empty).
                   gf_exp (int): Exponent for GF(2^n), must be in [1, 64].

               Returns:
                   int: SHA1ID value.

               Raises:
                   ValueError: If data is empty or gf_exp is out of range.
           )pbdoc",
          py::arg("data"), py::arg("gf_exp"))
      .def(
          "sha256id",
          [](IDCODES<T>& self, const std::vector<T>& data, uint16_t gf_exp) {
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
          py::arg("data"), py::arg("gf_exp"))
      .def(
          "pmhid",
          [](IDCODES<T>& self, py::array_t<T, py::array::c_style | py::array::forcecast> arr) {
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
          py::arg("message"))

      .def("generate_string_sequence", &IDCODES<T>::generate_string_sequence,
           R"pbdoc(
               Generates a random string of a particular data type.

               Args:
                   length (int): Length of the string.

               Returns:
                   list: Generated string as a list of type T.
           )pbdoc",
           py::arg("length"))

      .def("read_inputfile_sequence", &IDCODES<T>::read_inputfile_sequence,
           R"pbdoc(
               Reads the data from an input file.

               Args:
                   filename (str): Name of the file.
                   binary (bool): True if the file is binary, false otherwise.

               Returns:
                   list: Processed data as a message vector of type T.
           )pbdoc",
           py::arg("filename"), py::arg("binary"))

      .def("string_to_numeric", &IDCODES<T>::string_to_numeric,
           R"pbdoc(
               Converts a string to its numerical form.

               Args:
                   str (str): Input string.

               Returns:
                   list: Numerical representation of the string as a list of unsigned char.
           )pbdoc",
           py::arg("str"))

      .def("generate_message_vector", &IDCODES<T>::generate_message_vector,
           R"pbdoc(
               Generates a message vector.

               Args:
                   size_in_KB (int): Size of the message in KB.
                   gf_exp (int): Number of bits representing each element of the message vector.

               Returns:
                   list: Message vector of type T.
           )pbdoc",
           py::arg("size_in_KB"), py::arg("gf_exp"))

      .def("generate_random_tag_pos", &IDCODES<T>::generate_random_tag_pos,
           R"pbdoc(
               Generates a random tag position.

               Args:
                   tags_size (int): Minimum value of the tag position.

               Returns:
                   int: Random tag position of type T.
           )pbdoc",
           py::arg("tags_size"))

      .def("create_file", &IDCODES<T>::create_file,
           R"pbdoc(
               Creates a file with random data.

               Args:
                   filepath (str): Path to the file.
                   size_in_B (int): Size of the file in Bytes.
                   gf_exp (int): Number of bits representing each element of the message vector.
           )pbdoc",
           py::arg("filepath"), py::arg("size_in_B"), py::arg("gf_exp"))

      .def("read_file", &IDCODES<T>::read_file,
           R"pbdoc(
               Reads data from a file and stores it in a vector.

               Args:
                   filepath (str): Path to the file.
                   gf_exp (int): Number of bits representing each element of the message vector.

               Returns:
                   list: Processed data as a message vector of type T.
           )pbdoc",
           py::arg("filepath"), py::arg("gf_exp"))

      .def("generate_string", &IDCODES<T>::generate_string,
           R"pbdoc(
               Generates a random string of a particular length.

               Args:
                   length (int): Length of the string.

               Returns:
                   str: Generated string.
           )pbdoc",
           py::arg("length"));
}
PYBIND11_MODULE(idcodes, m) {
  m.doc() = "Pybind11 bindings for IDCODES";  // Optional module docstring
  bind_idcodes<uint8_t>(m, "IDCODES_U8");
  bind_idcodes<uint16_t>(m, "IDCODES_U16");
  bind_idcodes<uint32_t>(m, "IDCODES_U32");
  bind_idcodes<uint64_t>(m, "IDCODES_U64");
}
