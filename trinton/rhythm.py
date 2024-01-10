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


def treat_tuplets(non_power_of_two=False):
    def treatment(selections):
        tuplets = abjad.select.tuplets(selections)
        rmakers.rewrite_dots(tuplets)
        tuplets = abjad.select.tuplets(selections)
        rmakers.trivialize(tuplets)
        tuplets = abjad.select.tuplets(selections)
        rmakers.rewrite_rest_filled(tuplets)
        if non_power_of_two is False:
            tuplets = abjad.select.tuplets(selections)
            rmakers.rewrite_sustained(tuplets)
        tuplets = abjad.select.tuplets(selections)
        rmakers.extract_trivial(tuplets)

    return treatment


def force_note(selector):
    def force(selections):
        selection = selector(selections)
        rmakers.force_note(selection)

    return force


def force_rest(selector):
    def force(selections):
        selection = selector(selections)
        rmakers.force_rest(selection)

    return force


def beam_groups(beam_rests=False, beam_lone_notes=False, selector=None):
    def beam(argument):
        if selector is not None:
            selections = selector(argument)
        else:
            selections = [argument]

        for group in selections:
            abjad.beam(group, beam_rests=beam_rests, beam_lone_notes=False)

    return beam


def call_rmaker(rmaker, selector):
    def call(argument):
        selections = selector(argument)
        rmaker(selections)

    return call


# def respell_tuplets(tuplets):
#     for tuplet in tuplets:
#         prolation = tuplet.implied_prolation
#         if prolation.denominator == 3 and prolation.numerator % 2 == 0:
#             rmakers.force_diminution(tuplet)
#         if prolation.denominator == 5 and prolation.numerator % 3 == 0:
#             rmakers.force_augmentation(tuplet)
#         if prolation.denominator == 7 and prolation.numerator % 4 == 0:
#             rmakers.force_augmentation(tuplet)
#         if prolation.denominator == 7 and prolation.numerator % 5 == 0:
#             rmakers.force_augmentation(tuplet)
#         if prolation.denominator == 7 and prolation.numerator % 6 == 0:
#             rmakers.force_diminution(tuplet)
#         if prolation.denominator == 9 and prolation.numerator % 5 == 0:
#             rmakers.force_augmentation(tuplet)
#         if prolation.denominator == 9 and prolation.numerator % 7 == 0:
#             rmakers.force_diminution(tuplet)
#         if prolation.denominator % 9 == 0 and prolation.numerator % 11 == 0:
#             rmakers.force_augmentation(tuplet)
#             tuplet.denominator = 11
#         if prolation.denominator % 10 == 0 and prolation.numerator % 11 == 0:
#             rmakers.force_augmentation(tuplet)
#         if prolation.denominator == 15 and prolation.numerator % 2 == 0:
#             rmakers.force_augmentation(tuplet)


def respell_tuplets(tuplets, rewrite_brackets=True):
    for tuplet in tuplets:
        prolation = tuplet.implied_prolation
        numerator = prolation.denominator
        denominator = prolation.numerator
        duration = tuplet.multiplied_duration.pair
        duration_numerator = duration[0]
        duration_denominator = duration[-1]

        new_multiplier = Fraction(denominator, numerator)
        tuplet.multiplier = (new_multiplier.numerator, new_multiplier.denominator)

        if denominator % duration_numerator != 0:

            if denominator % 3 == 0 and denominator != 9:
                denominator = denominator * 3
                numerator = numerator * 3
            else:
                denominator = denominator * duration_numerator
                numerator = numerator * duration_numerator

            tuplet.multiplier = (denominator, numerator)

        if numerator == 3 and denominator == 2:
            tuplet_contents = abjad.get.contents(tuplet)[1:]
            tuplet_duration_denominator = duration[-1]
            target_duration = abjad.Duration(1, tuplet_duration_denominator * 4)
            target_durations = []
            non_target_durations = []

            for item in tuplet_contents:
                if abjad.get.duration(item, preprolated=True) <= target_duration:
                    target_durations.append(item)
                else:
                    non_target_durations.append(item)
            if len(target_durations) > len(non_target_durations):
                tuplet.multiplier = (4, 6)

            else:
                pass

        else:
            double_denominator = denominator * 2
            half_denominator = int(denominator / 2)

            current_difference = abs(numerator - denominator)
            double_difference = abs(numerator - double_denominator)
            half_difference = abs(numerator - half_denominator)

            difference_array = [current_difference, double_difference, half_difference]
            difference_array = sorted(difference_array)

            smallest = difference_array[0]

            if smallest == current_difference:
                pass

            if smallest == half_difference:
                rmakers.force_diminution(tuplet)

            if smallest == double_difference:
                rmakers.force_augmentation(tuplet)

        if rewrite_brackets is True:
            if abjad.Duration(duration) < abjad.Duration(3, 16):
                abjad.attach(
                    abjad.LilyPondLiteral(
                        r"\once \override TupletBracket.bracket-visibility = ##f",
                        site="before",
                    ),
                    abjad.select.leaf(tuplet, 0),
                )


def handwrite_nested_tuplets(
    tuplet_ratios,
    preprocessor=None,
    nested_ratios=None,
    triple_nested_ratios=None,
    nested_vectors=None,
    nested_period=None,
    triple_nested_vectors=None,
    triple_nested_period=None,
):
    def make_figures(divisions):

        first_layer_tuplets = rmakers.tuplet(divisions, tuplet_ratios)
        container = abjad.Container(first_layer_tuplets)
        rmakers.rewrite_dots(container)
        rmakers.trivialize(container)
        rmakers.rewrite_rest_filled(container)
        rmakers.rewrite_sustained(container)

        if nested_ratios is not None:
            period_selector = trinton.patterned_tie_index_selector(
                nested_vectors, nested_period
            )
            selections = period_selector(container)

            durations = [abjad.get.duration(_, preprolated=True) for _ in selections]
            tuplets = rmakers.tuplet(durations, nested_ratios)
            rmakers.rewrite_dots(tuplets)
            rmakers.trivialize(tuplets)
            rmakers.rewrite_rest_filled(tuplets)
            rmakers.rewrite_sustained(tuplets)

            for tie, tuplet in zip(selections, tuplets):
                abjad.mutate.replace(tie, tuplet)

        if triple_nested_ratios is not None:
            second_layer_tuplets = []
            for tuplet in abjad.select.tuplets(container):
                tuplet_parent = abjad.get.parentage(tuplet).parent
                if isinstance(tuplet_parent, abjad.Tuplet):
                    second_layer_tuplets.append(tuplet)

            period_selector = trinton.patterned_tie_index_selector(
                triple_nested_vectors, triple_nested_period
            )
            selections = period_selector(second_layer_tuplets)

            durations = [abjad.get.duration(_, preprolated=True) for _ in selections]
            tuplets = rmakers.tuplet(durations, triple_nested_ratios)
            rmakers.rewrite_dots(tuplets)
            rmakers.trivialize(tuplets)
            rmakers.rewrite_rest_filled(tuplets)
            rmakers.rewrite_sustained(tuplets)

            for tie, tuplet in zip(selections, tuplets):
                abjad.mutate.replace(tie, tuplet)

        rmakers.extract_trivial(container)
        respell_tuplets(abjad.select.tuplets(container))

        selections = abjad.mutate.eject_contents(container)
        return selections

    return make_figures


def intermittent_voice_with_selector(selector, rmaker, voice_name, direction=abjad.UP):
    def make_voice(argument):
        selections = selector(argument)
        handler = evans.IntermittentVoiceHandler(
            rhythm_handler=evans.RhythmHandler(rmaker),
            direction=direction,
            voice_name=voice_name,
        )

        handler(selections)

    return make_voice


def aftergrace_command(
    notes_string="c'16",
    selector=trinton.selectors.pleaves(),
    slash=False,
    glissando=False,
):
    def grace(argument):
        selections = selector(argument)

        ties = abjad.select.logical_ties(selections)

        containers = [abjad.AfterGraceContainer(notes_string) for _ in ties]

        if slash is True:
            for container in containers:
                literal = abjad.LilyPondLiteral(
                    r'\once \override Flag.stroke-style = #"grace"',
                )

                abjad.attach(literal, container[0])

        for container, tie in zip(containers, ties):
            abjad.attach(container, tie[-1])

            if glissando is True:
                with_next_leaf = abjad.select.with_next_leaf(tie)
                abjad.glissando(
                    with_next_leaf,
                    hide_middle_note_heads=True,
                    allow_repeats=True,
                    allow_ties=True,
                    zero_padding=True,
                )
                for leaf in tie:
                    abjad.attach(
                        abjad.LilyPondLiteral(
                            r"\once \override Dots.staff-position = #2", "before"
                        ),
                        leaf,
                    )
                    abjad.detach(abjad.Tie, leaf)

    return grace
