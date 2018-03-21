#!/usr/bin/env python3

"""
Tool to apply Caesar (i.e. rotation) ciphers to a text (encryption or decryption).
"""

import string
import argparse


def rot_char(char, count):
    """
    Rotate a single character by count positions if it is in A-Z or a-z.
    """

    if char in string.ascii_uppercase:
        c = ord(char) + count
        while c > ord('Z'):
            c -= 26
        while c < ord('A'):
            c += 26
        return chr(c)
    if char in string.ascii_lowercase:
        c = ord(char) + count
        while c > ord('z'):
            c -= 26
        while c < ord('a'):
            c += 26
        return chr(c)
    return char


def crypt(text, count):
    """
    Apply the rotation cipher to the text.

    Each character is rotated by count positions.
    """

    return "".join(rot_char(c, count) for c in text)


def crypt_all(text):
    """
    Apply all possible rotation ciphers to the text and return a list with all outputs.
    """

    return [crypt(text, count) for count in range(1, 26)]


if __name__ == "__main__":

    argparser = argparse.ArgumentParser(description="Apply Caesar (rotation) ciphers to a text.")
    argparser.add_argument("text", help="the text to encrypt/decrypt")
    argparser.add_argument("-n", type=int, choices=range(1, 26), help="rotation count")
    args = argparser.parse_args()

    if args.n:
        print(crypt(args.text, args.n))
    else:
        for i, s in enumerate(crypt_all(args.text), start=1):
            print("ROT {}:\n{}\n".format(i, s))
