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

def lambert_w(branch, x, dtype=np.float64):
    """
    Lambert W function: Functional inverse of x = w * exp(w).
    
    Parameters:
        - branch (int): Branch to compute (-1 for lower branch, 0 for upper
          branch).
        - x (array-like): Input value(s).

    Returns:
        - numpy.ndarray: Computed Lambert W values for the given input.
    """
    # Convert x to a numpy array for vectorized operations
    x = np.asarray(x, dtype=np.float64)
    
    # Initial guess
    if branch == -1:
        w = -2 * np.ones_like(x)  # Start below -1 for the lower branch
    else:
        w = np.ones_like(x)  # Start above -1 for the upper branch
    
    v = np.inf * w  # Initialize previous value for iteration comparison
    
    # Halley's method
    with np.errstate(divide='ignore', invalid='ignore'):
        while np.any(np.abs(w - v) / np.abs(w) > 1e-8):
            v = w
            e = np.exp(w)
            f = w * e - x  # Function to zero
            w = w - f / (e * (w + 1) - (w + 2) * f / (2 * w + 2))
        
    return w