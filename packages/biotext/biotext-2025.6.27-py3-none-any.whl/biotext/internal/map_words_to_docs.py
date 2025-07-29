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

from tqdm import tqdm
from collections import defaultdict

def map_words_to_docs(word_list, tokenized_docs, verbose=True):
    """
    Maps each word in a given list to the documents where it appears.

    This function creates an index that associates each word from `word_list`
    with the documents (by their indices) in which the word is found.

    Parameters:
        - word_list (list): A list of tokens to search for in the documents.
        - tokenized_docs (list): A list of documents, where each document is
          represented as a list of tokens (words).
        - verbose (bool): Boolean flag to enable/disable progress tracking
          (default is True).

    Returns:
        - list of lists: A list containing sublists, where each sublist
          contains the indices of the documents that contain the corresponding
          token in `word_list`. The order of the sublists matches the order of
          tokens in `word_list`.
    """
    # Convert `word_list` to a set for faster lookups
    word_set = set(word_list)

    # Preprocess `tokenized_docs` into a list of sets for efficient membership
    # testing
    tokenized_docs = [set(doc) for doc in tokenized_docs]

    # Initialize the dictionary to hold indices of documents for each token
    token_idx = defaultdict(list)

    # Iterate over each document with its index
    for index, doc in enumerate(tqdm(tokenized_docs, desc='Searching',
                                     ncols=0, disable=not verbose)):
        # Find intersection of tokens in the document with `word_set`
        for token in doc:
            if token in word_set:
                token_idx[token].append(index)

    # Convert `defaultdict` to a list of lists in the order of `word_list`
    return [token_idx[token] for token in word_list]