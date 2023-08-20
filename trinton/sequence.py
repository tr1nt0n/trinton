import abjad
import evans
import itertools
import trinton
import random
from random import randint
from itertools import combinations
from itertools import cycle


def rotated_sequence(pitch_list, start_index):
    result = []
    rotated_list = pitch_list[start_index:] + pitch_list[:start_index]
    for pitch in rotated_list:
        result.append(pitch)
    return result


def countList(lst1, lst2):
    return [sub[item] for item in range(len(lst2)) for sub in [lst1, lst2]]


def primes_odds_evens(lst):
    odds = []
    evens = []
    final = []
    for number in lst:
        if number % 2 == 0:
            evens.append(number)

        else:
            odds.append(number)

    for number in odds:
        final.append(number)

    for number in evens:
        final.append(number)

    return final


def logistic_map(x, r, n):
    """
    Creates a logistic map rounded to whole integers.

    >>> import trinton
    >>> logistic = trinton.logistic_map(x=4, r=-1, n=12)
    >>> logistic
    [7, 6, 7, 6, 4, 9, 7, 7, 5, 0, 0, 4, 7, 7, 8, 8, 7, 1, 6, 1, 0, 7, 5, 1, 1, 5, 0, 4, 2, 2, 2, 0, 1, 5, 8, 0, 1, 1, 4, 0, 5, 4, 5, 8, 3, 3, 6, 1, 3, 3, 2, 2, 4, 1, 2, 3, 1, 5, 6, 8, 0, 6, 5, 1, 6, 5, 4, 8, 2, 0, 6, 9, 9, 1, 9, 5, 4, 3, 9, 5, 0, 5, 7, 8, 3, 1, 2, 0, 9, 8, 6, 2, 2, 1, 1, 9, 6, 7, 5, 2, 3, 7, 9, 2, 1, 5, 3, 9, 7, 3, 0, 5, 6, 0, 8, 8, 6, 2, 7, 1, 3, 1, 7, 1, 6, 6, 3, 6, 0, 0, 2, 5, 6, 2, 9, 5, 9, 8, 4, 9, 2, 7, 4, 2, 8, 6, 7, 8, 9, 0, 0, 3, 5, 3, 8, 4, 7, 2, 4, 6, 3, 5, 7, 1, 7, 2, 6, 4, 7, 3, 9, 6, 4, 5, 9, 5, 1, 6, 6, 8, 3, 4, 6, 5, 9, 8, 4, 1, 3, 3, 7, 2, 4, 3, 0, 2, 0, 4, 7, 5, 5, 4, 9, 4, 8, 2, 0, 8, 8, 7, 9, 1, 7, 5, 3, 2, 4, 0, 2, 6, 9, 9, 9, 6, 0, 9, 5, 8, 5, 4, 1, 3, 8, 5, 1, 4, 5, 7, 3, 6, 6, 3, 3, 9, 3, 9, 3, 6, 1, 4, 7, 7, 8, 4, 7, 3, 4, 5, 5, 7, 3, 8, 2, 3, 5, 6, 1, 8, 3, 5, 3, 3, 6, 6, 3, 1, 7, 8, 0, 7, 0, 4, 6, 8, 2, 2, 8, 6, 4, 0, 8, 8, 8, 0, 1, 6, 2, 7, 9, 3, 2, 4, 8, 5, 9, 7, 5, 7, 2, 9, 9, 6, 0, 4, 7, 9, 8, 6, 9, 5, 2, 4, 0, 8, 0, 8, 1, 7, 4, 5, 0, 0, 6, 0, 6, 1, 5, 5, 9, 2, 4, 0, 9, 6, 0, 8, 8, 1, 5, 9, 3, 9, 0, 5, 3, 6, 2, 9, 8, 9, 6, 3, 6, 4, 2, 0, 0, 0, 3, 1, 0, 5, 0, 3, 4, 0, 0, 2, 0, 4, 6, 6, 2, 0, 4, 8, 5, 7, 3, 0, 4, 1, 0, 9, 8, 9, 5, 1, 9, 3, 8, 6, 5, 9, 8, 7, 6, 4, 9, 4, 9, 4, 2, 5, 4, 6, 1, 7, 2, 0, 7, 8, 9, 2, 3, 6, 7, 2, 1, 2, 4, 5, 6, 7, 7, 2, 1, 4, 5, 2, 6, 9, 3, 8, 8, 8, 2, 7, 7, 6, 1, 0, 0, 2, 6, 2, 6, 9, 6, 0, 9, 3, 6, 6, 5, 0, 1, 1, 8, 3, 3, 3, 0, 7, 4, 3, 6, 4, 7, 1, 6, 6, 3, 8, 6, 0, 2, 1, 1, 6, 9, 4, 9, 6, 7, 1, 2, 2, 0, 6, 6, 7, 8, 2, 7, 1, 4, 5, 8, 8, 7, 9, 9, 4, 3, 5, 5, 8, 9, 4, 8, 0, 9, 6, 4, 8, 0, 7, 5, 7, 9, 6, 4, 7, 2, 7, 1, 8, 2, 8, 9, 5, 8, 3, 9, 4, 1, 5, 5, 3, 8, 6, 0, 9, 9, 2, 5, 8, 3, 0, 0, 0, 0, 9, 2, 6, 4, 4, 7, 2, 4, 5, 7, 2, 0, 0, 1, 9, 3, 8, 8, 7, 2, 8, 1, 7, 2, 9, 9, 9, 2, 2, 7, 2, 7, 8, 9, 1, 6, 5, 8, 8, 7, 6, 5, 2, 8, 7, 3, 9, 7, 4, 5, 6, 5, 4, 9, 8, 7, 1, 6, 7, 3, 5, 2, 0, 3, 7, 1, 6, 6, 2, 9, 0, 3, 2, 8, 1, 2, 9, 7, 9, 0, 0, 9, 7, 2, 8, 7, 7, 4, 0, 3, 3, 1, 6, 7, 6, 3, 0, 6, 5, 4, 9, 0, 9, 8, 1, 5, 1, 3, 3, 2, 6, 5, 7, 5, 3, 9, 2, 4, 0, 3, 9, 8, 2, 8, 5, 5, 0, 4, 3, 6, 2, 2, 2, 8, 6, 5, 4, 3, 8, 1, 5, 2, 3, 3, 9, 7, 3, 3, 7, 5, 1, 4, 8, 1, 9, 0, 7, 2, 1, 9, 4, 3, 4, 4, 1, 0, 5, 4, 1, 1, 9, 6, 6, 9, 1, 4, 8, 0, 8, 2, 2, 6, 1, 8, 3, 0, 6, 0, 0, 9, 5, 5, 3, 8, 7, 9, 1, 9, 7, 9, 7, 8, 6, 3, 1, 6, 4, 2, 3, 0, 2, 0, 0, 2, 1, 8, 4, 7, 6, 1, 7, 1, 2, 1, 9, 0, 7, 5, 2, 8, 5, 6, 5, 6, 0, 0, 8, 6, 5, 8, 7, 2, 6, 4, 2, 2, 0, 8, 5, 4, 3, 1, 3, 6, 8, 5, 4, 9, 6, 3, 6, 6, 6, 9, 7, 7, 3, 9, 2, 8, 3, 6, 1, 9, 5, 4, 4, 1, 7, 5, 2, 0, 0, 1, 7, 5, 3, 0, 8, 9, 7, 1, 9, 8, 8, 2, 4, 1, 5, 7, 3, 7, 9, 3, 8, 8, 4, 3, 3, 7, 3, 6, 3, 4, 8, 6, 6, 4, 4, 0, 7, 7, 7, 7, 0, 7, 8, 2, 7, 2, 2, 5, 9, 5, 5, 8, 4, 6, 1, 5, 0, 1, 2, 4, 8, 8, 4, 2, 2, 7, 9, 9, 9, 6, 9, 7, 6, 4, 4, 9, 0, 2, 2, 3, 6, 1, 2, 5, 8, 7, 8, 6, 1, 4, 1, 2, 9, 6, 5, 9, 1, 8, 4, 9, 9, 7, 0, 5, 4, 4, 6, 8, 8, 6, 0, 9, 8, 2, 4, 9, 4, 1, 1, 0, 7, 5, 5, 7, 9, 1, 0, 1, 9, 7, 5, 6, 0, 8, 9, 2, 9, 0, 1, 7, 4, 5, 8, 2, 7, 3, 3, 1, 6, 0, 4, 2, 3, 0, 2, 5, 6, 2, 1, 0, 1, 4, 0, 9, 5, 1, 9, 7, 4, 3, 2, 4, 2, 4, 5, 5, 6, 3, 8, 2, 7, 0, 8, 9, 7, 8, 9, 3, 9, 1, 1, 2, 8, 1, 6, 6, 9, 0, 8, 3, 5, 8, 7, 6, 6, 8, 9, 7, 3, 4, 1, 1, 9, 1, 0, 3, 0, 5, 8, 8, 5, 1, 7, 2, 5, 5, 0, 9, 2, 5, 0, 4, 3, 7, 5, 6, 9, 2]

    """

    # if n > 9:
    #     raise Exception("n must be a whole number smaller than 10")

    for i in range(1, n):
        x = x * r * (1 - x)

    # digits = [int(_) for _ in str(x)]
    digits = []

    for _ in str(x):
        if _ == "." or _ == "-" or _ == "e" or _ == "+":
            pass

        else:
            digits.append(int(_))

    return digits


def remove_all(l, remove_all):
    for _ in l:
        for item in remove_all:
            if _ == item:
                l.remove(_)
    return l


def all_additions(lst, s, pair_num):
    return [pair for pair in combinations(lst, pair_num) if sum(pair) == s]


def remove_adjacent(sequence):
    a = []
    for item in sequence:
        if len(a):
            if a[-1] != item:
                a.append(item)
        else:
            a.append(item)
    return a


def return_middle_index(sequence):
    if len(sequence) % 2 == 0:
        half = (len(sequence) - 1) / 2
        return half + 0.5
    else:
        return (len(sequence) - 1) / 2


def correct_redundant_floats(n):
    string = str(n)
    if len(string) < 3:
        pass
    else:
        if string[-1] == "0" and string[-2] == ".":
            n = int(n)

    return n


def make_float(n):
    n = float(n)
    return n
