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
from .internal import (create_seqrecord_list, parallelization, sweep)
from .aminocode import aminocode

def sweeptex(corpus, emb_size=1200, n_jobs=1, chunk_size=1000, verbose=True):
    """
    Runs SWeeP on the encoded text to generate fixed-length vector
    representations.

    Parameters:
        - corpus (list or np.ndarray): Input text data to be processed. Each
          element should be a text string.
        - emb_size (int, optional): The size of the output word embedding.
          Must be divisible by 4. Defaults to 1200.
        - n_jobs (int, optional): Number of parallel jobs to run for
          processing. Defaults to 1.
        - chunk_size (int, optional): Number of items to process in each
          parallel batch. Defaults to 1000.
        - verbose (bool, optional): If True, prints progress during the
          process. Default is True.
          
    Returns:
        - numpy.ndarray: A 2D array where each row represents the SWeeP
          projection of the corresponding input text. The shape will be
          (len(corpus), emb_size).

    Raises:
        TypeError: If the input corpus is not a list or numpy array.
        ValueError: If emb_size is not divisible by 4.
    """
    
    if verbose:
        print("Starting SWeeP...")
    
    # Check if the type is either list or np.ndarray
    if not isinstance(corpus, (list, np.ndarray)):
        raise TypeError(
            f"Input must be a list or a NumPy array. "
            f"Received: {type(corpus).__name__}."
        )
        
    if emb_size % 4 != 0:
        raise ValueError(f"proj_size ({emb_size}) must be divisible by 4.")
    
    # Define parallel processing function for encoding
    par_function = lambda x: aminocode.encode_list(x)
    encoded_corpus = parallelization(
        corpus,
        par_function,
        n_jobs=n_jobs,
        chunk_size=chunk_size,
        desc="Encoding",
        verbose=verbose
    )

    # Define mask patterns for spaced words projection
    mask = [[1,1,0,0,1], [1,1,1,0,0], [1,0,1,0,1], [1,1,0,1,0]]
    # Divide embedding size among 4 mask patterns
    proj_size = int(emb_size / 4)

    # Calculate number of positions to consider based on mask
    ntake = sum(mask[0])
    # Create projection matrix for the specified dimensions
    proj = sweep.create_proj_mat(20**ntake, proj_size)

    # Convert encoded corpus to FASTA format records
    encoded_corpus_fasta = create_seqrecord_list(encoded_corpus)
    # Apply SWeeP projection to the encoded corpus
    sweeped_corpus = sweep.fasta_to_sweep(
        encoded_corpus_fasta,
        proj=proj,
        mask=mask,
        n_jobs=n_jobs, chunk_size=chunk_size,
        print_details=False,
        progress_bar=verbose
    )
    
    if verbose:
        print("SWeeP completed.")
    
    return sweeped_corpus