import abjad
import baca
import evans
import trinton
from abjadext import rmakers
from fractions import Fraction
import itertools
import quicktions
import numpy
import datetime
import dataclasses
import typing
import pathlib
import os


def get_top_level_components_from_leaves(leaves):
    out = []
    for leaf in leaves:
        parent = abjad.get.parentage(leaf).parent
        if isinstance(parent, (abjad.Voice, abjad.Staff)):
            if leaf not in out:
                out.append(leaf)
        else:
            sub_out = get_top_level_components_from_leaves([parent])
            for sub_leaf in sub_out:
                if sub_leaf not in out:
                    out.append(sub_leaf)
    return out


# rewriting


def rewrite_meter_without_splitting(target):
    global_skips = [_ for _ in abjad.select.leaves(target["Global Context"])]
    sigs = []
    for skip in global_skips:
        for indicator in abjad.get.indicators(skip):
            if isinstance(indicator, abjad.TimeSignature):
                sigs.append(indicator)
    for voice in abjad.select.components(target["Staff Group"], abjad.Voice):
        voice_dur = abjad.get.duration(voice)
        time_signatures = sigs
        durations = [_.duration for _ in time_signatures]
        sig_dur = sum(durations)
        assert voice_dur == sig_dur, (voice_dur, sig_dur)
        shards = abjad.select.group_by_measure(abjad.select.leaves(voice[:]))
        for i, shard in enumerate(shards):
            if voice.name == "violin 1 voice":
                print(i)
            if not all(
                isinstance(leaf, (abjad.Rest, abjad.MultimeasureRest, abjad.Skip))
                for leaf in abjad.select.leaves(shard)
            ):
                time_signature = sigs[i]
                top_level_components = get_top_level_components_from_leaves(shard)
                shard = top_level_components
                inventories = [
                    x
                    for x in enumerate(
                        abjad.Meter(time_signature.pair).depthwise_offset_inventory
                    )
                ]
                if time_signature.denominator == 4:
                    abjad.Meter.rewrite_meter(
                        shard,
                        time_signature,
                        boundary_depth=inventories[-1][0],
                        rewrite_tuplets=False,
                    )
                else:
                    abjad.Meter.rewrite_meter(
                        shard,
                        time_signature,
                        boundary_depth=inventories[-2][0],
                        rewrite_tuplets=False,
                    )


def rewrite_meter(target):
    print("Rewriting meter ...")
    global_skips = [_ for _ in abjad.select.leaves(target["Global Context"])]
    sigs = []
    for skip in global_skips:
        for indicator in abjad.get.indicators(skip):
            if isinstance(indicator, abjad.TimeSignature):
                sigs.append(indicator)
    for voice in abjad.select.components(target["Staff Group"], abjad.Voice):
        voice_dur = abjad.get.duration(voice)
        time_signatures = sigs  # [:-1]
        durations = [_.duration for _ in time_signatures]
        sig_dur = sum(durations)
        assert voice_dur == sig_dur, (voice_dur, sig_dur)
        shards = abjad.mutate.split(voice[:], durations)
        for i, shard in enumerate(shards):
            time_signature = sigs[i]
            inventories = [
                x
                for x in enumerate(
                    abjad.Meter(time_signature.pair).depthwise_offset_inventory
                )
            ]
            if time_signature.denominator == 4:
                abjad.Meter.rewrite_meter(
                    shard,
                    time_signature,
                    boundary_depth=inventories[-1][0],
                    rewrite_tuplets=False,
                )
            else:
                abjad.Meter.rewrite_meter(
                    shard,
                    time_signature,
                    boundary_depth=inventories[-2][0],
                    rewrite_tuplets=False,
                )


def rewrite_meter_by_voice(score, voice_indeces):
    print("Rewriting meter ...")
    global_skips = [_ for _ in abjad.select.leaves(score["Global Context"])]
    sigs = []
    for skip in global_skips:
        for indicator in abjad.get.indicators(skip):
            if isinstance(indicator, abjad.TimeSignature):
                sigs.append(indicator)
    voices = []
    for voice in voice_indeces:
        voices.append(abjad.select.components(score["Staff Group"], abjad.Voice)[voice])
    for voice in voices:
        voice_dur = abjad.get.duration(voice)
        time_signatures = sigs
        durations = [_.duration for _ in time_signatures]
        sig_dur = sum(durations)
        assert voice_dur == sig_dur, (voice_dur, sig_dur)
        shards = abjad.mutate.split(voice[:], durations)
        for i, shard in enumerate(shards):
            time_signature = sigs[i]
            inventories = [
                x
                for x in enumerate(
                    abjad.Meter(time_signature.pair).depthwise_offset_inventory
                )
            ]
            if time_signature.denominator == 4:
                abjad.Meter.rewrite_meter(
                    shard,
                    time_signature,
                    boundary_depth=inventories[-1][0],
                    rewrite_tuplets=False,
                )
            else:
                abjad.Meter.rewrite_meter(
                    shard,
                    time_signature,
                    boundary_depth=inventories[-2][0],
                    rewrite_tuplets=False,
                )


def rewrite_meter_by_measure(score, measures):
    print("Rewriting meter ...")
    global_skips = [_ for _ in abjad.select.leaves(score["Global Context"])]
    sigs = []
    skips = []
    for measure in measures:
        skips.append(global_skips[measure - 1])
    for skip in skips:
        for indicator in abjad.get.indicators(skip):
            if isinstance(indicator, abjad.TimeSignature):
                sigs.append(indicator)
    for voice in abjad.select.components(score["Staff Group"], abjad.Voice):
        all_measures = abjad.select.group_by_measure(abjad.select.leaves(voice))
        voice_sel = [all_measures[_ - 1] for _ in measures]
        voice_dur = abjad.get.duration(voice_sel)
        time_signatures = sigs  # [:-1]
        durations = [_.duration for _ in time_signatures]
        sig_dur = sum(durations)
        assert voice_dur == sig_dur, (voice_dur, sig_dur)
        all_shards = abjad.mutate.split(voice[:], durations)
        shards = []
        shards.append(all_shards[measures[0] - 1 : measures[-1]])
        for i, shard in enumerate(shards[0]):
            time_signature = sigs[i]
            inventories = [
                x
                for x in enumerate(
                    abjad.Meter(time_signature.pair).depthwise_offset_inventory
                )
            ]
            if time_signature.denominator == 4:
                abjad.Meter.rewrite_meter(
                    shard,
                    time_signature,
                    boundary_depth=inventories[-1][0],
                    rewrite_tuplets=False,
                )
            else:
                abjad.Meter.rewrite_meter(
                    shard,
                    time_signature,
                    boundary_depth=inventories[-2][0],
                    rewrite_tuplets=False,
                )


# beaming


def beam_meter(components, meter, offset_depth, include_rests=True):
    offsets = meter.depthwise_offset_inventory[offset_depth]
    offset_pairs = []
    for i, _ in enumerate(offsets[:-1]):
        offset_pair = [offsets[i], offsets[i + 1]]
        offset_pairs.append(offset_pair)
    initial_offset = abjad.get.timespan(components[0]).start_offset
    for i, pair in enumerate(offset_pairs):
        for i_, item in enumerate(pair):
            offset_pairs[i][i_] = item + initial_offset
    offset_timespans = [
        abjad.Timespan(start_offset=pair[0], stop_offset=pair[1])
        for pair in offset_pairs
    ]

    tup_list = [tup for tup in abjad.select.components(components, abjad.Tuplet)]
    for t in tup_list:
        if isinstance(abjad.get.parentage(t).components[1], abjad.Tuplet) is False:
            first_leaf = abjad.select.leaf(t, 0)
            if not hasattr(first_leaf._overrides, "Beam"):
                abjad.beam(
                    t[:],
                    beam_rests=include_rests,
                    stemlet_length=0.75,
                    beam_lone_notes=False,
                    selector=lambda _: abjad.select.leaves(_, grace=False),
                )
        else:
            continue

    non_tup_list = []
    for leaf in abjad.select.leaves(components):
        if isinstance(abjad.get.parentage(leaf).components[1], abjad.Tuplet) is False:
            non_tup_list.append(leaf)

    beamed_groups = []
    for i in enumerate(offset_timespans):
        beamed_groups.append([])

    for i, span in enumerate(offset_timespans):
        for group in abjad.select.group_by(
            abjad.select.leaves(non_tup_list[:]),
            predicate=lambda x: abjad.get.timespan(x).happens_during_timespan(span),
        ):
            if abjad.get.timespan(group).happens_during_timespan(span) is True:
                beamed_groups[i].append(group[:])

    for subgroup in beamed_groups:
        subgrouper = abjad.select.group_by_contiguity(subgroup)
        for beam_group in subgrouper:
            # if not all(isinstance(leaf, abjad.Rest) for leaf in beam_group)
            abjad.beam(
                beam_group[:],
                beam_rests=include_rests,
                stemlet_length=0.75,
                beam_lone_notes=False,
                selector=lambda _: abjad.select.leaves(_, grace=False),
            )


def beam_score_without_splitting(target):
    global_skips = [_ for _ in abjad.select.leaves(target["Global Context"])]
    sigs = []
    for skip in global_skips:
        for indicator in abjad.get.indicators(skip):
            if isinstance(indicator, abjad.TimeSignature):
                sigs.append(indicator)
    print("Beaming meter ...")
    for voice in abjad.iterate.components(target["Staff Group"], abjad.Voice):
        measures = abjad.select.group_by_measure(abjad.select.leaves(voice[:]))
        for i, shard in enumerate(measures):
            top_level_components = get_top_level_components_from_leaves(shard)
            shard = top_level_components
            met = abjad.Meter(sigs[i].pair)
            inventories = [
                x
                for x in enumerate(abjad.Meter(sigs[i].pair).depthwise_offset_inventory)
            ]
            if sigs[i].denominator == 4:
                beam_meter(
                    components=shard[:],
                    meter=met,
                    offset_depth=inventories[-1][0],
                    include_rests=False,
                )
            else:
                beam_meter(
                    components=shard[:],
                    meter=met,
                    offset_depth=inventories[-2][0],
                    include_rests=False,
                )
    for trem in abjad.select.components(target, abjad.TremoloContainer):
        if abjad.StartBeam() in abjad.get.indicators(trem[0]):
            abjad.detach(abjad.StartBeam(), trem[0])
        if abjad.StopBeam() in abjad.get.indicators(trem[-1]):
            abjad.detach(abjad.StopBeam(), trem[-1])


def beam_score(target):
    global_skips = [_ for _ in abjad.select.leaves(target["Global Context"])]
    sigs = []
    for skip in global_skips:
        for indicator in abjad.get.indicators(skip):
            if isinstance(indicator, abjad.TimeSignature):
                sigs.append(indicator)
    print("Beaming meter ...")
    for voice in abjad.iterate.components(target["Staff Group"], abjad.Voice):
        for i, shard in enumerate(abjad.mutate.split(voice[:], sigs)):
            met = abjad.Meter(sigs[i].pair)
            inventories = [
                x
                for x in enumerate(abjad.Meter(sigs[i].pair).depthwise_offset_inventory)
            ]
            if sigs[i].denominator == 4:
                beam_meter(
                    components=shard[:],
                    meter=met,
                    offset_depth=inventories[-1][0],
                    include_rests=False,
                )
            else:
                beam_meter(
                    components=shard[:],
                    meter=met,
                    offset_depth=inventories[-2][0],
                    include_rests=False,
                )
    for trem in abjad.select.components(target, abjad.TremoloContainer):
        if abjad.StartBeam() in abjad.get.indicators(trem[0]):
            abjad.detach(abjad.StartBeam(), trem[0])
        if abjad.StopBeam() in abjad.get.indicators(trem[-1]):
            abjad.detach(abjad.StopBeam(), trem[-1])


def beam_score_by_voice(score, voices):
    global_skips = [_ for _ in abjad.select.leaves(score["Global Context"])]
    sigs = []
    for skip in global_skips:
        for indicator in abjad.get.indicators(skip):
            if isinstance(indicator, abjad.TimeSignature):
                sigs.append(indicator)
    print("Beaming meter ...")
    for voice in voices:
        for i, shard in enumerate(abjad.mutate.split(voice[:], sigs)):
            met = abjad.Meter(sigs[i].pair)
            inventories = [
                x
                for x in enumerate(abjad.Meter(sigs[i].pair).depthwise_offset_inventory)
            ]
            if sigs[i].denominator == 4:
                beam_meter(
                    components=shard[:],
                    meter=met,
                    offset_depth=inventories[-1][0],
                    include_rests=False,
                )
            else:
                beam_meter(
                    components=shard[:],
                    meter=met,
                    offset_depth=inventories[-2][0],
                    include_rests=False,
                )
    for trem in abjad.select.components(score, abjad.TremoloContainer):
        if abjad.StartBeam() in abjad.get.indicators(trem[0]):
            abjad.detach(abjad.StartBeam(), trem[0])
        if abjad.StopBeam() in abjad.get.indicators(trem[-1]):
            abjad.detach(abjad.StopBeam(), trem[-1])


def rebar(
    score,
    global_context,
    selector_function,
    replacement_signatures,
    boundary_depth=None,
    rebeam=None,
):
    target = selector_function(global_context)
    indicators = [_ for _ in abjad.get.indicators(abjad.select.leaf(target, 0))]
    new_sigs = [abjad.TimeSignature(_) for _ in replacement_signatures]
    if boundary_depth is not None:
        for voice in abjad.select.components(score, abjad.Voice):
            rewrite_meter_command = evans.RewriteMeterCommand(
                boundary_depth=boundary_depth
            )
            voice_target = selector_function(voice)
            target_copy = abjad.mutate.copy(voice_target[:])
            metered_staff = rmakers.wrap_in_time_signature_staff(target_copy, new_sigs)
            rewrite_meter_command(metered_staff)
            selections = abjad.mutate.eject_contents(metered_staff)
            abjad.mutate.replace(voice_target, selections)

    for voice in abjad.select.components(score, abjad.Voice):
        rest_target = selector_function(voice)
        for leaf in abjad.select.leaves(rest_target):
            if isinstance(leaf, abjad.Skip):
                skip_duration = abjad.get.duration(leaf)
                new_rest = abjad.MultimeasureRest(multiplier=skip_duration)
                rest_indicators = [_ for _ in abjad.get.indicators(leaf)]
                for indicator in rest_indicators:
                    abjad.detach(indicator, leaf)
                    abjad.attach(indicator, new_rest)
                abjad.mutate.replace(leaf, new_rest)

    new_leaves = []

    for pair in replacement_signatures:
        signature = abjad.TimeSignature(pair)
        skip = abjad.Skip((1, 1), multiplier=abjad.Multiplier(pair))
        abjad.attach(signature, skip)
        new_leaves.append(skip)

    for indicator in indicators:
        if isinstance(indicator, abjad.TimeSignature):
            pass
        else:
            abjad.detach(indicator, abjad.select.leaf(target, 0))
            abjad.attach(indicator, abjad.select.leaf(new_leaves, 0))

    first_duration = abjad.get.duration(target)
    second_duration = abjad.get.duration(new_leaves)

    if first_duration != second_duration:
        raise Exception(
            "New time signatures must equal the total duration of the signatures they are to replace"
        )

    abjad.mutate.replace(target, new_leaves)

    if rebeam is not None:
        rebeam_voices = [selector_function(_) for _ in rebeam]
        for target in rebeam_voices:
            print("Rebeaming ...")
            for leaf in abjad.select.leaves(target):
                abjad.detach(abjad.StartBeam, leaf)
                abjad.detach(abjad.StopBeam, leaf)
            if len(new_sigs) > 1:
                measures = abjad.select.group_by_measure(target)
            else:
                measures = [target]
            for i, shard in enumerate(measures):
                top_level_components = trinton.get_top_level_components_from_leaves(
                    shard
                )
                shard = top_level_components
                met = abjad.Meter(new_sigs[i].pair)
                inventories = [
                    x
                    for x in enumerate(
                        abjad.Meter(new_sigs[i].pair).depthwise_offset_inventory
                    )
                ]
                if new_sigs[i].denominator == 4:
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
        for trem in abjad.select.components(target, abjad.TremoloContainer):
            if abjad.StartBeam() in abjad.get.indicators(trem[0]):
                abjad.detach(abjad.StartBeam(), trem[0])
            if abjad.StopBeam() in abjad.get.indicators(trem[-1]):
                abjad.detach(abjad.StopBeam(), trem[-1])


def remove_redundant_time_signatures(score):
    global_context = score["Global Context"]
    target = abjad.select.leaves(global_context)
    target = abjad.select.exclude(target, [-1])
    for leaf in target:
        next_leaf = abjad.select.with_next_leaf(leaf)[-1]
        ts_1 = abjad.get.indicator(leaf, abjad.TimeSignature)
        ts_2 = abjad.get.indicator(next_leaf, abjad.TimeSignature)

        if ts_1.pair == ts_2.pair:
            abjad.attach(
                abjad.LilyPondLiteral(
                    r"\once \override Score.TimeSignature.stencil = ##f",
                    site="before",
                ),
                next_leaf,
            )


def rewrite_meter_command(boundary_depth=-2):
    def rewrite(argument):
        parentage = abjad.get.parentage(abjad.select.leaf(argument, 0))
        outer_context = parentage.components[-1]
        global_context = outer_context["Global Context"]
        argument_timespans = [abjad.get.timespan(_) for _ in argument]
        start_offset = argument_timespans[0].offsets[0]
        stop_offset = argument_timespans[-1].offsets[-1]
        relevant_timespan = abjad.Timespan(start_offset, stop_offset)

        relevant_leaves = []

        for leaf in abjad.select.leaves(global_context):
            span = abjad.get.timespan(leaf)
            if span.intersects_timespan(relevant_timespan) is True:
                relevant_leaves.append(leaf)

        signature_instances = [
            abjad.get.indicator(_, abjad.TimeSignature) for _ in relevant_leaves
        ]

        container = abjad.Container()

        container.extend(abjad.mutate.copy(argument))

        tuplets = abjad.select.tuplets(container)

        tuplet_copies = []
        if len(tuplets) > 0:
            for tuplet in tuplets:
                tuplet_parent = abjad.get.parentage(tuplet).parent
                if isinstance(tuplet_parent, abjad.Tuplet):
                    pass

                else:
                    tuplet_first_leaf = abjad.select.leaf(tuplet, 0)
                    tuplet_previous_leaf = abjad.select.with_previous_leaf(
                        tuplet_first_leaf
                    )[0]
                    if abjad.get.has_indicator(tuplet_previous_leaf, abjad.Tie):
                        abjad.detach(abjad.Tie, tuplet_previous_leaf)
                        abjad.attach(
                            abjad.Markup(r'\markup {"tie previous leaf"}'),
                            tuplet_first_leaf,
                        )
                    tuplet_duration = abjad.get.duration(tuplet)
                    leaf = abjad.Note("c''1", multiplier=tuplet_duration)
                    tuplet_last_leaf = abjad.select.leaf(tuplet, -1)
                    tuplet_copy = abjad.mutate.copy(tuplet)
                    if abjad.get.has_indicator(tuplet_last_leaf, abjad.Tie):
                        abjad.attach(abjad.Tie(), abjad.select.leaf(tuplet_copy, -1))
                    tuplet_copies.append(tuplet_copy)
                    abjad.mutate.replace(tuplet, leaf)

        container_contents = abjad.mutate.eject_contents(container)

        metered_staff = rmakers.wrap_in_time_signature_staff(
            container_contents, signature_instances
        )

        rmakers.rewrite_meter(metered_staff, boundary_depth=boundary_depth)

        leaves = abjad.select.leaves(metered_staff)
        for leaf in leaves:
            abjad.detach(abjad.StartBeam, leaf)
            abjad.detach(abjad.StopBeam, leaf)

        placeholders = []

        for leaf in abjad.select.leaves(metered_staff, pitched=True):
            if isinstance(leaf, abjad.Chord):
                pass

            else:
                if leaf.written_pitch.number == 12:
                    placeholders.append(leaf)

        for tie, tuplet in zip(abjad.select.logical_ties(placeholders), tuplet_copies):
            abjad.mutate.replace(tie, tuplet)

        for leaf in abjad.select.leaves(metered_staff):
            if abjad.get.has_indicator(leaf, abjad.Markup):
                previous_leaf = abjad.select.with_previous_leaf(leaf)[0]
                abjad.detach(abjad.Markup, leaf)
                abjad.attach(abjad.Tie(), previous_leaf)

        selections = abjad.mutate.eject_contents(metered_staff)
        abjad.mutate.replace(argument, selections)

    return rewrite
