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

def map_docs_to_words(tokenized_docs, word_list, verbose=True):
    """
    Maps each document to the words (tokens) it contains from a given list.

    This function creates an index that associates each document (by its index)
    with the words from `word_list` that appear in it.
    
    Parameters:
        - tokenized_docs (list): A list of documents, where each document is
          represented as a list of tokens (words).
        - word_list (list): A list of target tokens to search for in the
          documents.
        - verbose (bool): Boolean flag to enable/disable progress tracking
          (default is True).
    
    Returns:
        - list of lists: A list where each element is a sublist containing the
          indices of tokens (from `word_list`) found in the corresponding
          document. The order of the sublists matches the order of documents
          in `tokenized_docs`.
    """
    # Create a dictionary mapping tokens to their indices in `word_list`
    word_dict = {token: i for i, token in enumerate(word_list)}
    
    # Create a set of tokens for faster membership testing
    word_keys = set(word_dict.keys())

    # Initialize the result list
    doc_word_idx = []

    # Iterate over the tokenized documents
    for doc in tqdm(tokenized_docs, desc='Searching', ncols=0,
                    disable=not verbose):
        # Get the indices of tokens present in the current document
        doc_word_idx.append([word_dict[token] for token in doc if token in
                             word_keys])

    return doc_word_idx