# Biotext Python Package

![License: Non-Commercial](https://img.shields.io/badge/license-non--commercial-blue.svg)

The Biotext Python Package bridges Bioinformatics and Natural Language Processing (NLP) by adapting biological sequence analysis techniques for Text Mining. At its core, Biotext utilizes the SWeeP algorithm — designed initially for biomolecular data — to introduce SWeePtex (SWeeP for text), a method for large-scale text representation and analysis. The package provides two text-to-BSL (Biological Sequence-Like) encoding schemes: AMINOcode, which models text in an amino acid-inspired (AAL) format, and DNAbits, which employs a nucleotide-like (NTL) representation. By transforming text into BSL, Biotext ensures compatibility with SWeeP, enabling applications in text similarity, clustering, and machine learning while maintaining computational efficiency.

## Features

- **aminocode**: Implements AMINOcode. Encodes and decodes text using amino acid representations.
- **dnabits**: Implements DNAbits. Encodes and decodes text using DNA binary representations.
- **sweeptex**: Implements SWeePtex. Generates fixed-length vector representations of text using the SWeeP algorithm.
- **sweeptex_emb**: Implements Biotext Embedding. Processes text data through a pipeline to generate word and document embeddings.

## Installation

```bash
pip install biotext
````

## Modules

### aminocode

Encode and decode text using amino acid representations.

```python
from biotext import aminocode

# Encode a string
encoded = aminocode.encode_string("Hello world!", 'dp')
print(encoded)  # Output: 'HYELLYQYSYWYQRLDYPW'

# Decode a string
decoded = aminocode.decode_string("HYELLYQYSYWYQRLDYPW", 'dp')
print(decoded)  # Output: 'hello world!'
```

### dnabits

Encode and decode text using DNA binary representations.

```python
from biotext import dnabits

# Encode a string
encoded = dnabits.encode_string("Hello world!")
print(encoded)  # Output: 'AGACCCGCATGCATGCTTGCAAGATCTCTTGCGATCATGCACGCCAGA'

# Decode a string
decoded = dnabits.decode_string("AGACCCGCATGCATGCTTGCAAGATCTCTTGCGATCATGCACGCCAGA")
print(decoded)  # Output: 'Hello world!'
```

### sweeptex

Generate fixed-length vector representations of text using the SWeePtex.

```python
from biotext import sweeptex

corpus = ["This is a sample text", "Another text example"]
embeddings = sweeptex(corpus, emb_size=1200)
print(embeddings.shape)  # Output: (2, 1200)
```

### sweeptex_emb

Process text data through a pipeline to generate word and document embeddings.

```python
from biotext import sweeptex_emb

corpus = ["First document", "Second document text", "Third example"]
results = sweeptex_emb(corpus, return_doc_emb=True, return_word_emb=True)

print(results['doc_emb'].shape)  # Document embeddings
print(results['word_emb'].shape)  # Word embeddings
```

## Authors

- Diogo de Jesus Soares Machado
- Roberto Tadeu Raittz

## License

This project is licensed under a non-commercial license. See the LICENSE.txt file for details.