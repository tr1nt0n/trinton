import abjad
import evans
import trinton
import random

def rotated_sequence(pitch_list, start_index):
    result = []
    rotated_list = pitch_list[start_index:] + pitch_list[:start_index]
    for pitch in rotated_list:
        result.append(pitch)
    return result

def countList(lst1, lst2):
    return [sub[item] for item in range(len(lst2))
    for sub in [lst1, lst2]]

def primes_odds_evens(lst):
    odds = []
    evens = []
    final = []
    for number in lst:
        if(number%2==0):
            evens.append(number)

        else:
            odds.append(number)

    for number in odds:
        final.append(number)

    for number in evens:
        final.append(number)

    return final
