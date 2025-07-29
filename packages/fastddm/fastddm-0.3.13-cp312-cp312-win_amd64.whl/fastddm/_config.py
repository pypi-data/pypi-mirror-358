# Copyright (c) 2023-2023 University of Vienna, Enrico Lattuada, Fabian Krautgasser, and Roberto Cerbino.
# Part of FastDDM, released under the GNU GPL-3.0 License.
# Author: Enrico Lattuada
# Maintainer: Enrico Lattuada

"""The collection of CMake compile flags."""

import numpy as np

IS_CPP_ENABLED = True              # configured by CMake
IS_CUDA_ENABLED = False            # configured by CMake
IS_SINGLE_PRECISION = False    # configured by CMake

CUDA_VERSION = ""         # configured by CMake

DTYPE = np.float32 if IS_SINGLE_PRECISION else np.float64
