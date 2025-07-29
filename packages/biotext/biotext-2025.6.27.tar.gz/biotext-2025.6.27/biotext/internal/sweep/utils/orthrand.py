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

def orthrand(xlines, Um, Un):
    """
    Generates orthonormal projection lines for use in the SweeP strategy 
    with a new pseudorandom generator approach.

    This function creates a pair of projections based on the input 
    vectors `Um` and `Un` using a mathematical transformation and returns 
    the result.

    Parameters:
        xlines (array-like): Indices of the lines to be used in the projection.
        Um (array-like): Array of values used to generate `Z1`.
        Un (array-like): Array of values used to generate `Z2`.

    Returns:
        np.ndarray: Array containing the orthonormal projections.
    """
    maxcol = len(Um)  # Get the number of columns in Um
    
    nlines = len(xlines)  # Get the number of lines
    Un = Un[xlines]  # Access Un at the positions defined by `xlines`

    # Partitioning process to generate Z1 and Z2:
    # - Generate Z1 based on Um
    Z1 = np.float32(10**8 * (10**4 * Um - np.trunc(10**4 * Um)))
    # - Generate Z2 based on Un
    Z2 = np.float32(10**8 * (10**4 * Un - np.trunc(10**4 * Un)))
    
    Z1 = np.repeat([Z1], nlines, axis=0)
    Z2 = np.repeat([Z2], maxcol, axis=0).T

    # Calculate the orthonormal projection result
    # Apply the sine function to the product of Z1 and Z2
    mret = np.sin(Z1 * Z2)
    
    # Return the resulting projections
    return mret

