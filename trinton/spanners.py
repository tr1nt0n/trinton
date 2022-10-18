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


def write_text_span(voice, begin_text, end_text, start_leaf, stop_leaf, padding):
    start_text_span = abjad.StartTextSpan(
        left_text=abjad.Markup(begin_text),
        right_text=abjad.Markup(end_text),
        style="dashed-line-with-arrow",
    )
    bundle = abjad.bundle(start_text_span, rf"- \tweak padding #{padding}")
    trinton.attach(voice, start_leaf, bundle)
    trinton.attach(voice, stop_leaf, abjad.StopTextSpan())


def write_hooked_spanner(voice, string, start_leaf, stop_leaf, padding):
    start_text_span = abjad.StartTextSpan(
        left_text=abjad.Markup(string),
        right_text=None,
        style="dashed-line-with-hook",
    )
    bundle = abjad.bundle(start_text_span, rf"- \tweak padding #{padding}")
    trinton.attach(voice, start_leaf, bundle)
    trinton.attach(voice, stop_leaf, abjad.StopTextSpan())


def write_slur(voice, start_slur, stop_slur):
    for leaf in start_slur:
        trinton.attach(voice, [leaf], abjad.StartPhrasingSlur())
    for leaf in stop_slur:
        trinton.attach(voice, [leaf], abjad.StopPhrasingSlur())


def dashed_slur(start_selection, stop_selection):
    abjad.attach(abjad.StartSlur(), start_selection)
    abjad.attach(
        abjad.LilyPondLiteral(r"\slurDashed", "absolute_before"),
        start_selection,
    )
    abjad.attach(abjad.StopSlur(), stop_selection)
    abjad.attach(
        abjad.LilyPondLiteral(r"\slurSolid", "absolute_after"),
        stop_selection,
    )


def write_trill_span(score, voice, pitch, start_leaf, stop_leaf):
    trinton.attach(
        voice=score[voice],
        leaves=start_leaf,
        attachment=abjad.StartTrillSpan(pitch=pitch),
    )
    trinton.attach(
        voice=score[voice],
        leaves=stop_leaf,
        attachment=abjad.StopTrillSpan(),
    )


def ottava(score, voice, start_ottava, stop_ottava, octave):
    for start, stop in zip(start_ottava, stop_ottava):
        start_va = abjad.Ottava(n=octave)
        abjad.attach(start_va, abjad.select.leaf(score[voice], start))
        stop_va = abjad.Ottava(n=0, site="after")
        abjad.attach(
            stop_va,
            abjad.select.leaf(score[voice], stop),
        )


def write_id_spanner(
    style, left_text, right_text, id, start_selection, stop_selection, padding=7
):
    strings = [
        rf"- \abjad-{style}",
        rf"- \tweak bound-details.left.text \markup \concat {{ {{ \upright {left_text} }} \hspace #0.5 }}",
    ]

    if right_text is not None:
        for string in [
            rf"- \tweak bound-details.right.text \markup \concat {{ {{ \upright {right_text} }} \hspace #0.5 }}"
            rf"\startTextSpan{id}",
        ]:
            strings.append(string)

    else:
        strings.append(rf"\startTextSpan{id}")

    spanner = abjad.LilyPondLiteral(
        strings,
        "absolute_after",
    )

    bundle = abjad.bundle(spanner, rf"- \tweak padding #{padding}")

    termination = abjad.LilyPondLiteral(rf"\stopTextSpan{id}", "absolute_after")

    abjad.attach(bundle, start_selection)
    abjad.attach(termination, stop_selection)
