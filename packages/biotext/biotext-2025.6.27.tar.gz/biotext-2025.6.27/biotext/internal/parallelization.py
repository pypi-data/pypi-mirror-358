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

from joblib import Parallel, delayed
from tqdm import tqdm
from .split_array import split_array

def parallelization(data_list, func, chunk_size=1000, n_jobs=1, desc=None,
                    verbose=True):
    """
    Perform parallel processing on a list of data by splitting it into chunks
    and applying a function.

    Parameters:
    - data_list: List of data to be processed.
    - func: Function to apply to each chunk of data.
    - chunk_size: Size of each chunk (default is 1000).
    - n_jobs: Number of parallel jobs to run (default is 1).
    - desc: Description to display alongside the progress tracking (default is
      None).
    - verbose: Boolean flag to enable/disable progress tracking (default is
      True).

    Returns:
    - A flattened list of results from the function applied to each chunk.
    """
    
    # Split the data list into smaller chunks of the specified size
    chunks = split_array(data_list, chunk_size)
    
    # Initialize the progress bar for monitoring progress
    with tqdm(total=len(chunks), desc=desc, ncols=0,
              disable=not verbose) as progress_bar:
        # Use Parallel to apply the function to each chunk of data
        result = Parallel(n_jobs=n_jobs, prefer="threads")(
            delayed(lambda chunk: (func(chunk), progress_bar.update()))(chunk)
            for chunk in chunks
        )
    
    # Extract the results from the tuples returned by Parallel
    result = [i[0] for i in result]
    
    # Flatten the list of results
    result = [item for sublist in result for item in sublist]
    
    return result