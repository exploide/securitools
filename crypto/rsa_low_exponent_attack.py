#!/usr/bin/env python3

"""
Tool to perform the low exponent attack against RSA.

If the public exponent e is sufficiently small and
one obtained e times the ciphertext of a fixed message
along with the differing moduli, the plaintext can be
recovered.
"""

import argparse
from functools import reduce
from operator import mul
import sys

import gmpy2


def xgcd(b, n):
    """
    Extended Euclidean Algorithm
    """

    x0, x1, y0, y1 = 1, 0, 0, 1
    while n != 0:
        q, b, n = b // n, n, b % n
        x0, x1 = x1, x0 - q * x1
        y0, y1 = y1, y0 - q * y1
    return b, x0, y0


def crt(moduli, x_list):
    """
    Chinese Remainder Theorem
    """

    modulus = reduce(mul, moduli, 1)
    multipliers = []
    for m in moduli:
        M = modulus // m
        _, inverse, _ = xgcd(M, m)
        multipliers.append((inverse * M) % modulus)
    result = 0
    for multi, x in zip(multipliers, x_list):
        result = (result + multi * x) % modulus
    return result


def low_exponent_attack(moduli, ciphertexts):
    """
    Low Exponent Attack against RSA
    """

    c = crt(moduli, ciphertexts)
    root, _ = gmpy2.iroot(c, len(rsa_moduli))
    return int(root)


def parse_file(filename, input_base):
    """
    Parse input file containing moduli or ciphertexts and return a list of them
    """

    content = []
    with open(filename, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                content.append(int(line, input_base))
    if len(set(content)) != len(content):
        print(f"Error: {filename} contains some duplicates, this won't work!", file=sys.stderr)
        sys.exit(1)
    return content


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description="Perform low exponent attack against RSA.")
    argparser.add_argument("moduli", help="file containing the used RSA moduli one per line")
    argparser.add_argument("ciphertexts", help="file containing the ciphertexts one per line")
    argparser.add_argument("--hex", dest="base", action="store_const", const=16, default=10, help="data in input files is hex encoded")
    args = argparser.parse_args()

    rsa_moduli = parse_file(args.moduli, args.base)
    rsa_ciphertexts = parse_file(args.ciphertexts, args.base)

    plain_int = low_exponent_attack(rsa_moduli, rsa_ciphertexts)
    print("Plaintext (integer):")
    print(plain_int)

    plain_hex = hex(plain_int)[2:]
    print("Plaintext (hex):")
    print(plain_hex)

    plain_bytes = bytes.fromhex(plain_hex)
    plain_utf8 = plain_bytes.decode('utf-8')
    print("Plaintext (utf-8):")
    print(plain_utf8)
