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

import re

def tokenize(text_list):
    """
    Tokenizes a list of text strings into words.

    This function splits each string in the input list into individual words
    based on word boundaries using regular expressions.

    Parameters:
        - text_list (list of str): A list of text strings to be tokenized.

    Returns:
        - list of list of str: A list where each element is a list of words
          corresponding to a string in the input text list.
    """
    # Split phrases into words
    return [re.findall(r'\b\w+\b', text) for text in text_list]