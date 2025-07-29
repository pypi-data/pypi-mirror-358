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

def nt_to_num(xseq):
    """
    Converts nucleotide sequences to numerical representations.

    Parameters:
        xseq (list of strings): nucleotide sequence(s).

    Returns:
        list: Numerical representation of the nucleotide sequences.
    """
    n = len(xseq)  # Number of sequences
    m = len(xseq[0]) if n > 0 else 0  # Length of the first sequence

    # Initialize result list
    mret = []

    for seq in xseq:
        # Convert the nucleotide sequence to integers
        vls = nt_to_int(seq)
        vls = [i - 1 for i in vls]  # Subtract 1 to adjust to 0-indexed values
        if -1 in vls:  # Check if any invalid nucleotide is encountered
            mret.append(-1)
            continue
        
        # Create the positional powers
        pot = list(range(m))

        # Compute the numerical representation using a loop and sum
        total = 0
        for i, p in enumerate(pot):
            total += (4 ** p) * vls[i]

        mret.append(total)

    return mret

def nt_to_int(nt_list):
    """
    Converts a list of nucleotide characters to integer values. The input list
    must be in uppercase for the conversion to be correct.
    
    Parameters:
    - nt_list (list): List of characters (nucleotides) to be converted to
      integers.
    
    Returns:
    - list: List of integers corresponding to the characters in the input list.
    """
    # Mapping dictionary
    nt_map = {
        "A":1, "B": 11, "C": 2, "D": 12, "E": 0, "F": 0,
        "G": 3, "H": 13, "I": 0, "J": 0, "K": 7, "L": 0,
        "M": 8, "N": 15, "O": 0, "P": 0, "Q": 0, "R": 5,
        "S": 9, "T": 4, "U": 4, "V": 14, "W": 10, "X": 15,
        "Y": 6, "Z": 0, "*": 0, "-": 16, "?": 0
    }
    
    # Mapping the elements of the list to their integer values
    nt_list = [nt_map[aa] for aa in nt_list]
    
    return nt_list