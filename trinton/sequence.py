import abjad
import evans
import trinton
import random
from random import randint
import itertools
from itertools import combinations


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


def logistic_map(x, r, n, seed):
    out = []

    def logisticmap(x=x, r=r):

        return x * r * (1 - x)

    def iterate(n=n, x=x, r=r):

        for i in range(1, n):
            x = logisticmap(x, r)

        return x

    l = [int(_) for _ in str(iterate())]

    for number in l:
        out.append(number)

    return out

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
        else: a.append(item)
    return a
