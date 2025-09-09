import abjad
import baca
import evans
import trinton
from trinton import selectors
from abjadext import rmakers
from fractions import Fraction
from itertools import cycle
import quicktions
import numpy
import datetime
import dataclasses
import typing
import pathlib
import os

# attachment functions


def attach(voice, leaves, attachment, direction=None, tag=None):
    if direction is not None:
        if leaves == all:
            for leaf in abjad.select.leaves(voice, pitched=True):
                abjad.attach(attachment, leaf, direction=direction, tag=tag)
        else:
            for number in leaves:
                sel = abjad.select.leaf(voice, number)
                abjad.attach(attachment, sel, direction=direction, tag=tag)
    else:
        if leaves == all:
            for leaf in abjad.select.leaves(voice, pitched=True):
                abjad.attach(attachment, leaf, tag=tag)
        else:
            for number in leaves:
                sel = abjad.select.leaf(voice, number)
                abjad.attach(attachment, sel, tag=tag)


def attach_multiple(score, voice, attachments, leaves, direction=None, tag=None):
    if direction is not None:
        for attachment in attachments:
            trinton.attach(
                voice=score[voice],
                leaves=leaves,
                attachment=attachment,
                direction=direction,
                tag=tag,
            )
    else:
        for attachment in attachments:
            trinton.attach(
                voice=score[voice], leaves=leaves, attachment=attachment, tag=tag
            )


def attachment_command(attachments, selector, direction=None, tag=None):
    def command(argument):
        selections = selector(argument)
        for selection in selections:
            for attachment in attachments:
                abjad.attach(attachment, selection, direction=direction, tag=tag)

    return command


def linear_attachment_command(attachments, selector, direction=None, tag=None):
    def command(argument):
        selections = selector(argument)
        for selection, attachment in zip(selections, attachments):
            abjad.attach(attachment, selection, direction=direction, tag=tag)

    return command


def detach_command(detachments, selector):
    def command(argument):
        selections = selector(argument)
        for selection in selections:
            for detachment in detachments:
                abjad.detach(
                    detachment,
                    selection,
                )

    return command


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


def artificial_harmonics(selector=selectors.pleaves()):
    def change_noteheads(argument):
        selections = selector(argument)
        for leaf in selections:
            if isinstance(leaf, abjad.Chord) is False:
                pass

            else:
                noteheads = leaf.note_heads
                abjad.tweak(noteheads[1], rf"\tweak style #'harmonic")

    return change_noteheads


def pitched_notehead_change(voice, pitches, notehead):
    for leaf in abjad.select.leaves(voice, pitched=True):
        for pitch in pitches:
            if leaf.written_pitch.number == pitch:
                abjad.tweak(leaf.note_head, rf"\tweak style #'{notehead}")


def change_notehead_command(notehead, selector=selectors.pleaves()):
    def change(argument):
        selections = selector(argument)
        leaves = abjad.select.leaves(selections, pitched=True)
        _overrides = {
            "highest": r"\once \override NoteHead.stencil = #(lambda (grob) (let ((dur (ly:grob-property grob 'duration-log))) (if (= dur 0) (grob-interpret-markup grob (markup #:ekmelos-char #xe0bb)) (if (= dur 1) (grob-interpret-markup grob (markup #:ekmelos-char #xe0bc)) (if (> dur 1) (grob-interpret-markup grob (markup #:ekmelos-char #xe0be)))))))",
            "lowest": r"\once \override NoteHead.stencil = #(lambda (grob) (let ((dur (ly:grob-property grob 'duration-log))) (if (= dur 0) (grob-interpret-markup grob (markup #:ekmelos-char #xe0c4)) (if (= dur 1) (grob-interpret-markup grob (markup #:ekmelos-char #xe0c5)) (if (> dur 1) (grob-interpret-markup grob (markup #:ekmelos-char #xe0c7)))))))",
            "cluster": [
                r"\once \override NoteHead.X-offset = 0",
                r"\once \override Staff.Accidental.stencil = ##f",
                r"\once \override Staff.Glissando.thickness = #8.25",
                r"\once \override NoteHead.duration-log = 2",
            ],
        }

        if notehead == "highest" or notehead == "lowest" or notehead == "cluster":
            notehead_literal = abjad.LilyPondLiteral(_overrides[notehead], "before")
            if notehead == "cluster":
                for leaf in leaves:
                    for head in leaf.note_heads:
                        abjad.tweak(head, r"\tweak style #'la")
                    abjad.attach(notehead_literal, leaf)

            if notehead == "highest" or notehead == "lowest":
                stem_literal = abjad.LilyPondLiteral(
                    r"\once \override NoteHead.stem-attachment = #'(0 . 0.75)"
                )

                ledger_literal = abjad.LilyPondLiteral(
                    r"\once \override NoteHead.no-ledgers = ##t"
                )

                accidental_literal = abjad.LilyPondLiteral(
                    r"\once \override Staff.AccidentalPlacement.right-padding = #0.6"
                )

                literals = [
                    stem_literal,
                    ledger_literal,
                    notehead_literal,
                    accidental_literal,
                ]

                for leaf in leaves:
                    for literal in literals:
                        abjad.attach(literal, leaf)

        else:
            for leaf in leaves:
                if isinstance(leaf, abjad.Chord):
                    for head in leaf.note_heads:
                        abjad.tweak(head, rf"\tweak style #'{notehead}")
                else:
                    abjad.tweak(leaf.note_head, rf"\tweak style #'{notehead}")

    return change


def parenthesize_notehead_command(selector=abjad.select.chords, head_indices=[0]):
    def parenthesize(argument):
        selections = selector(argument)

        for chord, head_index in zip(selections, head_indices):
            note_heads = chord.note_heads
            relevant_head = note_heads[head_index]
            relevant_head.is_parenthesized = True

    return parenthesize


def noteheads_only(
    selector=selectors.pleaves(), stem=False, duration_log="2", no_ledgers=False
):
    def only_noteheads(argument):
        selections = selector(argument)
        logical_ties = abjad.select.logical_ties(selections, pitched=True)
        literal_strings = [
            r"\once \override RepeatTie.transparent = ##t",
            r"\once \override Beam.stencil = ##f",
            r"\once \override Flag.stencil = ##f",
            r"\once \override Dots.stencil = ##f",
            r"\once \override Tie.stencil = ##f",
            rf"\once \override NoteHead.duration-log = {duration_log}",
        ]

        if no_ledgers is True:
            literal_strings.append(r"\once \override NoteHead.no-ledgers = ##t")

        if stem is False:
            literal_strings.append(r"\once \override Stem.stencil = ##f")

        for leaf in selections:
            abjad.attach(
                abjad.LilyPondLiteral(
                    literal_strings,
                    site="before",
                ),
                leaf,
            )
        for tie in logical_ties:
            relevant_leaves = abjad.select.exclude(abjad.select.leaves(tie), [0])
            for leaf in relevant_leaves:
                abjad.override(leaf).NoteHead.transparent = True
                abjad.attach(
                    abjad.LilyPondLiteral(
                        [
                            r"\once \override NoteHead.no-ledgers = ##t",
                        ],
                        site="before",
                    ),
                    leaf,
                )

    return only_noteheads


def transparent_noteheads(selector):
    def transparent(argument):
        selections = selector(argument)
        for leaf in abjad.select.leaves(selections):
            abjad.override(leaf).NoteHead.transparent = True
            abjad.attach(
                abjad.LilyPondLiteral(
                    r"\once \override NoteHead.no-ledgers = ##t", "before"
                ),
                leaf,
            )
            abjad.attach(
                abjad.LilyPondLiteral(
                    r"\once \override Accidental.stencil = ##f", "before"
                ),
                leaf,
            )

    return transparent


# barlines


def repeats(score, start_leaf, stop_leaf):
    trinton.attach(voice=score, leaves=start_leaf, attachment=abjad.BarLine(".|:"))

    trinton.attach(voice=score, leaves=stop_leaf, attachment=abjad.BarLine(":|."))


def change_lines(
    lines,
    selector=selectors.select_leaves_by_index([0], pitched=True),
    clef="treble",
    invisible_barlines=True,
    tag=abjad.Tag("+SCORE"),
):
    def change(argument):

        selections = selector(argument)
        for selection in selections:
            abjad.attach(abjad.Clef(clef), selection)
            if invisible_barlines is True:
                if lines == 1:
                    abjad.attach(
                        abjad.LilyPondLiteral(
                            r"\override Staff.BarLine.bar-extent = #'(-0.01 . 0.01)",
                            site="before",
                        ),
                        selection,
                        tag=tag,
                    )
                else:
                    abjad.attach(
                        abjad.LilyPondLiteral(
                            r"\revert Staff.BarLine.bar-extent", site="before"
                        ),
                        selection,
                        tag=tag,
                    )
            abjad.attach(
                abjad.LilyPondLiteral(
                    rf"\staff-line-count {lines}",
                    site="absolute_before",
                ),
                selection,
            )

    return change


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


def ficta_command(selector):
    def suggest(argument):
        selections = selector(argument)
        it = iter(selections)

        tups = [*zip(it, it)]

        for tup in tups:
            abjad.attach(
                abjad.LilyPondLiteral(
                    r"\set suggestAccidentals = ##t", "absolute_before"
                ),
                tup[0],
            )
            abjad.attach(
                abjad.LilyPondLiteral(
                    r"\set suggestAccidentals = ##f", "absolute_after"
                ),
                tup[1],
            )

    return suggest


def vertical_accidentals(selector, direction=None):
    def suggest(argument):
        selections = selector(argument)
        ties = abjad.select.logical_ties(selections, pitched=True)
        for tie in ties:
            first_leaf = tie[0]
            abjad.attach(
                abjad.LilyPondLiteral(
                    r"\once \override Staff.Accidental.stencil = ##f", site="before"
                ),
                first_leaf,
            )
            if isinstance(first_leaf, abjad.Note):
                first_leaf_pitch = first_leaf.written_pitch
                accidental = first_leaf_pitch.accidental
                accidental_name = accidental.name
                if accidental_name == "quarter sharp":
                    accidental_name = "quarter-sharp"
                if accidental_name == "quarter flat":
                    accidental_name = "quarter-flat"

                abjad.attach(
                    abjad.Articulation(f"{accidental_name}-articulation"),
                    first_leaf,
                    direction=direction,
                )

            if isinstance(first_leaf, abjad.Chord):
                note_heads = first_leaf.note_heads
                for note_head in note_heads:
                    pitch = note_head.written_pitch
                    accidental = pitch.accidental
                    accidental_name = accidental.name
                    if accidental_name == "quarter sharp":
                        accidental_name = "quarter-sharp"
                    if accidental_name == "quarter flat":
                        accidental_name = "quarter-flat"
                    abjad.attach(
                        abjad.Articulation(f"{accidental_name}-articulation"),
                        first_leaf,
                        direction=direction,
                    )

    return suggest


def respell_accidentals_command(selector):
    def respell(argument):
        selections = selector(argument)
        for tie in abjad.select.logical_ties(selections):
            if isinstance(tie[0], abjad.Chord):
                note_heads = tie[0].note_heads
                for head in note_heads:
                    if head.written_pitch.pitch_class == abjad.NamedPitchClass("bff"):
                        abjad.iterpitches.respell_with_sharps(tie)
                    if head.written_pitch.pitch_class == abjad.NamedPitchClass("bs"):
                        abjad.iterpitches.respell_with_flats(tie)
                    if head.written_pitch.pitch_class == abjad.NamedPitchClass("es"):
                        abjad.iterpitches.respell_with_flats(tie)
                    if head.written_pitch.pitch_class == abjad.NamedPitchClass("cf"):
                        abjad.iterpitches.respell_with_sharps(tie)
                    if head.written_pitch.pitch_class == abjad.NamedPitchClass("ff"):
                        abjad.iterpitches.respell_with_sharps(tie)
                    if head.written_pitch.pitch_class == abjad.NamedPitchClass("fss"):
                        abjad.iterpitches.respell_with_flats(tie)
                    if head.written_pitch.pitch_class == abjad.NamedPitchClass("eff"):
                        abjad.iterpitches.respell_with_sharps(tie)
            else:
                if tie[0].written_pitch.pitch_class == abjad.NamedPitchClass("bff"):
                    abjad.iterpitches.respell_with_sharps(tie)
                if tie[0].written_pitch.pitch_class == abjad.NamedPitchClass("bs"):
                    abjad.iterpitches.respell_with_flats(tie)
                if tie[0].written_pitch.pitch_class == abjad.NamedPitchClass("es"):
                    abjad.iterpitches.respell_with_flats(tie)
                if tie[0].written_pitch.pitch_class == abjad.NamedPitchClass("cf"):
                    abjad.iterpitches.respell_with_sharps(tie)
                if tie[0].written_pitch.pitch_class == abjad.NamedPitchClass("ff"):
                    abjad.iterpitches.respell_with_sharps(tie)
                if tie[0].written_pitch.pitch_class == abjad.NamedPitchClass("fss"):
                    abjad.iterpitches.respell_with_flats(tie)
                if tie[0].written_pitch.pitch_class == abjad.NamedPitchClass("eff"):
                    abjad.iterpitches.respell_with_sharps(tie)

    return respell


def respell_with_sharps(selector):
    def respell(argument):
        selections = selector(argument)
        for selection in selections:
            abjad.iterpitches.respell_with_sharps(selection)

    return respell


def respell_with_flats(selector):
    def respell(argument):
        selections = selector(argument)
        for selection in selections:
            abjad.iterpitches.respell_with_flats(selection)

    return respell


def force_accidentals(voice, selector):
    selections = selector(voice)
    for tie in abjad.select.logical_ties(selections, pitched=True):
        if isinstance(tie[0], abjad.Chord):
            for head in tie[0].note_heads:
                head.is_forced = True
        else:
            tie[0].note_head.is_forced = True


def force_accidentals_command(selector, after_ties=False):
    def force(argument):
        selections = selector(argument)
        if after_ties is True:
            selections = abjad.select.leaves(selections, pitched=True)
        else:
            selections = abjad.select.logical_ties(selections, pitched=True)

        for sel in selections:
            if isinstance(sel, abjad.LogicalTie):
                leaf = sel[0]
            else:
                leaf = sel

            if isinstance(leaf, abjad.Chord):
                for head in leaf.note_heads:
                    head.is_forced = True
            else:
                leaf.note_head.is_forced = True

    return force


def invisible_accidentals_command(selector=selectors.pleaves()):
    def invisible(argument):
        selections = selector(argument)

        for selection in selections:
            abjad.attach(
                abjad.LilyPondLiteral(
                    r"\once \override Accidental.stencil = ##f", "before"
                ),
                selection,
            )

    return invisible


# tuplets


class NoteheadBracketMaker:
    r"""
    Writes tuplet brackets with inserted note head.

    .. container:: example

        >>> tuplet = abjad.Tuplet((3, 2), "cs'8 d'8")
        >>> tuplet_2 = abjad.Tuplet((2, 3), components=[abjad.Note(0, (3, 8)), tuplet])
        >>> staff = abjad.Staff()
        >>> staff.append(tuplet_2)
        >>> staff.extend([abjad.Note("c'4"), abjad.Note("cs'8"), abjad.Note("d'8")])
        >>> new_brackets = evans.NoteheadBracketMaker()
        >>> new_brackets(staff)
        >>> score = abjad.Score([staff])
        >>> moment = "#(ly:make-moment 1 25)"
        >>> abjad.setting(score).proportional_notation_duration = moment
        >>> file = abjad.LilyPondFile(
        ...     items=[
        ...         "#(set-default-paper-size \"a4\" \'portrait)",
        ...         r"#(set-global-staff-size 16)",
        ...         "\\include \'Users/gregoryevans/abjad/abjad/scm/abjad.ily\'",
        ...         score,
        ...     ],
        ... )
        ...
        >>> abjad.show(file) # doctest: +SKIP

        .. docs::

            >>> print(abjad.lilypond(staff))
            \new Staff
            {
                \tweak TupletNumber.text #(tuplet-number::append-note-wrapper(tuplet-number::non-default-tuplet-fraction-text 3 2) (ly:make-duration 2 0))
                \times 2/3
                {
                    c'4.
                    \tweak text #tuplet-number::calc-fraction-text
                    \tweak TupletNumber.text #(tuplet-number::append-note-wrapper(tuplet-number::non-default-tuplet-fraction-text 2 3) (ly:make-duration 3 0))
                    \times 3/2
                    {
                        cs'8
                        d'8
                    }
                }
                c'4
                cs'8
                d'8
            }

    """

    def __call__(self, selections):
        return self._transform_brackets(selections)

    def __str__(self):
        return f"<{type(self).__name__}()>"

    def __repr__(self):
        return f"<{type(self).__name__}()>"

    def _assemble_notehead(self, head_dur):
        duration_map = {
            "1": "0",
            "2": "1",
            "4": "2",
            "8": "3",
            "16": "4",
            "32": "5",
            "64": "6",
            "128": "7",
            "256": "8",
            "512": "9",
        }
        pair = head_dur.pair
        dot_parts = []
        while 1 < pair[0]:
            dot_part = (1, pair[1])
            dot_parts.append(dot_part)
            head_dur -= abjad.Duration(dot_part)
            pair = head_dur.pair
        duration_string = duration_map[f"{pair[1]}"]
        dot_string = ""
        # for _ in dot_parts:
        #     dot_string += "."

        return duration_string, len(dot_string)

    def _transform_brackets(self, selections):
        for tuplet in abjad.select.tuplets(selections):
            rests = abjad.select.rests(tuplet)
            for rest_group in abjad.select.group_by_contiguity(rests):
                parental_groups = abjad.select.group_by(
                    rest_group, predicate=lambda _: abjad.get.parentage(_).parent
                )
                for parental_group in parental_groups:
                    abjad.mutate.fuse(parental_group)
            inner_durs = []
            for _ in tuplet[:]:
                if isinstance(_, abjad.Tuplet):
                    inner_durs.append(_.multiplied_duration)
                else:
                    inner_durs.append(_.written_duration)
            tuplet_dur = sum(inner_durs)
            colon_string = tuplet.colon_string
            parsed_colon_string = colon_string.split(":")
            colon_string_pair = (parsed_colon_string[0], parsed_colon_string[-1])
            imp_num, imp_den = colon_string_pair
            head_dur = tuplet_dur / float(imp_num)
            dur_pair = self._assemble_notehead(head_dur)
            abjad.tweak(
                tuplet,
                rf"\tweak TupletNumber.text #(tuplet-number::append-note-wrapper(tuplet-number::non-default-tuplet-fraction-text {imp_num} {imp_den}) (ly:make-duration {dur_pair[0]} {dur_pair[1]}))",
            )


def tuplet_brackets(score, all_staves):
    new_brackets = evans.NoteheadBracketMaker()

    for staff in all_staves:
        new_brackets(score[staff])


def notehead_bracket_command(selector=None):
    def call_handler(argument):
        handler = NoteheadBracketMaker()
        if selector is not None:
            selections = selector(argument)
            handler(selections)

        else:
            handler(argument)

    return call_handler


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


def fuse_tuplet_rests_command():
    def fuse(argument):
        fuse_tuplet_rests(argument)

    return fuse


def invisible_tuplet_brackets(selector=None):
    def command(argument):
        if selector is None:
            selections = abjad.select.tuplets(argument)
        else:
            selections = selector(argument)
        for tuplet in selections:
            abjad.attach(
                abjad.LilyPondLiteral(
                    "\once \override TupletBracket.stencil = ##f", "before"
                ),
                tuplet,
            )
            abjad.attach(
                abjad.LilyPondLiteral(
                    "\once \override TupletNumber.stencil = ##f", "before"
                ),
                tuplet,
            )

    return command


# tremoli


def unmeasured_stem_tremolo(selections, direction=None):
    for leaf in selections:
        if leaf.written_duration == abjad.Duration(1, 64):
            abjad.attach(abjad.StemTremolo(512), leaf)

        elif leaf.written_duration == abjad.Duration(1, 32):
            abjad.attach(abjad.StemTremolo(256), leaf)

        elif leaf.written_duration == abjad.Duration(3, 64):
            abjad.attach(abjad.StemTremolo(256), leaf)

        elif leaf.written_duration == abjad.Duration(7, 64):
            abjad.attach(abjad.StemTremolo(128), leaf)

        elif leaf.written_duration == abjad.Duration(3, 32):
            abjad.attach(abjad.StemTremolo(128), leaf)

        elif leaf.written_duration == abjad.Duration(1, 16):
            abjad.attach(abjad.StemTremolo(128), leaf)

        elif leaf.written_duration == abjad.Duration(3, 16):
            abjad.attach(abjad.StemTremolo(64), leaf)

        elif leaf.written_duration == abjad.Duration(7, 32):
            abjad.attach(abjad.StemTremolo(64), leaf)

        elif leaf.written_duration == abjad.Duration(1, 8):
            abjad.attach(abjad.StemTremolo(64), leaf)

        elif leaf.written_duration >= abjad.Duration(1, 4):
            abjad.attach(abjad.StemTremolo(32), leaf)

        if direction is not None:
            abjad.attach(
                abjad.LilyPondLiteral(
                    rf"\once \override Staff.StemTremolo.direction = #{direction}",
                    site="before",
                ),
                leaf,
            )


def tremolo_lines(selector, lines):
    _lines_to_multiplier = {
        1: 4,
        2: 8,
        3: 16,
    }

    def tremolo(argument):
        selections = selector(argument)
        for leaf, line_ammount in zip(selections, lines):
            duration = leaf.written_duration
            string = duration.lilypond_duration_string
            denominator = int(string[0])
            abjad.attach(
                abjad.StemTremolo(denominator * _lines_to_multiplier[line_ammount]),
                leaf,
            )

    return tremolo


def tremolo_command(selector=selectors.pleaves(), direction=None):
    def trem(argument):
        selections = selector(argument)
        for selection in selections:
            if isinstance(selection, abjad.LogicalTie):
                for leaf in abjad.select.leaves(selection):
                    unmeasured_stem_tremolo([leaf], direction=direction)
            else:
                unmeasured_stem_tremolo([selection], direction=direction)

    return trem


# glissandi


def glissando(score, voice, start_gliss, stop_gliss):
    for gliss1, gliss2 in zip(start_gliss, stop_gliss):
        leaves = list(range(gliss1, gliss2 + 1))
        sel = trinton.make_leaf_selection(score=score, voice=voice, leaves=leaves)
        abjad.glissando(
            sel,
            hide_middle_note_heads=True,
            allow_repeats=True,
            allow_ties=True,
        )


def glissando_command(selector, tweaks=[], zero_padding=False, no_ties=False):
    def command(argument):
        selections = selector(argument)
        for selection in selections:
            abjad.glissando(
                selection,
                *tweaks,
                hide_middle_note_heads=True,
                allow_repeats=True,
                allow_ties=True,
                zero_padding=zero_padding,
            )
            middle_leaves = abjad.select.exclude(selection, [0, -1])
            all_but_last_leaf = abjad.select.exclude(selection, [-1])
            for leaf in middle_leaves:
                abjad.attach(
                    abjad.LilyPondLiteral(
                        r"\once \override Dots.staff-position = #2", "before"
                    ),
                    leaf,
                )
            if no_ties is True:
                for leaf in all_but_last_leaf:
                    abjad.detach(abjad.Tie, leaf)

    return command


def continuous_glissando(
    selector=trinton.selectors.logical_ties(),
    no_ties=False,
    tweaks=None,
    zero_padding=False,
    invisible_center=False,
    slur=False,
):
    def glissando(argument):
        selections = selector(argument)
        selections = abjad.select.logical_ties(selections, pitched=True)
        glissando_groups = abjad.select.group_by_contiguity(selections)

        for group in glissando_groups:
            if slur is True:
                abjad.slur(group)

            if zero_padding is True:
                abjad.attach(
                    abjad.LilyPondLiteral(
                        r"\override Dots.staff-position = #2", site="absolute_before"
                    ),
                    abjad.select.leaf(group, 0),
                )

                abjad.attach(
                    abjad.LilyPondLiteral(
                        r"\revert Dots.staff-position", site="before"
                    ),
                    abjad.select.leaf(group, -1),
                )

            group = abjad.select.exclude(abjad.select.logical_ties(group), [-1])

            if invisible_center is True:
                abjad.attach(
                    abjad.LilyPondLiteral(
                        [
                            r"\override NoteHead.X-extent = #'(0 . 0)",
                            r"\override NoteHead.transparent = ##t",
                        ],
                        site="before",
                    ),
                    abjad.select.leaf(group, 1),
                )

                abjad.attach(
                    abjad.LilyPondLiteral(
                        [r"\revert NoteHead.X-extent", r"\revert NoteHead.transparent"],
                        site="absolute_after",
                    ),
                    abjad.select.leaf(group, -1),
                )

            singletons = []
            multiples = []

            for tie in abjad.select.logical_ties(group):
                if len(tie) > 1:
                    multiples.append(tie)

                else:
                    singletons.append(tie)

            singleton_gliss = abjad.Glissando(zero_padding=zero_padding)

            if tweaks is not None:
                for tweak in tweaks:
                    singleton_gliss = abjad.bundle(singleton_gliss, tweak)

            for tie in singletons:
                abjad.attach(singleton_gliss, tie[0])

            for tie in multiples:
                glissando_group = abjad.select.with_next_leaf(tie)

                if tweaks is not None:
                    abjad.glissando(
                        glissando_group,
                        *tweaks,
                        hide_middle_note_heads=True,
                        allow_repeats=True,
                        allow_ties=True,
                        zero_padding=zero_padding,
                    )

                else:
                    abjad.glissando(
                        glissando_group,
                        hide_middle_note_heads=True,
                        allow_repeats=True,
                        allow_ties=True,
                        zero_padding=zero_padding,
                    )

                if no_ties is True:
                    for leaf in tie:
                        abjad.detach(abjad.Tie, leaf)

    return glissando


# beaming


def manual_beam_positions(positions, selector=abjad.select.leaves):
    def beaming(argument):
        selections = selector(argument)
        leaves = abjad.select.leaves(selections)
        start_beam_leaves = []

        for leaf in leaves:
            if abjad.get.has_indicator(leaf, abjad.StartBeam):
                start_beam_leaves.append(leaf)

        for start_beam_leaf in start_beam_leaves:
            start_beam = abjad.get.indicator(start_beam_leaf, abjad.StartBeam)

            start_beam = abjad.bundle(
                start_beam,
                rf"- \tweak Beam.positions #'({positions[0]} . {positions[-1]})",
            )

            abjad.detach(abjad.StartBeam, start_beam_leaf)

            abjad.attach(start_beam, start_beam_leaf)

    return beaming


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


def beam_durations(divisions, beam_rests=False, preprolated=True):
    def func(selections):
        selections = abjad.select.leaves(selections)

        durations = cycle([abjad.Duration(_) for _ in divisions])

        new_durations = []

        for _, duration in zip(range(len(selections)), durations):
            new_durations.append(duration)

        group = []

        for leaf in selections:
            group.append(leaf)

            if abjad.get.duration(group, preprolated=preprolated) == new_durations[0]:
                rmakers.unbeam(group)
                abjad.beam(group, beam_rests=beam_rests)
                group.clear()
                new_durations.pop(0)

        abjad.beam(group, beam_rests=beam_rests)

    return func


def _matches_pitch(pitched_leaf, pitch_object):
    if isinstance(pitch_object, baca.Coat):
        pitch_object = pitch_object.argument
    if pitch_object is None:
        return False
    if isinstance(pitched_leaf, abjad.Note):
        written_pitches = [pitched_leaf.written_pitch]
    elif isinstance(pitched_leaf, abjad.Chord):
        written_pitches = pitched_leaf.written_pitches
    else:
        raise TypeError(pitched_leaf)
    if isinstance(pitch_object, int | float):
        source = [_.number for _ in written_pitches]
    elif isinstance(pitch_object, abjad.NamedPitch):
        source = written_pitches
    elif isinstance(pitch_object, abjad.NumberedPitch):
        source = [abjad.NumberedPitch(_) for _ in written_pitches]
    elif isinstance(pitch_object, abjad.NamedPitchClass):
        source = [abjad.NamedPitchClass(_) for _ in written_pitches]
    elif isinstance(pitch_object, abjad.NumberedPitchClass):
        source = [abjad.NumberedPitchClass(_) for _ in written_pitches]
    else:
        raise TypeError(f"unknown pitch object: {pitch_object!r}.")
    # if not type(source[0]) is type(pitch_object):
    #     raise TypeError(f"{source!r} type must match {pitch_object!r}.")
    return pitch_object in source


def _do_imbrication(
    container: abjad.Container,
    segment: list,
    voice_name: str,
    *commands,
    allow_unused_pitches: bool = False,
    by_pitch_class: bool = False,
    hocket: bool = False,
    truncate_ties: bool = False,
) -> dict[str, list]:
    original_container = container
    container = baca.copy.deepcopy(container)
    abjad.override(container).TupletBracket.stencil = False
    abjad.override(container).TupletNumber.stencil = False
    segment = abjad.sequence.flatten(segment, depth=-1)
    if by_pitch_class:
        segment = [abjad.NumberedPitchClass(_) for _ in segment]
    cursor = baca.Cursor(singletons=True, source=segment, suppress_exception=True)
    pitch_number = cursor.next()
    original_logical_ties = abjad.select.logical_ties(original_container)
    logical_ties = abjad.select.logical_ties(container)
    pairs = zip(logical_ties, original_logical_ties)
    for logical_tie, original_logical_tie in pairs:
        if isinstance(logical_tie.head, abjad.Rest):
            for leaf in logical_tie:
                duration = leaf.written_duration
                skip = abjad.Skip(duration)
                abjad.mutate.replace(leaf, [skip])
        elif isinstance(logical_tie.head, abjad.Skip):
            pass
        elif _matches_pitch(logical_tie.head, pitch_number):
            if isinstance(pitch_number, baca.Coat):
                for leaf in logical_tie:
                    duration = leaf.written_duration
                    skip = abjad.Skip(duration)
                    abjad.mutate.replace(leaf, [skip])
                pitch_number = cursor.next()
                continue
            baca.figures._trim_matching_chord(logical_tie, pitch_number)
            pitch_number = cursor.next()
            if truncate_ties:
                head = logical_tie.head
                tail = logical_tie.tail
                for leaf in logical_tie[1:]:
                    duration = leaf.written_duration
                    skip = abjad.Skip(duration)
                    abjad.mutate.replace(leaf, [skip])
                abjad.detach(abjad.Tie, head)
                next_leaf = abjad.get.leaf(tail, 1)
                if next_leaf is not None:
                    abjad.detach(abjad.RepeatTie, next_leaf)
            if hocket:
                for leaf in original_logical_tie:
                    duration = leaf.written_duration
                    skip = abjad.Skip(duration)
                    abjad.mutate.replace(leaf, [skip])
        else:
            for leaf in logical_tie:
                duration = leaf.written_duration
                skip = abjad.Skip(duration)
                abjad.mutate.replace(leaf, [skip])
    if not allow_unused_pitches and not cursor.is_exhausted:
        assert cursor.position is not None
        current, total = cursor.position - 1, len(cursor)
        raise Exception(f"{cursor!r} used only {current} of {total} pitches.")
    for command in commands:
        command(container)
    selection = [container]
    if not hocket:
        pleaves = baca.select.pleaves(container)
        assert isinstance(pleaves, list)
        for pleaf in pleaves:
            abjad.attach(baca.enums.ALLOW_OCTAVE, pleaf)
    return {voice_name: selection}


def imbricate(
    container: abjad.Container,
    voice_name: str,
    segment: list,
    *specifiers: typing.Any,
    allow_unused_pitches: bool = False,
    by_pitch_class: bool = False,
    hocket: bool = False,
    truncate_ties: bool = False,
) -> dict[str, list]:
    return _do_imbrication(
        container,
        segment,
        voice_name,
        *specifiers,
        allow_unused_pitches=allow_unused_pitches,
        by_pitch_class=by_pitch_class,
        hocket=hocket,
        truncate_ties=truncate_ties,
    )


def imbrication(
    selections,
    pitches,
    name,
    *,
    direction=abjad.UP,
    articulation=None,
    beam=False,
    secondary=False,
    allow_unused_pitches=False,
    by_pitch_class=False,
    hocket=False,
    truncate_ties=False,
):
    def _find_parent(selections):
        first_leaf = abjad.select.leaf(selections, 0)
        parentage = abjad.get.parentage(first_leaf)
        parent_voice = abjad.select.components(parentage, abjad.Voice)
        return f"{parent_voice[0].name} temp"

    container = abjad.Container(simultaneous=True)
    original_voice = abjad.Voice(name=_find_parent(selections))
    intermittent_voice = abjad.Voice(name=name)
    selections_ = trinton.get_top_level_components_from_leaves(selections)
    abjad.mutate.wrap(selections_, original_voice)
    abjad.mutate.wrap(original_voice, container)
    if beam is True:
        groups = rmakers.nongrace_leaves_in_each_tuplet(original_voice)
        abjad.beam(groups, beam_rests=False, beam_lone_notes=False)
        baca.extend_beam(abjad.select.leaf(original_voice, -1))

    imbrications = imbricate(
        original_voice,
        "v1",
        pitches,
        allow_unused_pitches=allow_unused_pitches,
        by_pitch_class=by_pitch_class,
        hocket=hocket,
        truncate_ties=truncate_ties,
    )
    imbrication = imbrications["v1"][0]
    contents = abjad.mutate.eject_contents(imbrication)
    intermittent_voice.extend(contents)

    groups = rmakers.nongrace_leaves_in_each_tuplet(intermittent_voice)
    rmakers.beam_groups(groups, beam_rests=True)
    if articulation is not None:
        for head in baca.select.pheads(intermittent_voice):
            abjad.attach(abjad.Articulation(articulation), head)
    baca.extend_beam(abjad.select.leaf(intermittent_voice, -1))
    abjad.override(intermittent_voice).TupletBracket.stencil = False
    abjad.override(intermittent_voice).TupletNumber.stencil = False

    container.append(intermittent_voice)
    if secondary is False:
        direction_1 = "One"
        direction_2 = "Two"
    else:
        direction_1 = "Three \shiftOff"
        direction_2 = "Four \shiftOff"
    if direction == abjad.UP:
        abjad.attach(
            abjad.LilyPondLiteral(rf"\voice{direction_2}", site="before"),
            abjad.select.leaf(original_voice, 0),
        )
        abjad.attach(
            abjad.LilyPondLiteral(rf"\voice{direction_1}", site="before"),
            abjad.select.leaf(intermittent_voice, 0),
        )
    else:
        abjad.attach(
            abjad.LilyPondLiteral(rf"\voice{direction_1}", site="before"),
            abjad.select.leaf(original_voice, 0),
        )
        abjad.attach(
            abjad.LilyPondLiteral(rf"\voice{direction_2}", site="before"),
            abjad.select.leaf(intermittent_voice, 0),
        )
    closing_literal = abjad.LilyPondLiteral(r"\oneVoice", site="after")
    abjad.attach(closing_literal, container)


def call_imbrication(
    pitches, name="Imbrication", articulation=">", beam=True, hocket=False
):
    def imbricate(argument):
        trinton.imbrication(
            selections=argument,
            pitches=pitches,
            name=name,
            direction=abjad.UP,
            articulation=articulation,
            beam=beam,
            hocket=hocket,
        )

    return imbricate


# rest measures


def whiteout_empty_staves(
    score, voice_names=None, cutaway=True, tag=abjad.Tag("+SCORE"), last_segment=False
):
    print("Making empty staves ...")
    if voice_names is not None:
        voices = [score[_] for _ in voice_names]
    else:
        voices = abjad.iterate.components(score["Staff Group"], abjad.Staff)

    for voice in voices:
        shards = abjad.select.group_by_measure(abjad.select.leaves(voice))
        relevant_shards = []
        for shard in shards:
            if (
                all(isinstance(leaf, abjad.Rest) for leaf in shard)
                or all(isinstance(leaf, abjad.MultimeasureRest) for leaf in shard)
                or all(isinstance(leaf, abjad.Skip) for leaf in shard)
            ):
                relevant_shards.append(shard)

        for i, shard in enumerate(relevant_shards):
            indicators = abjad.get.indicators(shard[0])
            multiplier = abjad.get.duration(shard)
            invisible_rest = abjad.MultimeasureRest(1, multiplier=(multiplier))
            rest_literal = abjad.LilyPondLiteral(
                r"\once \override MultiMeasureRest.transparent = ##t", "opening"
            )
            bar_literal = abjad.LilyPondLiteral(
                r"\once \override Staff.BarLine.transparent = ##f", "absolute_before"
            )
            abjad.attach(bar_literal, invisible_rest, tag=tag)
            for indicator in indicators:
                abjad.attach(
                    indicator,
                    invisible_rest,
                )
            if cutaway == "blank":
                abjad.attach(rest_literal, invisible_rest, tag=tag)
                start_command = abjad.LilyPondLiteral(
                    [
                        r"\stopStaff \once \override Staff.StaffSymbol.line-count = #0 \startStaff",
                        r"\once \override Staff.TimeSignature.transparent = ##t",
                    ],
                    site="before",
                )
            else:
                start_command = abjad.LilyPondLiteral(
                    r"\stopStaff \once \override Staff.StaffSymbol.line-count = #1 \startStaff",
                    site="before",
                )

            stop_command = abjad.LilyPondLiteral(
                r"\stopStaff \startStaff", site="after"
            )
            if cutaway is True or cutaway == "blank":
                abjad.attach(start_command, invisible_rest, tag=tag)
                abjad.attach(stop_command, invisible_rest, tag=tag)
                abjad.mutate.replace(shard, invisible_rest)
            else:
                abjad.mutate.replace(shard, invisible_rest)


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


def invisible_rests(selector=None):
    def rests(argument):
        if selector is not None:
            rests = selector(argument)
        else:
            rests = abjad.select.rests(argument)
        for rest in rests:
            rest_literal = abjad.LilyPondLiteral(
                r"\once \override Rest.transparent = ##t", "before"
            )
            abjad.attach(rest_literal, rest)
            rest_literal = abjad.LilyPondLiteral(
                r"\once \override Dots.transparent = ##t", "before"
            )
            abjad.attach(rest_literal, rest)

    return rests


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


# leaf indexing


def annotate_leaves(score, prototype=abjad.Leaf):
    for voice in abjad.select.components(score, abjad.Voice):
        if prototype is not None:
            abjad.label.with_indices(voice, prototype=prototype)
        else:
            abjad.label.with_indices(voice)


def annotate_leaves_locally(selector=abjad.select.leaves, direction=abjad.UP):
    def annotate(argument):
        leaves = selector(argument)
        amount = len(leaves)

        for leaf, i in zip(leaves, list(range(amount))):
            abjad.attach(abjad.Markup(rf"\markup {i}"), leaf, direction=direction)

    return annotate


# tweaks


def tweak_command(tweaks, selector=trinton.selectors.pleaves()):
    def tweak_it(argument):
        selections = selector(argument)
        for selection in selections:
            for new_tweak in tweaks:
                abjad.tweak(selection, new_tweak)

    return tweak_it
