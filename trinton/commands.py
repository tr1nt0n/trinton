import abjad
import baca
import evans
import trinton
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


def attachment_command(attachments, selector, direction=None):
    def command(argument):
        selections = selector(argument)
        for selection in selections:
            for attachment in attachments:
                abjad.attach(attachment, selection, direction=direction)

    return command


def linear_attachment_command(attachments, selector, direction=None):
    def command(argument):
        selections = selector(argument)
        for selection, attachment in zip(selections, attachments):
            abjad.attach(attachment, selection, direction=direction)

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


def pitched_notehead_change(voice, pitches, notehead):
    for leaf in abjad.select.leaves(voice, pitched=True):
        for pitch in pitches:
            if leaf.written_pitch.number == pitch:
                abjad.tweak(leaf.note_head, rf"\tweak style #'{notehead}")


def change_notehead_command(notehead, selector):
    def change(argument):
        selections = selector(argument)
        leaves = abjad.select.leaves(selections, pitched=True)
        for leaf in leaves:
            abjad.tweak(leaf.note_head, rf"\tweak style #'{notehead}")

    return change


def noteheads_only(duration_log="2"):
    def only_noteheads(argument):
        for leaf in abjad.select.leaves(argument, pitched=True):
            abjad.attach(
                abjad.LilyPondLiteral(r"\once \override Stem.stencil = ##f", "before"),
                leaf,
            )
            abjad.attach(
                abjad.LilyPondLiteral(r"\once \override Beam.stencil = ##f", "before"),
                leaf,
            )
            abjad.attach(
                abjad.LilyPondLiteral(r"\once \override Flag.stencil = ##f", "before"),
                leaf,
            )
            abjad.attach(
                abjad.LilyPondLiteral(r"\once \override Dots.stencil = ##f", "before"),
                leaf,
            )
            abjad.attach(
                abjad.LilyPondLiteral(
                    rf"\once \override NoteHead.duration-log = {duration_log}", "before"
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


# tuplets


def tuplet_brackets(score, all_staves):
    new_brackets = evans.NoteheadBracketMaker()

    for staff in all_staves:
        new_brackets(score[staff])


def notehead_bracket_command(selector=None):
    def call_handler(argument):
        handler = evans.NoteheadBracketMaker()
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


def invisible_tuplet_brackets():
    def command(argument):
        for tuplet in abjad.select.tuplets(argument):
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


def unmeasured_stem_tremolo(selections):
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


def tremolo_command(selector):
    def trem(argument):
        selections = selector(argument)
        for selection in selections:
            unmeasured_stem_tremolo([selection])

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


def glissando_command(selector, tweaks=[], zero_padding=False):
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
            for leaf in middle_leaves:
                abjad.attach(
                    abjad.LilyPondLiteral(
                        r"\once \override Dots.staff-position = #2", "before"
                    ),
                    leaf,
                )

    return command


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


def beam_durations(divisions, beam_rests=False):
    def func(selections):
        selections = abjad.select.leaves(selections)

        durations = cycle([abjad.Duration(_) for _ in divisions])

        new_durations = []

        for _, duration in zip(range(len(selections)), durations):
            new_durations.append(duration)

        group = []

        for leaf in selections:
            group.append(leaf)

            if abjad.get.duration(group) == new_durations[0]:
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


# rest measures


def whiteout_empty_staves(score, voice_names=None, cutaway=True):
    print("Making empty staves ...")
    ts_leaves = abjad.select.leaves(score["Global Context"])
    signature_instances = [
        abjad.get.indicator(_, abjad.TimeSignature) for _ in ts_leaves
    ]
    if voice_names is not None:
        voices = [score[_] for _ in voices]
    else:
        voices = abjad.iterate.components(score["Staff Group"], abjad.Staff)

    for voice in voices:
        leaves = abjad.select.leaves(voice, grace=False)
        shards = abjad.mutate.split(leaves, signature_instances)
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
            if cutaway == "blank":
                multimeasure_rest = abjad.Skip(1, multiplier=(multiplier))
                start_command = abjad.LilyPondLiteral(
                    r"\stopStaff \once \override Staff.StaffSymbol.line-count = #0 \startStaff",
                    site="before",
                )
            else:
                multimeasure_rest = abjad.MultimeasureRest(1, multiplier=(multiplier))
                start_command = abjad.LilyPondLiteral(
                    r"\stopStaff \once \override Staff.StaffSymbol.line-count = #1 \startStaff",
                    site="before",
                )

            stop_command = abjad.LilyPondLiteral(
                r"\stopStaff \startStaff", site="after"
            )
            if cutaway is True or cutaway == "blank":
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


def invisible_rests():
    def rests(argument):
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
