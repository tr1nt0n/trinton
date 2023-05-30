import abjad
import baca
import evans
import trinton
from abjadext import rmakers
from fractions import Fraction
import quicktions
import numpy
import itertools
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


def write_slur(voice, start_slur, stop_slur, direction=None):
    for leaf in start_slur:
        trinton.attach(voice, [leaf], abjad.StartPhrasingSlur(), direction=direction)
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


def trill_span_command(pitch=None, selector=trinton.pleaves()):
    def span(argument):
        selections = selector(argument)
        it = iter(selections)

        tups = [*zip(it, it)]

        for tup in tups:
            abjad.attach(abjad.StartTrillSpan(pitch=abjad.NamedPitch(pitch)), tup[0])
            abjad.attach(abjad.StopTrillSpan(), tup[1])

    return span


def ottava(score, voice, start_ottava, stop_ottava, octave):
    for start, stop in zip(start_ottava, stop_ottava):
        start_va = abjad.Ottava(n=octave)
        abjad.attach(start_va, abjad.select.leaf(score[voice], start))
        stop_va = abjad.Ottava(n=0, site="after")
        abjad.attach(
            stop_va,
            abjad.select.leaf(score[voice], stop),
        )


def ottava_command(selector, octave=1):
    def wrap(argument):
        selections = selector(argument)
        it = iter(selections)

        tups = [*zip(it, it)]

        for tup in tups:
            abjad.attach(abjad.Ottava(n=octave), tup[0])
            abjad.attach(abjad.Ottava(n=0, site="after"), tup[1])

    return wrap


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


def hooked_spanner_command(
    string,
    selector,
    padding=7,
    direction=None,
    right_padding=1,
    full_string=False,
    style="dashed-line-with-hook",
    hspace=None,
    command="",
    tag=None,
):
    if full_string is True:
        markup = abjad.Markup(string)

    else:
        markup = abjad.Markup(rf'\markup \upright {{ "{string}" }}')

    def attach_spanner(argument):
        start_text_span = abjad.StartTextSpan(
            command=r"\startTextSpan" + command,
            left_text=markup,
            right_text=None,
            style=style,
            right_padding=-right_padding,
        )

        bundle = abjad.bundle(start_text_span, rf"- \tweak padding #{padding}")

        selections = selector(argument)

        it = iter(selections)

        tups = [*zip(it, it)]

        for tup in tups:
            if direction == "down":
                abjad.attach(
                    abjad.LilyPondLiteral(
                        r"\textSpannerDown",
                        "before",
                    ),
                    tup[0],
                    tag=tag,
                )
                abjad.attach(
                    abjad.LilyPondLiteral(
                        r"\textSpannerUp",
                        "after",
                    ),
                    tup[1],
                    tag=tag,
                )
            abjad.attach(bundle, tup[0], tag=tag),
            abjad.attach(
                abjad.StopTextSpan(
                    command=r"\stopTextSpan" + command,
                ),
                tup[1],
                tag=tag,
            )

    return attach_spanner


def arrow_spanner_command(
    l_string,
    r_string,
    selector,
    style="dashed-line-with-arrow",
    padding=7,
    direction=None,
    tempo=False,
    right_padding=None,
):
    def attach_spanner(argument):

        if right_padding is not None:
            r_padding = right_padding * -1

        else:
            r_padding = right_padding

        if tempo is True:
            start_text_span = abjad.StartTextSpan(
                left_text=abjad.Markup(l_string),
                right_text=abjad.Markup(r_string),
                style=style,
                right_padding=r_padding,
            )

        else:
            start_text_span = abjad.StartTextSpan(
                left_text=abjad.Markup(rf'\markup \upright {{ "{l_string}" }}'),
                right_text=abjad.Markup(rf"\markup \upright {{ {r_string} }}"),
                style=style,
                right_padding=r_padding,
            )

        bundle = abjad.bundle(start_text_span, rf"- \tweak padding #{padding}")

        selections = selector(argument)

        it = iter(selections)

        tups = [*zip(it, it)]

        for tup in tups:
            if direction == "down":
                abjad.attach(
                    abjad.LilyPondLiteral(
                        r"\textSpannerDown",
                        "before",
                    ),
                    tup[0],
                )
                abjad.attach(
                    abjad.LilyPondLiteral(
                        r"\textSpannerUp",
                        "after",
                    ),
                    tup[1],
                )
            abjad.attach(bundle, tup[0]),
            abjad.attach(abjad.StopTextSpan(), tup[1])

    return attach_spanner


def spanner_command(
    strings,
    selector,
    style="dashed-line-with-arrow",
    padding=7,
    right_padding=None,
    direction=None,
    full_string=False,
    command="",
    end_hook=False,
    end_hook_style="dashed-line-with-hook",
):
    def attach_spanner(argument):
        if full_string is True:
            markups = [abjad.Markup(_) for _ in strings]

        else:
            markups = [abjad.Markup(rf'\markup \upright {{ "{_}" }}') for _ in strings]

        if right_padding is not None:
            r_padding = right_padding * -1

        else:
            r_padding = right_padding

        if len(strings) < 3 and end_hook is False:
            start_spans = [
                abjad.StartTextSpan(
                    command=r"\startTextSpan" + command,
                    left_text=markups[0],
                    right_text=markups[1],
                    style=style,
                    right_padding=r_padding,
                )
            ]

        if len(strings) < 3 and end_hook is True:
            start_spans = [
                abjad.StartTextSpan(
                    command=r"\startTextSpan" + command,
                    left_text=markups[0],
                    style=style,
                    right_padding=r_padding,
                ),
            ]

            last_span = abjad.StartTextSpan(
                command=r"\startTextSpan" + command,
                left_text=markups[1],
                style=end_hook_style,
                right_padding=-1.5,
            )

        if len(strings) > 2 and end_hook is False:
            all_but_last_markup = markups[:]
            del all_but_last_markup[-1]
            del all_but_last_markup[-1]

            start_spans = [
                abjad.StartTextSpan(
                    command=r"\startTextSpan" + command,
                    left_text=markup,
                    style=style,
                    right_padding=r_padding,
                )
                for markup in all_but_last_markup
            ]

            last_span = abjad.StartTextSpan(
                command=r"\startTextSpan" + command,
                left_text=markups[-2],
                right_text=markups[-1],
                style=style,
                right_padding=r_padding,
            )

        if len(strings) > 2 and end_hook is True:
            all_but_last_markup = markups[:]
            del all_but_last_markup[-1]

            start_spans = [
                abjad.StartTextSpan(
                    command=r"\startTextSpan" + command,
                    left_text=markup,
                    style=style,
                    right_padding=r_padding,
                )
                for markup in all_but_last_markup
            ]

            last_span = abjad.StartTextSpan(
                command=r"\startTextSpan" + command,
                left_text=markups[-1],
                style=end_hook_style,
                right_padding=-1.5,
            )

        selections = selector(argument)

        if len(strings) < 3:
            selections = selections

        if len(strings) > 2 or end_hook is True:
            last_pair = selections[-2:]
            selections = abjad.select.exclude(selections, [-1, -2])

        it = iter(selections)

        tups = [*zip(it, it)]

        start_spans = [
            abjad.bundle(span, rf"- \tweak padding #{padding}") for span in start_spans
        ]

        for tup, span in zip(tups, start_spans):
            abjad.attach(span, tup[0]),
            abjad.attach(
                abjad.StopTextSpan(command=r"\stopTextSpan" + command), tup[-1]
            )

        if len(strings) > 2 or end_hook is True:
            last_span = abjad.bundle(last_span, rf"- \tweak padding #{padding}")

            abjad.attach(last_span, last_pair[0])

            abjad.attach(
                abjad.StopTextSpan(command=r"\stopTextSpan" + command), last_pair[-1]
            )

    return attach_spanner


def id_spanner_command(
    selector,
    id,
    left_text,
    right_text=None,
    style="dashed-line-with-arrow",
    padding=7,
    right_padding=None,
    tag=None,
):
    def attach_spanner(argument):
        selections = selector(argument)

        if right_padding is not None:
            r_padding = right_padding * -1

        else:
            r_padding = right_padding

        if right_text is not None:
            spanner = abjad.StartTextSpan(
                command=r"\startTextSpan" + id,
                left_text=abjad.Markup(rf'\markup \upright {{ "{left_text}" }}'),
                right_text=abjad.Markup(rf'\markup \upright {{ "{right_text}" }}'),
                style=style,
                right_padding=r_padding,
            )

        else:
            spanner = abjad.StartTextSpan(
                command=r"\startTextSpan" + id,
                left_text=abjad.Markup(rf'\markup \upright {{ "{left_text}" }}'),
                style=style,
                right_padding=r_padding,
            )

        bundle = abjad.bundle(spanner, rf"- \tweak padding #{padding}")

        termination = abjad.StopTextSpan(
            command=rf"\stopTextSpan" + id,
        )

        it = iter(selections)

        tups = [*zip(it, it)]

        for tup in tups:
            abjad.attach(bundle, tup[0], tag=tag)
            abjad.attach(termination, tup[1], tag=tag)

    return attach_spanner
