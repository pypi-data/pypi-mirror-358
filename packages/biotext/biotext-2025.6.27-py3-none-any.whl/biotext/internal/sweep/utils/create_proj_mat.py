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
from .orthrand import orthrand

def create_proj_mat(rows, cols):
    """
    Generate a pseudo-random projection matrix designed for use in the SWeeP
    method.

    Parameters:
        rows (int): Number of rows in the projection matrix.
        cols (int): Number of columns in the projection matrix.

    Returns:
        np.ndarray: The computed pseudo-random projection matrix R.
    """
    Um = np.sin(range(1, cols + 1))
    Un = np.sin(range(1, rows + 1))
    xnorm = np.sqrt(rows / 3)
    idx = list(range(0, rows))
    R = (1 / xnorm) * orthrand(idx, Um, Un)
    return R