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
            # tuplet_contents = abjad.get.contents(tuplet)[1:]
            # tuplet_duration_denominator = duration[-1]
            # target_duration = abjad.Duration(1, tuplet_duration_denominator * 4)
            # target_durations = []
            # non_target_durations = []
            #
            # for item in tuplet_contents:
            #     if abjad.get.duration(item, preprolated=True) <= target_duration:
            #         target_durations.append(item)
            #     else:
            #         non_target_durations.append(item)

            def sextuplet_or_not(triplet):
                dotted_duration = abjad.Duration(duration) / 2
                checked_notes = []
                for item in abjad.get.contents(triplet)[1:]:
                    checked_duration = abjad.get.duration(checked_notes)
                    if checked_duration != dotted_duration:
                        checked_notes.append(item)
                    else:
                        return True
                        break

            if sextuplet_or_not(triplet=tuplet) is True:
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


def respell_tuplets_command(selector=abjad.select.tuplets, rewrite_brackets=True):
    def respell(argument):
        selections = selector(argument)

        respell_tuplets(tuplets=selections, rewrite_brackets=rewrite_brackets)

    return respell


def handwrite_nested_tuplets(
    tuplet_ratios,
    preprocessor=None,
    nested_ratios=None,
    triple_nested_ratios=None,
    nested_vectors=None,
    nested_period=None,
    triple_nested_vectors=None,
    triple_nested_period=None,
    extract_trivial_tuplets=True,
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
                nested_vectors, nested_period, pitched=True
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
                triple_nested_vectors, triple_nested_period, pitched=True
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

        if extract_trivial_tuplets is True:
            rmakers.extract_trivial(container)

        respell_tuplets(abjad.select.tuplets(container), rewrite_brackets=False)

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


class IntermittentVoiceHandler(evans.handlers.Handler):
    r"""
    IntermittentVoiceHandler

    .. container:: example

        >>> ph_up = evans.PitchHandler([8, 8.5, 9, 9.5, 9, 8.5], forget=False)
        >>> ph_down = evans.PitchHandler([0, 1, 2, 3, 4, 5], forget=False)
        >>> s = abjad.Staff([abjad.Voice("c'4 c'8 c'8 c'8 c'4.", name="Voice1")], name="Staff1")
        >>> ph_down(s)
        >>> maker = evans.talea([1, 2, 3, 4], 8, extra_counts=[1, 0, -1])
        >>> handler = evans.RhythmHandler(maker, forget=False)
        >>> def rhythm_function(durations):
        ...     nested_music = handler(durations)
        ...     container = abjad.Container()
        ...     for _ in nested_music:
        ...         container.append(_)
        ...     tuplet_target = abjad.select.tuplets(container)
        ...     rmakers.trivialize(tuplet_target)
        ...     tuplet_target = abjad.select.tuplets(container)
        ...     rmakers.extract_trivial(tuplet_target)
        ...     tuplet_target = abjad.select.tuplets(container)
        ...     rmakers.rewrite_rest_filled(tuplet_target)
        ...     tuplet_target = abjad.select.tuplets(container)
        ...     rmakers.rewrite_sustained(tuplet_target)
        ...     music = abjad.mutate.eject_contents(container)
        ...     return music
        ...
        >>> ivh = evans.IntermittentVoiceHandler(rhythm_function, direction=abjad.UP)
        >>> sel1 = abjad.select.leaf(s["Voice1"], 0)
        >>> sel2 = abjad.select.leaf(s["Voice1"], 2)
        >>> sel3 = abjad.select.leaves(s["Voice1"])
        >>> sel3_get = abjad.select.get(sel3, [3, 4])
        >>> ivh(sel1)
        >>> ivh(sel2)
        >>> ivh(sel3_get)
        >>> ph_up = evans.PitchHandler([8, 8.5, 9, 9.5, 9, 8.5], forget=False)
        >>> for voice in abjad.select.components(s, abjad.Voice):
        ...     if voice.name == "intermittent_voice":
        ...         ph_up(voice)
        ...
        >>> score = abjad.Score([s])
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

            >>> print(abjad.lilypond(s))
            \context Staff = "Staff1"
            {
                \context Voice = "Voice1"
                {
                    <<
                        \context Voice = "Voice1"
                        {
                            \voiceTwo
                            c'4
                        }
                        \context Voice = "intermittent_voice"
                        {
                            \times 2/3
                            {
                                \voiceOne
                                af'8
                                aqf'4
                            }
                        }
                    >>
                    \oneVoice
                    cs'8
                    <<
                        \context Voice = "Voice1"
                        {
                            \voiceTwo
                            d'8
                        }
                        \context Voice = "intermittent_voice"
                        {
                            \voiceOne
                            a'8
                        }
                    >>
                    \oneVoice
                    <<
                        \context Voice = "Voice1"
                        {
                            \voiceTwo
                            ef'8
                            e'4.
                        }
                        \context Voice = "intermittent_voice"
                        {
                            \tweak text #tuplet-number::calc-fraction-text
                            \times 4/3
                            {
                                \voiceOne
                                aqs'4
                                a'8
                            }
                        }
                    >>
                    \oneVoice
                }
            }

    """

    def __init__(
        self,
        rhythm_handler,
        direction=abjad.UP,
        cluster=False,
        cluster_color="#(rgb-color 0.56 0.85 0.6)",
        voice_name="intermittent_voice",
        from_components=False,
        preprocessor=None,
        temp_name="temp",
        tag=None,
    ):
        self.rhythm_handler = rhythm_handler
        self.direction = direction
        self.cluster = cluster
        self.cluster_color = cluster_color
        self.voice_name = voice_name
        self.from_components = from_components
        self.preprocessor = preprocessor
        self.temp_name = temp_name
        self.tag = tag

    def __call__(
        self,
        selections,
    ):
        selections = selections
        self._add_voice(selections)

    def _add_voice(self, selections):
        if self.direction == abjad.UP:
            literal1 = abjad.LilyPondLiteral(r"\voiceTwo")
            literal2 = abjad.LilyPondLiteral(r"\voiceOne")
        else:
            literal1 = abjad.LilyPondLiteral(r"\voiceOne")
            literal2 = abjad.LilyPondLiteral(r"\voiceTwo")
        closing_literal = abjad.LilyPondLiteral(r"\oneVoice", site="after")
        if isinstance(selections, list):
            duration = [abjad.get.duration(selections[:])]
        else:
            duration = [abjad.get.duration(selections)]
        if self.preprocessor is not None:
            duration = self.preprocessor(duration)
        container = abjad.Container(simultaneous=True)
        original_voice = abjad.Voice(name=self._find_parent(selections))
        intermittent_voice = abjad.Voice(name=self.voice_name, tag=self.tag)
        if self.cluster is False:
            new_components = self._make_components(duration)[:]
            for new_component in new_components:
                intermittent_voice.append(new_component)
        else:
            new_components = self._make_components(duration)
            intermittent_voice.append(new_components)
        selections = evans.get_top_level_components_from_leaves(selections)
        abjad.mutate.wrap(selections, original_voice)
        abjad.mutate.wrap(original_voice, container)
        container.append(intermittent_voice)
        if self.direction != "neutral":
            abjad.attach(literal1, abjad.select.leaf(original_voice, 0))
            abjad.attach(literal2, abjad.select.leaf(intermittent_voice, 0))
            abjad.attach(closing_literal, container)

    def _find_parent(self, selections):
        first_leaf = abjad.select.leaf(selections, 0)
        parentage = abjad.get.parentage(first_leaf)
        parent_voice = abjad.select.components(parentage, abjad.Voice)
        return f"{parent_voice[0].name} " + self.temp_name

    def _make_components(self, duration):
        if self.from_components is False:
            components = self.rhythm_handler(duration)
        else:
            components = self.rhythm_handler
        if self.cluster is True:
            # components.append(abjad.Note("c'16"))
            # opening = abjad.LilyPondLiteral(
            #     r"\afterGrace 15/16 ", site="before"
            # )  # maybe allow fraction to be configurable (cont.)
            # closing = abjad.LilyPondLiteral(
            #     "{ ", site="after"
            # )  # (cont. ^) or simply call rmaker on duration including following leaf?
            # close_grace = abjad.LilyPondLiteral(" }", site="after")
            # target = abjad.select.leaf(components, -2)
            # abjad.attach(opening, target)
            # abjad.attach(closing, target)
            # abjad.attach(close_grace, components[-1])
            target = abjad.select.leaf(components, -1)
            if isinstance(target, abjad.Note):
                p = target.written_pitch
                grace_n = abjad.Note(p, (1, 16))
            elif isinstance(target, abjad.Chord):
                p = target.written_pitches
                grace_n = abjad.Chord(p, (1, 16))
            after_g = abjad.AfterGraceContainer([grace_n])
            abjad.attach(after_g, target)
            components = abjad.Cluster(components)
            overrides = abjad.LilyPondLiteral(
                [
                    r"\override Staff.ClusterSpanner.style = #'ramp",
                    r"\override Staff.ClusterSpanner.layer = #-10",
                    rf"\override Staff.ClusterSpanner.color = {self.cluster_color}",
                ],
                site="before",
            )
            abjad.attach(overrides, components)
        return components


def aftergrace_command(
    notes_string="c'16",
    selector=trinton.selectors.pleaves(),
    slash=False,
    glissando=False,
    invisible=False,
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

        if invisible is True:
            for container in containers:
                first_leaf = abjad.select.leaf(container, 0)
                abjad.override(first_leaf).NoteHead.transparent = True
                literal = abjad.LilyPondLiteral(
                    [
                        r"\once \override Stem.stencil = ##f",
                        r"\once \override Flag.stencil = ##f",
                        r"\once \override NoteHead.no-ledgers = ##t",
                        r"\once \override Accidental.stencil = ##f",
                    ],
                    site="before",
                )
                abjad.attach(literal, first_leaf)

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
