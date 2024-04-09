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


def write_markup(voice, leaf, string, down):
    if down == True:
        markup = abjad.Markup(string, direction=abjad.Down)
        trinton.attach(voice, leaf, markup)
    else:
        markup = abjad.Markup(string, direction=abjad.Up)
        trinton.attach(voice, leaf, markup)


def write_startmarkups(score, voices, markups):
    for voice, markup in zip(voices, markups):
        start_markup = abjad.InstrumentName(markup=markup)

        trinton.attach(
            voice=score[voice],
            leaves=[0],
            attachment=start_markup,
        )


def write_marginmarkups(score, voices, markups):
    for voice, markup in zip(voices, markups):
        margin_markup = abjad.ShortInstrumentName(markup=markup)

        trinton.attach(
            voice=score[voice],
            leaves=[0],
            attachment=margin_markup,
        )


def return_fraction_string_list(tups):
    return [
        rf"\markup \concat {{ \upright \fraction {tup[0]} {tup[-1]} }}" for tup in tups
    ]


def boxed_markup(
    string,
    tweaks=None,
    column="\center-column",
    font_name="Bodoni72 Book",
    fontsize=2,
    string_only=False,
):
    if isinstance(string, list):
        lines = [f"\line {{ {_} }} " for _ in string]

        lines = "".join(lines)

        markup = abjad.Markup(
            rf"""\markup \override #'(font-name . " {font_name} ") \override #'(style . "box") \override #'(box-padding . 0.5) \whiteout \box \fontsize #{fontsize} {{ {column} {{ { lines } }} }}""",
        )

    else:
        markup = abjad.Markup(
            rf"""\markup \override #'(font-name . " {font_name} ") \override #'(style . "box") \override #'(box-padding . 0.5) \whiteout \fontsize #{fontsize} \box \line {{ {string} }}""",
        )

    if tweaks is not None:
        for tweak in tweaks:
            markup = abjad.bundle(markup, tweak)

    if string_only is True:
        return markup.string
    else:
        return markup


def notation_markup(
    time_signatures,
    rhythm_handler,
    *args,
    tweaks=None,
    preprocessor=None,
    beam_meter=False,
):
    durations = [abjad.Duration(_.pair) for _ in time_signatures]
    if preprocessor is not None:
        divisions = preprocessor(durations)
    else:
        divisions = time_signatures
    nested_music = rhythm_handler(divisions)
    container = abjad.Container(nested_music)

    music = rmakers.wrap_in_time_signature_staff(
        abjad.select.components(container)[1:], time_signatures
    )

    for arg in args:
        arg(music)

    if len(time_signatures) > 1:
        new_time_signatures = []

        for time_signature, previous_time_signature in zip(
            time_signatures[:], trinton.rotated_sequence(time_signatures, -1)
        ):
            if previous_time_signature == time_signature:
                bundle = abjad.bundle(time_signature, r"\tweak stencil ##f")

                new_time_signatures.append(bundle)
            else:
                new_time_signatures.append(time_signature)

    else:
        new_time_signatures = time_signatures

    component_voices = abjad.select.components(music, abjad.Voice)

    component_voices = component_voices[1:]

    if len(component_voices) > 1:
        grouped_music = abjad.select.group_by_measure(component_voices[0])
    else:
        grouped_music = abjad.select.group_by_measure(music)

    for measure, time_signature in zip(grouped_music, new_time_signatures):
        abjad.attach(time_signature, abjad.select.leaf(measure, 0))
        if len(component_voices) > 1:
            abjad.attach(
                abjad.LilyPondLiteral(
                    [
                        r"\once \override Voice.Rest.transparent = ##t",
                        r"\once \override Voice.Dots.transparent = ##t",
                    ],
                    site="before",
                ),
                abjad.select.leaf(measure, 0),
            )

    if beam_meter is True:
        measures = abjad.select.group_by_measure(music)
        for i, shard in enumerate(measures):
            top_level_components = trinton.get_top_level_components_from_leaves(shard)
            shard = top_level_components
            met = abjad.Meter(time_signatures[i].pair)
            inventories = [
                x
                for x in enumerate(
                    abjad.Meter(time_signatures[i].pair).depthwise_offset_inventory
                )
            ]
            if time_signatures[i].denominator == 4:
                trinton.beam_meter(
                    components=shard[:],
                    meter=met,
                    offset_depth=inventories[-1][0],
                    include_rests=False,
                )
            else:
                trinton.beam_meter(
                    components=shard[:],
                    meter=met,
                    offset_depth=inventories[-2][0],
                    include_rests=False,
                )
    for trem in abjad.select.components(music, abjad.TremoloContainer):
        if abjad.StartBeam() in abjad.get.indicators(trem[0]):
            abjad.detach(abjad.StartBeam(), trem[0])
        if abjad.StopBeam() in abjad.get.indicators(trem[-1]):
            abjad.detach(abjad.StopBeam(), trem[-1])

    music = abjad.lilypond(music)

    string = rf"""\markup {{ \score {{
    \new Staff {{
    {music}
    }}
    \layout
    {{ ragged-right = ##t  indent = 0\cm
    \context {{
    \Staff
    \consists Time_signature_engraver
    \override TimeSignature.whiteout-style = #'outline
    \override TimeSignature.whiteout = 1
    \override TimeSignature.layer = 20
    }}
    }}
    }} }}"""

    markup = abjad.Markup(string)

    if tweaks is not None:
        for tweak in tweaks:
            markup = abjad.bundle(markup, tweak)

    return markup
