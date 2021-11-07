import abjad
import evans
import trinton
import random

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

def reduceMod(l, m):
    out = []
    for _ in l:
        out.append(_ % m)
    return out

def accumulative_transposition(list, trans, iter):
    out = []
    temp_trans = trans
    for _ in list:
        out.append(_)
    for x in range(iter):
        if 0 < x:
            temp_trans = temp_trans + trans
        new = trinton.transpose(list, temp_trans)
        for _ in new:
            out.append(_)
    return out

def copied_transposition(motive, transpositions):
    out = []
    for _ in transpositions:
        new_list = trinton.transpose(motive, _)
        for x in new_list:
            out.append(x)
    return out

def random_walk(chord, seed):
    random.seed(seed)
    random_walk = []
    random_walk.append(-1 if random.random() < 0.5 else 1)
    for i in range(1, 60):
        movement = -1 if random.random() < 0.5 else 1
        value = random_walk[i - 1] + movement
        random_walk.append(value)
    random_walk = [abs(x) for x in random_walk]
    notes = [
        chord[x] for x in trinton.reduceMod(random_walk, len(chord))
    ]
    return notes

def consecutive_multiplication(notes, mult):
    if isinstance(mult, (int, float)):
        multipliers = [mult for _ in range(len(notes))]
    else:
        multipliers = mult
        try:
            assert len(mult) == len(notes)
        except:
            print("WARNING: length of notes must equal length of mult.")
            return
    pc_set = [a*b for a, b in zip(notes, multipliers)]
    return pc_set

def rotated_sequence(pitch_list, start_index):
    result = []
    rotated_list = pitch_list[start_index:] + pitch_list[:start_index]
    for pitch in rotated_list:
        result.append(pitch)
    return result

def countList(lst1, lst2):
    return [sub[item] for item in range(len(lst2))
    for sub in [lst1, lst2]]

def durational_pitch_association(score, voice, selection, durations, pitch_lists, forget):
    for duration, pitch_list in zip(durations, pitch_lists):
        for leaf in selection:
            if leaf.written_duration == duration:
                container.append(leaf)
            else:
                pass

        handler = evans.PitchHandler(
            pitch_list=pitch_list,
            forget=forget,
        )
        handler(container)

        score[voice].append(container)
