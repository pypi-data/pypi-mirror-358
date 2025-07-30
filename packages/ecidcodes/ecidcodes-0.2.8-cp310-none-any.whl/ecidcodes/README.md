# ECIDCODES Library

## Overview

**`ECIDCODES`** is a C++ library designed to provide tools for Binary Galois (Finite) Field `GF` and
 includes functionality for polynomial evaluation `RSID` and `RS2ID`, hashing `SHA1ID` and `SHA256ID`, Reed-Muller `RMID` and Polymur hash `PMHID`,
 and collision testing modules. The library is designed for use in high-performance computational environments and
 supports modular, extensible templates.

## Features

- **Galois Field Operations:** Initialization, multiplication, and evaluation of polynomials over finite fields `GF 2^n = 1 to 64`.
- **Reed Solomon Codes:** Evaluate Reed-Solomon `RSID` and Concatenated Reed-Solomon `RS2ID` Tagging codes
- **Hashing Algorithms:** Implements `SHA-1` and `SHA-256` for secure message hashing.
- **Reed-Muller Codes:** `RMID` Evaluate multivariable polynomials for error correction.
- **Polymur hash:** `PMHID` encodes a message using the Polymur hash function.
- **Collision Testing:** Measure collision probabilities in tag values for large-scale simulations.
- **Speed Benchmarks:** Measure execution speed for various parameters with CLI input and save to CSV Results.

## 1. Installation

- **Create a Virtual Environment**  
    It is recommended to use a virtual environment to isolate the dependencies for the project. Run the following command to create a virtual environment:

    ```
         sudo apt install python3-venv
         python3.12 -m venv .venv
         python -m pip install --upgrade pip
    ```
- **Activate the Virtual Environment**  
    Activate the virtual environment using the following command:

    ```
         source .venv/bin/activate
         python -m pip install --upgrade pip
    ```
- **Install the Package**  
    Once the virtual environment is activated, install the `ecidcodes` `*.whl` using the provided wheel file:

    ```
         pip install ecidcodes
    ```
- **Verify the Installation**  
    After installation, you can verify that the package is installed correctly by running:

    ```
         python -c "import ecidcodes; print(dir(ecidcodes))"
    ```
    If the package is installed correctly, you should see the message:  
    `ecidcodes installed successfully!`


### 2. Test the Module

```bash
python
>>> import ecidcodes
>>> print(dir(ecidcodes))
```

### 3. Uninstall .whl Package 

Run the following commands to uninstall the project:

```bash
pip uninstall ecidcodes
```

### 4. Verify `.so` file and copy to python environment
Copy the .so file to your virtual environment's site-packages directory:

```bash
       
       # Uninstall old version of idcodeslibrary if exists
       sudo apt remove idcodeslibrary

        ```bash

       # Download the `*.deb` package and install it using `dpkg`
       sudo dpkg -i idcodeslibrary_*.deb
       # If you encounter any dependency issues, you can resolve them by running:
       sudo apt-get install -f
       
        # Verify by searching for installed packages
        dpkg -l | grep -i ecidcodes


       # Modify or update idcodeslibrary.conf file to add `/usr/local/lib` to path
       sudo sh -c 'echo "/usr/local/lib" >> /etc/ld.so.conf.d/idcodeslibrary.conf'
       # verify the contents of the file
       cat /etc/ld.so.conf.d/idcodeslibrary.conf

       # Configure
       sudo ldconfig

       # Verify if *.so files for ecidcodes library are in path
       ldconfig -p | grep -i ecidcodes

```
## Notes

- Ensure that all dependencies are installed before building the project.
- Use a virtual environment to avoid conflicts with system-wide packages.
- Refer to the official Pybind11 and CMake documentation for advanced configuration options.


```bash
    pip install myst-parser
```

for latex pdf
```bash
    sudo apt install texlive-full 
```

