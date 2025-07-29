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

def create_sweep_masks(nbits, ntake):
    """
    Generate all binary vector combinations of length `nbits` with exactly
    `ntake` ones.

    This function recursively creates all possible binary vectors of length
    `nbits` where exactly `ntake` elements are set to 1, and the remaining
    elements are set to 0.
    
    Parameters:
    - nbits (int): The total number of elements in the binary vector.
    - ntake (int): The number of elements in the binary vector to be set to 1.

    Returns:
    - list of lists: A list containing all possible binary vectors of length
      `nbits` with exactly `ntake` ones. Each binary vector is represented as
      a list of 0s and 1s.
    """
    
    # Recursive helper function to generate combinations of binary vectors
    # with exactly `ntake` ones
    def generate_combination(position, nbits, ntake, vector):
        if ntake == 0:
            combinations.append(vector[:])
            return
        if position == nbits:
            return
        
        # Place a 1 at the current position and recursively generate the next
        # vector
        vector[position] = 1
        generate_combination(position + 1, nbits, ntake - 1, vector)
        
        # Place a 0 at the current position and recursively generate the next
        # vector
        vector[position] = 0
        generate_combination(position + 1, nbits, ntake, vector)
    
    combinations = []
    initial_vector = [0] * nbits
    generate_combination(0, nbits, ntake, initial_vector)
    
    return combinations