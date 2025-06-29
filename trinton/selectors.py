import abjad
import baca
import evans
import trinton
from itertools import cycle


def exclude_tuplets():
    def selector(argument):
        selection = abjad.select(argument)

        components = trinton.get_top_level_components_from_leaves(selection)

        out = []

        for component in components:
            if isinstance(component, abjad.Tuplet):
                pass
            else:
                sel = abjad.select(component)
                out.append(sel)

        return out

    return selector


def select_leaves_in_tuplet(pairs, cycle_leaves=True):
    def selector(argument):
        out = []

        if cycle_leaves is True:
            tuplets = abjad.select.tuplets(argument)
        else:
            tuplets = [abjad.select.tuplet(argument, _[0]) for _ in pairs]

        for tuplet, leaf_index in zip(tuplets, cycle(pairs)):
            leaf = abjad.select.leaf(tuplet, leaf_index[-1])
            out.append(leaf)

        return out

    return selector


def tuplets():
    def selector(argument):

        tuplets = abjad.select.tuplets(argument)

        return tuplets

    return selector


def select_tuplets_by_annotation(annotation):
    def selector(argument):
        top_level_components = trinton.get_top_level_components_from_leaves(argument)
        tuplets = abjad.select.tuplets(top_level_components)

        out = []

        for tuplet in tuplets:
            if abjad.get.annotation(tuplet, annotation) is True:
                out.append(tuplet)

        return abjad.select.leaves(out[:])

    return selector


def select_tuplets_by_index(indices):
    def selector(argument):
        out = []

        for index in indices:
            tuplet = abjad.select.tuplet(argument, index)

            out.append(tuplet)

        return out

    return selector


def select_logical_ties_by_index(
    indices, pitched=None, first=False, last=False, grace=None
):
    def selector(argument):
        out = []
        if first is True or last is True:
            if first is True:
                for index in indices:
                    out.append(
                        abjad.select.logical_ties(
                            argument, pitched=pitched, grace=grace
                        )[index][0]
                    )
            if last is True:
                for index in indices:
                    out.append(
                        abjad.select.logical_ties(
                            argument, pitched=pitched, grace=grace
                        )[index][-1]
                    )
        else:
            for index in indices:
                out.append(
                    abjad.select.logical_ties(argument, pitched=pitched, grace=grace)[
                        index
                    ]
                )
        return out

    return selector


def select_leaves_in_tie(tie_indices, leaf_indices):
    def selector(argument):
        out = []
        for index in tie_indices:
            tie = abjad.select.logical_ties(argument)[index]
            for leaf in leaf_indices:
                out.append(abjad.select.leaf(tie, leaf))
        return out

    return selector


def select_leaves_by_index(indices, pitched=None, grace=None):
    def selector(argument):
        out = []
        for index in indices:
            out.append(abjad.select.leaf(argument, index, pitched=pitched, grace=grace))
        return out

    return selector


def patterned_leaf_index_selector(
    indices, period, pitched=None, grace=None, exclude=None
):
    def selector(argument):
        out = []
        index = []
        pattern = abjad.Pattern(indices=indices, period=period)
        leaves = abjad.select.leaves(argument, pitched=pitched, grace=grace)
        if exclude is not None:
            leaves = abjad.select.exclude(leaves, exclude)
        for i in range(len(leaves)):
            if pattern.matches_index(i, len(leaves)):
                index.append(i)
        for i in index:
            out.append(leaves[i])
        return out

    return selector


def patterned_tie_index_selector(
    indices, period, first=False, last=False, pitched=None, grace=None, exclude=None
):
    def selector(argument):
        out = []
        index = []
        pattern = abjad.Pattern(indices=indices, period=period)
        ties = abjad.select.logical_ties(argument, pitched=pitched, grace=grace)
        if exclude is not None:
            ties = abjad.select.exclude(ties, exclude)
        for i in range(len(ties)):
            if pattern.matches_index(i, len(ties)):
                index.append(i)
        if first is True or last is True:
            if first is True:
                for i in index:
                    out.append(ties[i][0])
            if last is True:
                for i in index:
                    out.append(ties[i][-1])
        else:
            for i in index:
                out.append(ties[i])
        return out

    return selector


def group_leaves_by_measure(voice, pitched=None):
    if pitched is not None:
        return abjad.select.group_by_measure(
            abjad.select.leaves(voice, pitched=pitched)
        )
    else:
        return abjad.select.group_by_measure(abjad.select.leaves(voice))


def group_logical_ties_by_measure(voice):
    return abjad.select.group_by_measure(abjad.select.logical_ties(voice))


def grace_selector():
    def selector(argument):
        return baca.select.graces(argument)

    return selector


def exclude_graces():
    def selector(argument):
        return abjad.select.leaves(argument, grace=False)

    return selector


def pleaves(exclude=None, grace=None):
    def selector(argument):
        selections = abjad.select.leaves(argument, pitched=True, grace=grace)
        if grace is True or grace is None:
            selections = abjad.select.leaves(selections)

        if exclude is not None:
            selections = abjad.select.exclude(selections, exclude)

        return selections

    return selector


def make_leaf_selection(score, voice, leaves):
    selection = []
    for leaf in leaves:
        sel = abjad.select.leaf(score[voice], leaf)
        selection.append(sel)
    return selection


def group_selections(voice, leaves, groups=None):
    out = []
    for leaf in leaves:
        out.append(abjad.select.leaf(voice, leaf))
    if groups is None:
        return out
    else:
        new_out = evans.Sequence(out).grouper(groups)
        return new_out


def select_target(voice, measure_number_range=(1, 3), grace=True):
    if len(measure_number_range) == 1:
        indices = [_ - 1 for _ in measure_number_range]
    else:
        revised_range = range(measure_number_range[0] - 1, measure_number_range[1])
        indices = [_ for _ in revised_range]

    parentage = abjad.get.parentage(voice)
    outer_context = parentage.components[-1]
    global_context = outer_context["Global Context"]
    measures = abjad.select.group_by_measure(global_context)

    target_measures = []

    for i in indices:
        target_measures.extend(measures[i])

    target_timespans = [abjad.get.timespan(_) for _ in target_measures]

    start_offset = target_timespans[0].offsets[0]
    stop_offset = target_timespans[-1].offsets[-1]
    relevant_timespan = abjad.Timespan(start_offset, stop_offset)

    out = []

    for component in voice[:]:
        span = abjad.get.timespan(component)
        container = abjad.Container()
        if span.intersects_timespan(relevant_timespan) is True:
            before_grace = abjad.get.before_grace_container(component)
            after_grace = abjad.get.after_grace_container(component)
            if before_grace is not None and grace is True:
                out.append(before_grace)
            out.append(component)
            if after_grace is not None and grace is True:
                out.append(after_grace)

    return out


def logical_ties(
    first=False,
    all_except_first=False,
    last=False,
    pitched=None,
    exclude=None,
    grace=None,
):
    def selector(argument):
        ties = abjad.select.logical_ties(argument, pitched=pitched, grace=grace)
        if exclude is not None:
            ties = abjad.select.exclude(ties, exclude)
        if first is True:
            out = []
            for tie in ties:
                out.append(tie[0])
            return out
        if all_except_first is True:
            out = []
            for tie in ties:
                relevant_leaves = tie[1:]
                for leaf in relevant_leaves:
                    out.append(leaf)
            return out
        if last is True:
            out = []
            for tie in ties:
                out.append(tie[-1])
            return out
        else:
            return ties

    return selector


def group_selections(selector, groups):
    def group(argument):
        selections = selector(argument)
        grouped = evans.Sequence(selections).grouper(groups)
        return grouped

    return group


def ranged_selector(ranges, nested=False, pitched=None, grace=None):
    def selector(argument):
        out = []
        for range in ranges:
            selection = [
                abjad.select.leaf(argument, _, pitched=pitched, grace=grace)
                for _ in range
            ]
            out.append(selection)
        if nested is True:
            return out
        else:
            return selection

    return selector


def notehead_selector(chord_indices, head_indices_lists):
    def selector(argument):

        chords = abjad.select.chords(argument)

        out = []

        for chord_index, head_indices in zip(chord_indices, head_indices_lists):
            chord = chords[chord_index]

            note_heads = chord.note_heads

            for head_index in head_indices:
                head = note_heads[head_index]
                out.append(head)

        return out

    return selector


def durational_selector(
    durations, preselector=abjad.select.logical_ties, preprolated=True, first=False
):
    def selector(argument):
        selections = preselector(argument)
        out = []
        for duration in durations:
            for selection in selections:
                selection_duration = abjad.get.duration(
                    selection, preprolated=preprolated
                )
                if selection_duration == duration:
                    if first is True:
                        leaf = abjad.select.leaf(selection, 0)
                        out.append(leaf)
                    else:
                        out.append(selection)

        return out

    return selector


def pitched_selector(pitches):
    def selector(argument):
        out = []
        for pitch in pitches:
            for leaf in abjad.select.leaves(argument, pitched=True):
                if isinstance(leaf, abjad.Chord):
                    pass
                else:
                    written_pitch = leaf.written_pitch
                    pitch_class = written_pitch.pitch_class
                    if pitch_class == abjad.NamedPitchClass(pitch):
                        out.append(leaf)
        return out

    return selector


# def group_by_duration(durations, preselector=None, preprolated=True):
#     def selector(argument):
#         if preselector is not None:
#             selections = preselector(argument)
#         else:
#             selections = argument
#
#         out = []
#         group = []
#         for selection in abjad.select.components(selections, abjad.Note):
#             group_duration = abjad.get.duration(group, preprolated=preprolated)
#             relevant_duration = durations[0]
#             if isinstance(relevant_duration, abjad.TimeSignature):
#                 relevant_duration = relevant_duration.duration
#             else:
#                 relevant_duration = relevant_duration
#
#             if group_duration == relevant_duration:
#                 out_group = []
#                 for selection in group:
#                     out_group.append(selection)
#                 out.append(out_group)
#                 # group.clear()
#                 durations.pop(0)
#                 group.append(selection)
#
#             else:
#                 group.append(selection)
#
#             print("")
#             print(f"selection: {selection}")
#             print("")
#             print(f"relevant duration: {relevant_duration}")
#             print("")
#             print(f"group duration: {group_duration}")
#             print("")
#             print(f"group contents: {group}")
#             print("")
#
#         return out
#     return selector
