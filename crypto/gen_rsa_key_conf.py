#!/usr/bin/env python3

"""
This tool can generate the ASN1 input for OpenSSL asn1parse.

It allows to create keys with specifically chosen RSA parameters.
"""

import argparse


if __name__ == '__main__':

    argparser = argparse.ArgumentParser(description="Generate RSA Key configuration for OpenSSL asn1parse.")
    argparser.add_argument("p", type=int, help="first prime")
    argparser.add_argument("q", type=int, help="second prime")
    argparser.add_argument("e", type=int, help="public exponent")
    argparser.add_argument("d", type=int, help="private exponent")
    args = argparser.parse_args()

    n = args.p * args.q
    e1 = args.d % (args.p - 1)
    e2 = args.d % (args.q - 1)
    coeff = pow(args.q, args.p - 2, args.p)

    print("asn1=SEQUENCE:rsa_key")
    print("[rsa_key]")
    print("version=INTEGER:0")
    print("modulus=INTEGER:" + str(n))
    print("pubExp=INTEGER:" + str(args.e))
    print("privExp=INTEGER:" + str(args.d))
    print("p=INTEGER:" + str(args.p))
    print("q=INTEGER:" + str(args.q))
    print("e1=INTEGER:" + str(e1))
    print("e2=INTEGER:" + str(e2))
    print("coeff=INTEGER:" + str(coeff))
