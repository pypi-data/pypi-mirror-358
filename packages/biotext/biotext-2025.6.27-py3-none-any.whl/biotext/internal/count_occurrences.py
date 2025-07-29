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

def count_occurrences(input_list):
    """
    Counts the occurrences of each item in the input list and returns the
    unique items along with their counts in descending order.

    This function calculates the frequency of each unique item in the provided
    list, sorts the items by their occurrence count in descending order, and
    returns two lists: one with the unique items and one with their
    corresponding counts.

    Parameters:
        - input_list (list): A list of items to count occurrences of.

    Returns:
        - unique_items (list): A list of unique items sorted by occurrence
          count.
        - counts (list): A list of counts corresponding to the unique items,
          sorted in descending order.
    """
    
    # Count the occurrences of each item in the list
    counts = Counter(input_list)
    
    # Extract the unique items and their counts
    unique_items = list(counts.keys())
    counts = list(counts.values())
    
    # Combine items and counts into a list of tuples and sort by count in
    # descending order
    sorted_items_counts = sorted(zip(unique_items, counts), key=lambda x: x[1],
                                 reverse=True)
    
    # Separate the unique items and counts, now sorted
    unique_items, counts = zip(*sorted_items_counts)
    
    return (unique_items, counts)