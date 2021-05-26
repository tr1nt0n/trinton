import abjad


def make_pitches(pitch_list):
    out = []
    for _ in pitch_list:
        out.append abjad.namedpitch(_)
    return out
