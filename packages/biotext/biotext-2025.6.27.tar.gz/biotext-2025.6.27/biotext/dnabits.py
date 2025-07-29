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

"""
This module provides a class with static methods for encoding and decoding
text using dnabits.

methods:
- encode_string: Encodes a string using dnabits.
- decode_string: Decodes a string encoded with dnabits.
- encode_list: Encodes all strings in a list using dnabits.
- decode_list: Decodes all strings in a list encoded with dnabits.
- str_to_bin: Converts a string to a binary representation.
- bin_to_str: Converts a binary representation to a string.
"""

class dnabits:
    
    @staticmethod
    def encode_string(input_string):
        """
        Encodes a string with dnabits.
    
        Parameters
        ----------
        input_string : string
            Natural language text string to be encoded.
    
        Returns
        -------
        encoded_string : string
            Encoded text.
    
        Example
        -------
        Encode a string.
    
        >>> input_string = "Hello world!"
        >>> encoded_string = encode_string(input_string)
        >>> print(encoded_string)
        AGACCCGCATGCATGCTTGCAAGATCTCTTGCGATCATGCACGCCAGA
        """
        
        input_string = dnabits.str_to_bin(input_string)
        
        # Split the binary string into two parts
        text_0 = input_string[0::2]
        text_1 = input_string[1::2]
        
        # Convert binary pairs to DNA characters
        binary_pairs = zip(text_0, text_1)
        dna_chars = {'00': 'A', '01': 'G', '10': 'C', '11': 'T'}
        encoded_string = ''.join(dna_chars[b0 + b1] for b0, b1 in binary_pairs)
        
        return encoded_string
    
    @staticmethod
    def decode_string(input_string):
        """
        Decodes a string with DNAbits reverse.
    
        Parameters
        ----------
        input_string : string
            Text string encoded with dnabits.
    
        Returns
        -------
        decoded_string : string
            Decoded text.
    
        Example
        -------
        Decode a string.
    
        >>> encoded_string = "AGACCCGCATGCATGCTTGCAAGATCTCTTGCGATCATGCACGCCAGA"
        >>> decoded_string = decode_string(encoded_string)
        >>> print(decoded_string)
        Hello world!
        """
        
        # Define the DNA to binary mapping
        dna_to_bin = {'A': '00', 'G': '01', 'C': '10', 'T': '11'}
        
        # Convert DNA string to binary string
        binary_string = ''.join(dna_to_bin[char] for char in input_string)
        
        # Convert binary string to ASCII string
        decoded_string = ''.join(
            dnabits.bin_to_str(binary_string[i:i+8])
            for i in range(0, len(binary_string), 8))
        
        return decoded_string
    
    @staticmethod
    def encode_list(string_list, verbose=False):
        """
        Encodes all strings in a list with dnabits.	
        
        Parameters
        ----------
        string_list : list
            List of string to be encoded.
        verbose  : bool
            If True displays progress.
    
        Returns
        -------
        encoded_list : list
            List with all encoded text in string format.
            
        Example
        -------
        Encode the strings in a list and view the result of the first item.
    
        >>> import biotext as bt
        >>> string_list = ['Hello','world','!']
        >>> encoded_list = bt.dnabits.encode_list(string_list)
        >>> print(encoded_list)
        ['AGACCCGCATGCATGCTTGC', 'TCTCTTGCGATCATGCACGC', 'CAGA']
        """
        
        list_size = len(string_list)
        selectedEncoder = lambda x: dnabits.encode_string(x)
    
        encoded_list = []
        if verbose:
            print('Encoding text...')
        for c,i in enumerate(string_list):
            seq = selectedEncoder(i)
            encoded_list.append(seq)
            if verbose and (c+1) % 10000 == 0:
                print (str(c+1)+'/'+str(list_size))
        if verbose:
            print (str(list_size)+'/'+str(list_size))
        return encoded_list
    
    @staticmethod
    def decode_list(input_list,output_file=None,verbose=False):
        """
        Decodes all strings in a list with reverse dnabits.	
        
        Parameters
        ----------
        string_list : list
            List of string encoded with dnabits.
        verbose  : bool
            If True displays progress.
    
        Returns
        -------
        decoded_list : list of string
            List with all decoded text.
            
        Example
        --------
        Decode the strings in a list and view the result with a loop.
    
        >>> import biotext as bt
        >>> encoded_list = ['AGACCCGCATGCATGCTTGC', 'TCTCTTGCGATCATGCACGC', 'CAGA']
        >>> decoded_list = bt.dnabits.decode_list(encoded_list)
        >>> print(decoded_list)
        ['Hello', 'world', '!']
        """
        
        list_size = len(input_list)
        selectedEncoder = lambda x: dnabits.decode_string(x)
        
        decoded_list = []
        if verbose:
            print('Decoding text...')
        for c,i in enumerate(input_list):
            c+=1
            if verbose and (c+1) % 10000 == 0:
                print(str(c+1)+'/'+str(list_size))
            decoded_list.append((selectedEncoder(str(i))))
        if verbose:
            print(str(list_size)+'/'+str(list_size))
        
        return decoded_list
    
    @staticmethod
    def str_to_bin(string):
        return ''.join(f'{ord(char):08b}'[::-1] for char in string)
    
    @staticmethod
    def bin_to_str(string):
        res = ''
        for idx in range(int(len(string)/8)):
            cstr = string[idx*8:(idx+1)*8]
            cstr=cstr[::-1]
            tmp = chr(int(cstr, 2))
            res += tmp
        return res