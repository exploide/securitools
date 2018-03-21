#!/usr/bin/env python3

"""
Tool to apply the Vigenère cipher to a text (encryption and decryption).
"""

import argparse

from caesar import rot_char


def crypt(key, text, decrypt=False):
    """
    Encrypt or decrypt given text with given key using the Vigenère cipher.
    """

    enc_dec_factor = -1 if decrypt else 1
    key_list = [ord(c) - 65 for c in key.upper()]  # map char in key to rotation count
    output = ""
    key_counter = 0
    for c in text:
        if c.isalpha():
            output += rot_char(c, key_list[key_counter] * enc_dec_factor)
            key_counter = (key_counter + 1) % len(key_list)
        else:
            output += c
    return output


if __name__ == "__main__":

    argparser = argparse.ArgumentParser(description="Apply Vigenère cipher to a text.")
    argparser.add_argument("key", help="the key needed for encryption/decryption")
    argparser.add_argument("text", help="the text to encrypt/decrypt")
    argparser.add_argument("-d", action='store_true', help="decrypt instead of encrypt")
    args = argparser.parse_args()

    print(crypt(args.key, args.text, args.d))
