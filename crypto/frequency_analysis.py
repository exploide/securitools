#!/usr/bin/env python3

"""
Tool to analyse the frequencies of the characters in a given text.
"""

import math
import argparse


def analyse(text):
    """
    Return a dictionary with the number of occurrences for each character in the given string.
    """

    frequencies = {}
    for c in text:
        if c in frequencies:
            frequencies[c] += 1
        else:
            frequencies[c] = 1
    return frequencies


def show_statistic(frequencies, sort=0):
    """
    Visualise the frequencies in a diagram.
    """

    n = sum(frequencies[c] for c in frequencies)
    for key, value in sorted(frequencies.items(), key=lambda x: x[sort]):
        percent = (value * 100) / n
        print(f"[{key}] {percent:6.2f}%| {'#'*math.ceil(percent)}")


if __name__ == "__main__":

    argparser = argparse.ArgumentParser(description="Analyse the frequencies of the characters in a text.")
    argparser.add_argument("text", help="the text to analyse")
    argparser.add_argument("--sort", action='store_const', const=1, default=0,
                           help="sort result table according to number of occurrences")
    args = argparser.parse_args()

    show_statistic(analyse(args.text), sort=args.sort)
