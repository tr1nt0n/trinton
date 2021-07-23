import abjad
import evans


def make_pitches(pitch_list):
    out = []
    for _ in pitch_list:
        out.append(abjad.namedpitch(_))
    return out

def transpose(l, m):
    out = []
    for _ in l:
        out.append(_ + m)
    return out

def accumulative_transposition(list, trans, iter):
    out = []
    temp_trans = trans
    for _ in list:
        out.append(_)
    for x in range(iter):
        if 0 < x:
            temp_trans = temp_trans + trans
        new = transpose(list, temp_trans)
        for _ in new:
            out.append(_)
    return out

def copied_transposition(motive, transpositions):
    out = []
    for _ in transpositions:
        new_list = transpose(motive, _)
        for x in new_list:
            out.append(x)
    return out
