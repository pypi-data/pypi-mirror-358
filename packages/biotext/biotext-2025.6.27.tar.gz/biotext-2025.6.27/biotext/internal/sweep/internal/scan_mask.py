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

def scan_mask(xseq, xmask):
    """
    Performs a scan on the sequence `xseq` based on the mask `xmask`.
    Optimizes memory usage for masks with large `nbits`.

    Parameters:
        xseq (str): Amino acid sequence.
        xmask (list or array-like): Binary mask to apply to the sequence.

    Returns:
        list: Extracted columns based on the mask.
    """
    xseq_len = len(xseq)  # Length of the sequence
    
    # Ensure a minimum sequence length of 10
    min_len = 10
    if xseq_len < min_len:
        xseq = xseq + "K" * (min_len - xseq_len)
        xseq = xseq[:min_len]
        
        xseq_len = min_len

    # Indices where the mask is 1
    ids = (i for i, bit in enumerate(xmask) if bit)
    
    IDS = [
        range(idx, min(idx + xseq_len, xseq_len))
        for idx in ids
    ]

    # Find the minimum length across all IDS arrays
    lmx = min(map(len, IDS))

    # Extract columns based on the mask and ensure uniformity
    xcols = [xseq[idx] for ids_array in IDS for idx in ids_array[:lmx]]

    xcols = [xcols[i:i+lmx] for i in range(0, len(xcols), lmx)]
    
    xcols = list(zip(*xcols))
    
    return xcols