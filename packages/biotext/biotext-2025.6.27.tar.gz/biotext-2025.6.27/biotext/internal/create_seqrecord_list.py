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

from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
import re

def create_seqrecord_list(seq_list, header_list=None):
    """
    Creates a list of SeqRecord (Biopython object) from a list of sequences.

    This function takes a list of biological sequences and, optionally, a list
    of headers, and creates a list of SeqRecord objects with corresponding
    headers.

    Parameters:
        - seq_list (list of str): List of biological sequences in string
          format.
        - header_list (list of str or None): List of headers in string format.
          If None, the headers will be automatically assigned as numbers in
          increasing order.

    Returns:
        - list of SeqRecord: List of SeqRecord objects created from the input
          sequences and headers.
    """
    if header_list is None:
        header_list = list(range(1, len(seq_list) + 1))
    
    seqrecord_list = []
    for i in range(len(seq_list)):
        description = str(header_list[i])
        ident = re.split('\s+', description)[0]
        record = SeqRecord(Seq(seq_list[i]), description=description, id=ident)
        seqrecord_list.append(record)
    
    return seqrecord_list