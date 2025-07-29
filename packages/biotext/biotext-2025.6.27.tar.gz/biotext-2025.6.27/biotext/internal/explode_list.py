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

def explode_list(lists_of_lists, return_indices=False):
    """
    Flattens a list of lists into a single list and optionally returns the
    indices.

    This function takes a list of lists and flattens it into a single list.
    Each item from the sublists is added to the flattened list, and the
    function can optionally return the indices of the items in the original
    structure.

    Parameters:
        - lists_of_lists (list of lists): A list where each element is a
          sublist that needs to be flattened.
        - return_indices (bool, optional): If True, returns the indices of the
          original items. Defaults to False.

    Returns:
        - list: The flattened list containing all the elements from the
          sublists.
        - list of tuples (optional): If return_indices is True, a list of
          tuples where each tuple represents the indices of the items in the
          original sublists.
    """
    flattened_list = []
    indices = []
    
    for sublist_idx, sublist in enumerate(lists_of_lists):
        for item_idx, item in enumerate(sublist):
            flattened_list.append(item)
            indices.append((sublist_idx, item_idx))
    
    if return_indices:
        return flattened_list, indices
    else:
        return flattened_list