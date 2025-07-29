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

from setuptools import setup, find_packages
from datetime import datetime

# Get current date in YYYY.MM.DD format
current_date = datetime.now().strftime("%Y.%m.%d")

setup(
    name='biotext',
    version=current_date,  # Uses automatically generated date version
    author='Diogo de Jesus Soares Machado, Roberto Tadeu Raittz',
    description=(
        'Biotext bridges Bioinformatics and NLP by encoding data into a '
        'Biological Sequence-Like format. Combined with the SWeeP method, it '
        'supports vector operations for efficient analysis.'
    ),
    packages=find_packages(),
    long_description_content_type='text/markdown',
    long_description=open('README.md').read(),
    zip_safe=False,
    install_requires=[
        'biopython==1.85',
        'h5py==3.13.0',
        'joblib==1.4.2',
        'numpy==2.2.4',
        'scipy==1.15.2',
        'tqdm==4.67.1'
    ],
    license='Custom Non-Commercial License',
    license_files=['LICENSE.txt']
)