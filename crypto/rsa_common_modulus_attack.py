#!/usr/bin/env python3

import argparse
import base64
import sys

from cryptography.hazmat.primitives import serialization
import gmpy2


def msg_file_to_int(msg, byteorder=sys.byteorder):
    """
    Given the name of a file containing a base64-encoded ciphertext,
    return the decoded ciphertext as an integer.
    """
    with open(msg) as f:
        return int.from_bytes(base64.b64decode(f.read()), byteorder=byteorder)


def parse_rsa_files(key1, key2):
    """
    Given two RSA public key files in PEM format sharing the same modulus,
    return the modulus and the two exponents.
    """
    rsa1 = None
    rsa2 = None
    with open(key1, 'rb') as f:
        rsa1 = serialization.load_pem_public_key(f.read()).public_numbers()
    with open(key2, 'rb') as f:
        rsa2 = serialization.load_pem_public_key(f.read()).public_numbers()
    if rsa1.n != rsa2.n:
        print("Error: The keys do not share the same modulus!")
        exit(1)
    return rsa1.n, rsa1.e, rsa2.e


def common_modulus_attack(modulus, exp1, exp2, msg1, msg2):
    """
    Perform RSA Common Modulus Attack, given the modulus, two exponents
    and two ciphertexts as integers.
    Returns the plaintext as an integer.
    """
    g, s, t = gmpy2.gcdext(exp1, exp2)
    if g != 1:
        print("Error: GCD of the two exponents is not 1!")
    tmp1 = gmpy2.powmod(msg1, s, modulus)
    tmp2 = gmpy2.powmod(msg2, t, modulus)
    return int(gmpy2.mod(tmp1 * tmp2, modulus))


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description="Perform Common Modulus Attack against RSA")
    argparser.add_argument("key1", help="File containing first RSA public key in PEM format")
    argparser.add_argument("key2", help="File containing second RSA public key in PEM format")
    argparser.add_argument("msg1", help="File containing first base64-encoded ciphertext")
    argparser.add_argument("msg2", help="File containing second base64-encoded ciphertext")
    argparser.add_argument("--byteorder", default=sys.byteorder, choices=["little", "big"], help="Byteorder for message decoding")
    args = argparser.parse_args()

    n, e1, e2 = parse_rsa_files(args.key1, args.key2)
    m1 = msg_file_to_int(args.msg1, args.byteorder)
    m2 = msg_file_to_int(args.msg2, args.byteorder)
    plain = common_modulus_attack(n, e1, e2, m1, m2)
    plain_bytes = plain.to_bytes((plain.bit_length() + 7) // 8, byteorder=args.byteorder)
    print(plain_bytes.decode(encoding="UTF-8"))
