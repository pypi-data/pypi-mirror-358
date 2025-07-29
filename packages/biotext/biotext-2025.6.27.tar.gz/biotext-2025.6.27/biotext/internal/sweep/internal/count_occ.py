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

from collections import Counter

def count_occ(input_list):
    """
    Count occurrences of each item in the input list, returning two separate
    lists: one with items and one with their corresponding counts, ordered by
    the items in ascending order.

    Parameters:
        input_list (list): The list of items to count.

    Returns:
        tuple: A tuple containing two lists:
               - A list of items, ordered in ascending order.
               - A list of counts corresponding to each item.
    """
    # Count occurrences using Counter
    count_dict = Counter(input_list)
    
    # Sort items by key and separate into two lists
    items, counts = zip(*sorted(count_dict.items()))
    
    return list(items), list(counts)