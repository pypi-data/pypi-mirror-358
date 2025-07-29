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

def aa_to_num(xseq):
    """
    Converts amino acid sequences to numerical representations.

    Parameters:
        xseq (list of strings): Amino acid sequence(s).

    Returns:
        list: Numerical representation of the amino acid sequences.
    """
    n = len(xseq)  # Number of sequences
    m = len(xseq[0]) if n > 0 else 0  # Length of the first sequence

    # Initialize result list
    mret = []

    for seq in xseq:
        # Convert the amino acid sequence to integers (map from 1 to 20,
        # subtract 1 for 0-indexing)
        vls = aa_to_int(seq)
        vls = [i - 1 for i in vls]  # Subtract 1 to adjust to 0-indexed values
        if -1 in vls:  # Check if any invalid amino acid is encountered
            mret.append(-1)
            continue
        
        # Create the positional powers
        pot = list(range(m))

        # Compute the numerical representation using a loop and sum
        total = 0
        for i, p in enumerate(pot):
            total += (20 ** p) * vls[i]

        mret.append(total)

    return mret

def aa_to_int(aa_list):
    """
    Converts a list of amino acids characters to integer values. The input
    list must be in uppercase for the conversion to be correct.
    
    Parameters:
    - aa_list (list): List of characters (amino acids) to be converted to
      integers.
    
    Returns:
    - list: List of integers corresponding to the characters in the input list.
    """
    # Mapping dictionary
    aa_map = { 
        "A": 1, "B": 21, "C": 5, "D": 4, "E": 7, "F": 14,
        "G": 8, "H": 9, "I": 10, "J": 0, "K": 12, "L": 11,
        "M": 13, "N": 3, "O": 0, "P": 15, "Q": 6, "R": 2,
        "S": 16, "T": 17, "U": 0, "V": 20, "W": 18, "X": 23,
        "Y": 19, "Z": 22, "*": 24, "-": 25, "?": 0
    }
    
    # Mapping the elements of the list to their integer values
    aa_list = [aa_map[aa] for aa in aa_list]
    
    return aa_list