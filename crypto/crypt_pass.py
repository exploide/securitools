#!/usr/bin/env python3

"""
Simple tool to produce crypt hashes out of given passwords.

Instead of weak DES-based hashes, the strongest method available is used, e.g. SHA-512.
"""

from crypt import crypt
from getpass import getpass


def main():
    pw = getpass("Password to hash using crypt: ")
    h = crypt(pw)
    print(h)


if __name__ == '__main__':
    main()
