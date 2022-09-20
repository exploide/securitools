#!/usr/bin/env python3

"""
Generate lists of potential account names, based on 'Firstname Lastname' input.
Lists for different naming schemes will be generated.
"""

import argparse


def main(names_file):
    names = None
    with open(names_file, 'r', encoding='utf-8') as f:
        names = f.readlines()
    names = [n.split() for n in names if n.strip() != ""]

    with open("first.last.txt", 'w', encoding='utf-8') as f:
        for name in names:
            f.write('.'.join([n.lower() for n in name]) + '\n')

    with open("flast.txt", 'w', encoding='utf-8') as f:
        for name in names:
            if len(name) > 1:
                f.write(name[0][0].lower() + name[-1].lower() + '\n')
            else:
                f.write(name[0].lower() + '\n')


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description="Generate lists of potential usernames")
    argparser.add_argument('names', help="File containing 'Firstname Lastname' entries")
    parsed_args = argparser.parse_args()
    main(parsed_args.names)
