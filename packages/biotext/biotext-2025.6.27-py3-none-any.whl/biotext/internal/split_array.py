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

def split_array(arr, chunk_size):
    """
    Splits an array into chunks of a specified size.

    This function divides the input array into smaller subarrays, each
    containing up to `chunk_size` elements. If the array size is not a
    multiple of `chunk_size`, the final chunk will contain the remaining
    elements.

    Parameters:
        - arr (list): The input array to be split.
        - chunk_size (int): The size of each chunk.

    Returns:
        - list of list: A list containing subarrays (chunks), where each chunk
          has a maximum of `chunk_size` elements.
    """
    chunks = []
    for i in range(0, len(arr), chunk_size):
        chunks.append(arr[i:i+chunk_size])
    return chunks