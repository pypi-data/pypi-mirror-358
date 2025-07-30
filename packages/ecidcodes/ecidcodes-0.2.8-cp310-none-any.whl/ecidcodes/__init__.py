# -*- coding: utf-8 -*-
# This file is part of the ECIDCODES Python bindings.
# Package metadata
__version__ = "0.0.0"  # Default version, will be updated dynamically
__author__ = "EcoLogic Computing GmbH"
__email__ = "info@ecologic-computing.com"
__description__ = "Python bindings for ECIDCODES Library"

# Dynamically load the version from the VERSION file
import os

version_file = os.path.join(os.path.dirname(__file__), "version")
try:
    with open(version_file, "r") as vf:
        version_info = {}
        for line in vf:
            key, value = line.strip().split()
            version_info[key] = value
        __version__ = f"{version_info['PROJECT_VERSION_MAJOR']}.{version_info['PROJECT_VERSION_MINOR']}.{version_info['PROJECT_VERSION_PATCH']}"
except FileNotFoundError:
    __version__ = "unknown"  # Fallback if the version file is missing
except Exception as e:
    raise RuntimeError(f"Error reading version from {version_file}: {e}")
