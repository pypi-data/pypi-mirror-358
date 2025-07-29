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

import numpy as np
from typing import Optional, Union, List
from .sweeptex import sweeptex
from .internal import (
    parallelization,
    tokenize,
    explode_list,
    count_occurrences,
    map_words_to_docs,
    map_docs_to_words
)


def sweeptex_emb(
    corpus: Union[List[str], np.ndarray],
    word_list: Optional[Union[List[str], np.ndarray]] = None,
    sweeped_corpus: Optional[List[np.ndarray]] = None,
    word_emb: Optional[np.ndarray] = None,
    return_doc_emb: bool = True,
    return_word_emb: bool = True,
    n_jobs: int = 1,
    chunk_size: int = 1000,
    verbose: bool = True
) -> dict:
    """
    SWeePtex Embedding Processor.
    
    This function implements the SWeePtex embedding method which processes text
    data through a pipeline using SWeePtex to generate word and document
    embeddings.

    Parameters:
        - corpus: Input text corpus as a list of documents or numpy array.
        - word_list: Optional custom vocabulary list to override
          automatic generation.
        - sweeped_corpus: Optional pre-processed sweeped corpus to skip
          sweeping step.
        - word_emb: Optional pre-computed word embeddings to skip word
          embedding calculation.
        - return_doc_emb: Whether to compute and return document embeddings
          (default: True).
        - return_word_emb: Whether to compute and return word embeddings
          (default: True).
        - n_jobs: Number of parallel jobs to run (default: 1).
        - chunk_size: Size of chunks for parallel processing (default: 1000).
        - verbose: Whether to print progress messages (default: True).

    Returns:
        - Dictionary containing requested outputs with the following possible
          keys:
            - 'doc_emb': Document embeddings array (if return_doc_emb=True).
            - 'sweeped_corpus': Processed corpus after sweeping.
            - 'word_count': Array of word frequency counts (not generated with
              word_list).
            - 'word_emb': Word embeddings array (if return_word_emb=True).
            - 'word_list': Array of unique words (custom or generated).
            - 'word_to_idx': Dictionary mapping words to indices.

    Raises:
        - TypeError: If input corpus is not a list or numpy array.
        - ValueError: If any of these dimension mismatches occur:
            - When both word_list and word_emb are provided:
                * Length of word_list ({N}) doesn't match first
                  dimension of word_emb ({M}).
            - When only word_emb is provided:
                * First dimension of word_emb ({M}) doesn't match size of
                  generated vocabulary ({K}).
    """
    
    # Input validation
    if not isinstance(corpus, (list, np.ndarray)):
        raise TypeError(
            f"Input must be a list or a NumPy array. "
            f"Received: {type(corpus).__name__}."
        )

    # Early validation of word_list and word_emb dimensions
    if word_list is not None and word_emb is not None:
        if len(word_list) != len(word_emb):
            raise ValueError(
                "Dimension mismatch: word_list has "
                f"{len(word_list)} words but word_emb has "
                f"{len(word_emb)} vectors."
            )

    # Tokenization phase
    tokenize_par = lambda x: tokenize(x)
    tokenized_corpus = parallelization(
        corpus, tokenize_par,
        n_jobs=n_jobs, chunk_size=chunk_size,
        desc="Tokenizing texts",
        verbose=verbose
    )

    # Clean tokens by stripping special characters
    tokenized_corpus = [
        [word.strip("!@#$%^&*()[]{};:\"',<>?.")
         for word in sublist]
        for sublist in tokenized_corpus
    ]
    
    # Handle vocabulary generation or custom word list
    if word_list is not None:
        if verbose:
            print("Using custom word list...")
        word_list = np.array(word_list)
        word_count = None  # Not available with custom word list
    else:
        if verbose:
            print("Creating vocabulary...")
        
        # Create unique word list per document
        tokenized_corpus_set = [sorted(set(i)) for i in tokenized_corpus]

        # Count word occurrences across corpus
        tokenized_corpus_exp = explode_list(
            tokenized_corpus_set,
            return_indices=False
        )
        word_list, word_count = count_occurrences(tokenized_corpus_exp)
        word_list = np.array(word_list)
        word_count = np.array(word_count)

        # Sort words by frequency
        sorted_indices = word_count.argsort(stable=True)[::-1]
        word_list = word_list[sorted_indices]
        word_count = word_count[sorted_indices]
        
        # Validate word_emb dimensions if provided
        if word_emb is not None and len(word_emb) != len(word_list):
            raise ValueError(
                f"Pre-computed word embeddings dimension mismatch. "
                f"Expected {len(word_list)}, got {len(word_emb)}."
            )
    
    # Process corpus through sweeptex or use pre-processed version
    sweeped_corpus = (
        sweeped_corpus if sweeped_corpus is not None else
        sweeptex(corpus)
    )

    # Create word to index mapping
    word_to_idx = {item: index for index, item in enumerate(word_list)}
    
    # Initialize output dictionary
    output_dict = {
        'sweeped_corpus': sweeped_corpus,
        'word_list': word_list,
        'word_to_idx': word_to_idx
    }
    
    # Add word_count only if not using custom word list
    if word_list is None:
        output_dict['word_count'] = word_count

    # Word embedding calculation (if requested)
    if return_word_emb:
        if word_emb is None:
            word_doc_idx = map_words_to_docs(
                word_list, tokenized_corpus,
                verbose=verbose
            )
            
            word_emb_fun_par = lambda x: [
                np.mean(j, axis=0, where=~np.isnan(j))
                for j in [sweeped_corpus[i] for i in x]
            ]
            word_emb = parallelization(
                word_doc_idx, word_emb_fun_par,
                n_jobs=n_jobs, chunk_size=chunk_size,
                desc="Creating word embedding",
                verbose=verbose
            )
            word_emb = np.array(word_emb, dtype=np.float32)
        
        output_dict['word_emb'] = word_emb

    # Document embedding calculation (if requested)
    if return_doc_emb:        
        doc_word_idx = map_docs_to_words(
            tokenized_corpus, word_list,
            verbose=verbose
        )
        
        doc_emb_fun_par = lambda x: [
            np.mean(j, axis=0, where=~np.isnan(j))
            for j in [word_emb[i] for i in x]
        ]
        doc_emb = parallelization(
            doc_word_idx, doc_emb_fun_par,
            n_jobs=n_jobs, chunk_size=chunk_size,
            desc="Creating document embedding",
            verbose=verbose
        )
        doc_emb = np.array(doc_emb, dtype=np.float32)
        
        output_dict['doc_emb'] = doc_emb

    return output_dict