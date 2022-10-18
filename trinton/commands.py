import abjad
import baca
import evans
import trinton
from abjadext import rmakers
from fractions import Fraction
import quicktions
import numpy
import datetime
import dataclasses
import typing
import pathlib
import os

# attachment functions


def attach(voice, leaves, attachment, direction=None):
    if direction is not None:
        if leaves == all:
            for leaf in abjad.select.leaves(voice, pitched=True):
                abjad.attach(attachment, leaf, direction=direction)
        else:
            for number in leaves:
                sel = abjad.select.leaf(voice, number)
                abjad.attach(attachment, sel, direction=direction)
    else:
        if leaves == all:
            for leaf in abjad.select.leaves(voice, pitched=True):
                abjad.attach(
                    attachment,
                    leaf,
                )
        else:
            for number in leaves:
                sel = abjad.select.leaf(voice, number)
                abjad.attach(
                    attachment,
                    sel,
                )


def attach_multiple(score, voice, attachments, leaves, direction=None):
    if direction is not None:
        for attachment in attachments:
            trinton.attach(
                voice=score[voice],
                leaves=leaves,
                attachment=attachment,
                direction=direction,
            )
    else:
        for attachment in attachments:
            trinton.attach(
                voice=score[voice],
                leaves=leaves,
                attachment=attachment,
            )


# notehead changers


def change_notehead(voice, leaves, notehead):
    if leaves == all:
        for _ in abjad.select.leaves(voice, pitched=True):
            abjad.tweak(_.note_head, rf"\tweak style #'{notehead}")
    else:
        for _ in leaves:
            abjad.tweak(
                abjad.select.leaf(voice, _).note_head, rf"\tweak style #'{notehead}"
            )


def pitched_notehead_change(voice, pitches, notehead):
    for leaf in abjad.select.leaves(voice, pitched=True):
        for pitch in pitches:
            if leaf.written_pitch.number == pitch:
                abjad.tweak(leaf.note_head).style = notehead


# barlines


def repeats(score, start_leaf, stop_leaf):
    trinton.attach(voice=score, leaves=start_leaf, attachment=abjad.BarLine(".|:"))

    trinton.attach(voice=score, leaves=stop_leaf, attachment=abjad.BarLine(":|."))


# accidentals


def transparent_accidentals(score, voice, leaves):
    if leaves == all:
        for leaf in abjad.select.leaves(score[voice], pitched=True):
            abjad.tweak(leaf.note_head, r"\tweak Accidental.transparent ##t")

    else:
        for leaf in leaves:
            sel = abjad.select.leaf(score[voice], leaf)
            abjad.tweak(sel.note_head, r"\tweak Accidental.transparent ##t")


def ficta(score, voice, start_ficta, stop_ficta):
    for (
        start,
        stop,
    ) in zip(start_ficta, stop_ficta):
        trinton.attach(
            voice=score[voice],
            leaves=[start],
            attachment=abjad.LilyPondLiteral(
                r"\set suggestAccidentals = ##t", "absolute_before"
            ),
        )

        trinton.attach(
            voice=score[voice],
            leaves=[stop],
            attachment=abjad.LilyPondLiteral(
                r"\set suggestAccidentals = ##f", "absolute_after"
            ),
        )


def respell(selections):
    for tie in abjad.select.logical_ties(selections):
        if tie[0].written_pitch.pitch_class == abjad.NamedPitchClass("bs"):
            abjad.iterpitches.respell_with_flats(tie)
        elif tie[0].written_pitch.pitch_class == abjad.NamedPitchClass("es"):
            abjad.iterpitches.respell_with_flats(tie)
        elif tie[0].written_pitch.pitch_class == abjad.NamedPitchClass("cf"):
            abjad.iterpitches.respell_with_sharps(tie)
        elif tie[0].written_pitch.pitch_class == abjad.NamedPitchClass("ff"):
            abjad.iterpitches.respell_with_sharps(tie)


# tuplets


def tuplet_brackets(score, all_staves):
    new_brackets = evans.NoteheadBracketMaker()

    for staff in all_staves:
        new_brackets(score[staff])


def reduce_tuplets(score, voice, tuplets):
    def numpy_gcd(a, b):
        a, b = numpy.broadcast_arrays(a, b)
        a = a.copy()
        b = b.copy()
        pos = numpy.nonzero(b)[0]
        while len(pos) > 0:
            b2 = b[pos]
            a[pos], b[pos] = b2, a[pos] % b2
            pos = pos[b[pos] != 0]
        return a

    if tuplets == "all":
        for tuplet in abjad.select.tuplets(score[voice]):
            multiplier = Fraction(tuplet.multiplier)
            num = multiplier.numerator
            den = multiplier.denominator
            tuple = (num, den)
            gcd = numpy_gcd(numpy.array([num]), numpy.array([den]))
            list = [int(_) / gcd for _ in tuple]
            tuple = (int(list[0][0]), int(list[1][0]))
            new_markup = rf"{tuple[1]}:{tuple[0]}"
            abjad.override(tuplet).TupletNumber.text = rf"\markup \italic {new_markup}"

    else:
        for tuplet in tuplets:
            tuplet = abjad.select.tuplet(score[voice], tuplet)
            multiplier = Fraction(tuplet.multiplier)
            num = multiplier.numerator
            den = multiplier.denominator
            tuple = (num, den)
            gcd = numpy_gcd(numpy.array([num]), numpy.array([den]))
            list = [int(_) / gcd for _ in tuple]
            tuple = (int(list[0][0]), int(list[1][0]))
            new_markup = rf"{tuple[1]}:{tuple[0]}"
            abjad.override(tuplet).TupletNumber.text = rf"\markup \italic {new_markup}"


def fuse_tuplet_rests(voice):
    for tuplet in abjad.select.tuplets(voice):
        rests = abjad.select.rests(tuplet)
        for rest_group in abjad.select.group_by_contiguity(rests):
            abjad.mutate.fuse(rest_group)


# tremoli


def unmeasured_stem_tremolo(selections):
    for leaf in selections:
        if leaf.written_duration == abjad.Duration(1, 64):
            abjad.attach(abjad.StemTremolo(512), leaf)

        elif leaf.written_duration == abjad.Duration(1, 32):
            abjad.attach(abjad.StemTremolo(256), leaf)

        elif leaf.written_duration == abjad.Duration(3, 32):
            abjad.attach(abjad.StemTremolo(256), leaf)

        elif leaf.written_duration == abjad.Duration(1, 16):
            abjad.attach(abjad.StemTremolo(128), leaf)

        elif leaf.written_duration == abjad.Duration(3, 16):
            abjad.attach(abjad.StemTremolo(64), leaf)

        elif leaf.written_duration == abjad.Duration(1, 8):
            abjad.attach(abjad.StemTremolo(64), leaf)

        elif leaf.written_duration == abjad.Duration(1, 4):
            abjad.attach(abjad.StemTremolo(32), leaf)

        elif leaf.written_duration == abjad.Duration(3, 8):
            abjad.attach(abjad.StemTremolo(32), leaf)

        elif leaf.written_duration == abjad.Duration(1, 2):
            abjad.attach(abjad.StemTremolo(32), leaf)

        elif leaf.written_duration == abjad.Duration(3, 4):
            abjad.attach(abjad.StemTremolo(32), leaf)

        elif leaf.written_duration == abjad.Duration(7, 8):
            abjad.attach(abjad.StemTremolo(32), leaf)

        elif leaf.written_duration == abjad.Duration(1, 1):
            abjad.attach(abjad.StemTremolo(32), leaf)

        elif leaf.written_duration == abjad.Duration(3, 2):
            abjad.attach(abjad.StemTremolo(32), leaf)

        elif leaf.written_duration == abjad.Duration(7, 4):
            abjad.attach(abjad.StemTremolo(32), leaf)

        elif leaf.written_duration == abjad.Duration(2, 1):
            abjad.attach(abjad.StemTremolo(32), leaf)


# glissandi


def glissando(score, voice, start_gliss, stop_gliss):
    for gliss1, gliss2 in zip(start_gliss, stop_gliss):
        leaves = list(range(gliss1, gliss2 + 1))
        sel = make_leaf_selection(score=score, voice=voice, leaves=leaves)
        abjad.glissando(
            sel,
            hide_middle_note_heads=True,
            allow_repeats=True,
            allow_ties=True,
        )


# beaming


def beam_runs_by_selection(score, voice, start_beam, stop_beam, beam_rests):
    selection = []
    for (
        start,
        stop,
    ) in zip(start_beam, stop_beam):
        sel = trinton.make_leaf_selection(
            score=score, voice=voice, leaves=list(range(start, stop + 1))
        )
        selection.append(sel)

    for sel in selection:
        abjad.beam(sel, beam_rests=beam_rests)


def unbeam_quarters(selections):
    for leaf1, leaf2, leaf3 in zip(
        selections, selections[1:], trinton.rotated_sequence(selections, -1)
    ):
        if leaf1.written_duration >= abjad.Duration(1, 4):
            abjad.detach(abjad.StartBeam, leaf1)
            abjad.detach(abjad.StopBeam, leaf1)
            if leaf2.written_duration < abjad.Duration(1, 4):
                abjad.attach(abjad.StartBeam(), leaf2)
            if leaf3.written_duration < abjad.Duration(1, 4):
                abjad.attach(abjad.StopBeam(), leaf3)


# rest measures


def whiteout_empty_staves(score, voice, cutaway):
    leaves = abjad.select.leaves(score[voice])
    shards = leaves.group_by_measure()
    for i, shard in enumerate(shards):
        if not all(isinstance(leaf, abjad.Rest) for leaf in shard):
            continue
        indicators = abjad.get.indicators(shard[0])
        multiplier = abjad.get.duration(shard) / 2
        invisible_rest = abjad.Rest(1, multiplier=(multiplier))
        rest_literal = abjad.LilyPondLiteral(
            r"\once \override Rest.transparent = ##t", "before"
        )
        abjad.attach(
            rest_literal, invisible_rest, tag=abjad.Tag("applying invisibility")
        )
        for indicator in indicators:
            abjad.attach(
                indicator, invisible_rest, tag=abjad.Tag("applying indicators")
            )
        multimeasure_rest = abjad.MultimeasureRest(1, multiplier=(multiplier))
        start_command = abjad.LilyPondLiteral(
            r"\stopStaff \once \override Staff.StaffSymbol.line-count = #1 \startStaff",
            "before",
        )
        stop_command = abjad.LilyPondLiteral(r"\stopStaff \startStaff", "after")
        if cutaway == True:
            abjad.attach(
                start_command, invisible_rest, tag=abjad.Tag("applying cutaway")
            )
            abjad.attach(
                stop_command,
                multimeasure_rest,
                tag=abjad.Tag("applying cutaway"),
            )
            both_rests = [invisible_rest, multimeasure_rest]
            abjad.mutate.replace(shard, both_rests[:])
        else:
            both_rests = [invisible_rest, multimeasure_rest]
            abjad.mutate.replace(shard, both_rests[:])


def fill_empty_staves_with_skips(voice):
    leaves = abjad.select.leaves(voice)
    shards = abjad.select.group_by_measure(leaves)
    for i, shard in enumerate(shards):
        if not all(isinstance(leaf, abjad.Rest) for leaf in shard):
            continue
        indicators = abjad.get.indicators(shard[0])
        multiplier = abjad.get.duration(shard)
        invisible_rest = abjad.Rest(1, multiplier=(multiplier))
        rest_literal = abjad.LilyPondLiteral(
            r"\once \override Rest.transparent = ##t", "before"
        )
        abjad.attach(
            rest_literal, invisible_rest, tag=abjad.Tag("applying invisibility")
        )
        for indicator in indicators:
            abjad.attach(
                indicator, invisible_rest, tag=abjad.Tag("applying indicators")
            )

        both_rests = [invisible_rest]
        abjad.mutate.replace(shard, invisible_rest)


# multiphonics


def write_multiphonics(score, voice, dict, leaves, multiphonic, markup):
    pair = dict[multiphonic]
    pitch_list, string = pair
    handler = evans.PitchHandler(pitch_list=pitch_list, forget=False)
    if markup is True:
        for leaf in leaves:
            sel = abjad.select.leaf(score[voice], leaf)
            handler(sel)
            markup = abjad.Markup(
                string,
            )
            trinton.attach(
                voice=score[voice], leaves=[leaf], attachment=markup, direction=abjad.UP
            )
    else:
        for leaf in leaves:
            sel = abjad.select.leaf(score[voice], leaf)
            handler(sel)
