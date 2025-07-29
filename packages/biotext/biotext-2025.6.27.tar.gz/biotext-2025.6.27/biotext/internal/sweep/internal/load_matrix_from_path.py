"""
NON-COMMERCIAL LICENSE

Copyright (C) 2025 Diogo de Jesus Soares Machado, Roberto Tadeu Raittz

This file is part of Biotext Python Package.

Biotext Python Package and its associated documentation files are available
for anyone to use, copy, modify, and share, only for non-commercial purposes,
under the following conditions:

1. This copyright notice and this license appear in all copies or substantial
   parts of the Software.
2. All use of the Software gives proper credit to the original authors.
3. No one uses the Software in any commercial context. This includes, but is
   not limited to, using it in paid products, services, platforms, or tools
   that generate profit or other commercial benefit, without written
   permission from the authors.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED. THE AUTHORS TAKES NO RESPONSIBILITY FOR ANY DAMAGE THAT COMES FROM
USING OR NOT BEING ABLE TO USE THE SOFTWARE.
"""

import numpy as np
import h5py
import pickle
from scipy.io import loadmat

def load_matrix_from_path(path):
    """
    Loads a matrix from a file. Tries .txt, .npy, .h5, .mat, and .pickle formats in sequence.
    
    Parameters:
        path (str): Path to the file.
    
    Returns:
        np.ndarray: A numpy array loaded from the file.
    
    Raises:
        ValueError: If no valid method succeeds in loading the file.
    """
    errors = []
    
    # Try loading as .txt
    try:
        return np.loadtxt(path, encoding='utf-8')
    except FileNotFoundError as e:
        raise FileNotFoundError(e)
    except Exception as e:
        errors.append(f"TXT load error: {e}")
    
    # Try loading as .npy
    try:
        return np.load(path, allow_pickle=True)
    except Exception as e:
        errors.append(f"NPY load error: {e}")
    
    # Try loading as .h5
    try:
        with h5py.File(path, 'r') as file:
            first_key = list(file.keys())[0]
            return file[first_key][:]
    except Exception as e:
        errors.append(f"HDF5 load error: {e}")
    
    # Try loading as .mat
    try:
        # Attempt HDF5-based .mat format
        with h5py.File(path, 'r') as file:
            first_key = list(file.keys())[0]
            return file[first_key][:]
    except OSError:
        try:
            # Fallback to older .mat format
            mat_data = loadmat(path)
            keys = [key for key in mat_data.keys() if not key.startswith("__")]
            if len(keys) != 1:
                raise ValueError("The .mat file contains multiple datasets.")
            return mat_data[keys[0]]
        except Exception as e:
            errors.append(f"MAT load error: {e}")
    
    # Try loading as .pickle
    try:
        with open(path, 'rb') as file:
            return pickle.load(file)
    except Exception as e:
        errors.append(f"Pickle load error: {e}")
    
    # If all methods fail, raise a ValueError with detailed error messages
    raise ValueError(f"Failed to load matrix from {path}. Errors:\n" + "\n".join(errors))