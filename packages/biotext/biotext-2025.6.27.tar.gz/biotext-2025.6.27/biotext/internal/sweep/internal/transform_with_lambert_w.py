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
from .lambert_w import lambert_w

def transform_with_lambert_w(kmer_counts):
    """
    Apply a transformation to input values using the Lambert W function.

    This function transforms the input values using a custom transformation
    involving the Lambert W function. Specifically, it computes:
        fx(x) = (-W₀(-exp(-x) * x))^0.1,
    where W₀ is the upper branch of the Lambert W function. After the
    transformation, any zeros in the result are replaced with -1.

    Parameters:
        - values (array-like): Array of values to be transformed.
          Expected to be non-negative values.

    Returns:
        - numpy.ndarray: The transformed values, with zeros replaced by -1.
    """
    # Define the function fx using Lambert W
    fx = lambda x: (-lambert_w(0, -np.exp(-x) * x)) ** 0.1
    
    # Apply the transformation
    u = fx(kmer_counts)
    
    # Replace zeros with -1
    u[u == 0] = -1
    
    return u