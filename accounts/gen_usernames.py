#!/usr/bin/env python3

"""
Generate lists of potential account names, based on file input.
Lists for different naming schemes will be generated.
"""

import argparse
import itertools


def main(names_files):
    names = None
    if len(names_files) == 1:
        # file with combined 'Firstname Lastname' entries
        with open(names_files[0], 'r', encoding='utf-8') as f:
            names = [n.lower().split() for n in f.readlines() if n.strip() != ""]
    else:
        # separate files with 'Firstname' and 'Lastname'
        with open(names_files[0], 'r', encoding='utf-8') as f:
            firstnames = [n.lower().strip() for n in f.readlines() if n.strip() != ""]
        with open(names_files[1], 'r', encoding='utf-8') as f:
            lastnames = [n.lower().strip() for n in f.readlines() if n.strip() != ""]
        names = list(itertools.product(firstnames, lastnames))

    with open("first.last.txt", 'w', encoding='utf-8') as f:
        for name in names:
            f.write('.'.join(name) + '\n')

    with open("flast.txt", 'w', encoding='utf-8') as f:
        for name in names:
            if len(name) > 1:
                f.write(name[0][0] + name[-1] + '\n')
            else:
                f.write(name[0] + '\n')


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description="Generate lists of potential usernames")
    argparser.add_argument('names', nargs='+', help="Files containing name entries. Either one file with 'Firstname Lastname' or two separate files with 'Firstname' and 'Lastname' for cartesian product.")
    parsed_args = argparser.parse_args()
    if len(parsed_args.names) > 2:
        argparser.error("Give either one file with 'Firstname Lastname' or two separate files with 'Firstname' and 'Lastname' for cartesian product.")
    main(parsed_args.names)
