#!/usr/bin/env python3

"""
Tool to perform the low exponent attack against RSA.
"""

import argparse
from functools import reduce
from operator import mul

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


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description="Perform low exponent attack against RSA.")
    argparser.add_argument("moduli", help="file containing the used RSA moduli one per line")
    argparser.add_argument("ciphertexts", help="file containing the ciphertexts one per line")
    args = argparser.parse_args()

    rsa_moduli = []
    rsa_ciphertexts = []

    with(open(args.moduli)) as f:
        for line in f:
            if line.strip() != "":
                rsa_moduli.append(int(line))

    with(open(args.ciphertexts)) as f:
        for line in f:
            if line.strip() != "":
                rsa_ciphertexts.append(int(line))

    print(low_exponent_attack(rsa_moduli, rsa_ciphertexts))
