import abjad
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


def tuplets():
    def selector(argument):
        selection = abjad.select(argument)

        components = trinton.get_top_level_components_from_leaves(selection)

        out = []

        for component in components:
            if isinstance(component, abjad.Tuplet):
                out.append(component)
            else:
                pass

        return out

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


def select_logical_ties_by_index(indices):
    def selector(argument):
        out = []
        for index in indices:
            out.append(abjad.select.logical_ties(argument)[index])
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


def select_leaves_by_index(indices):
    def selector(argument):
        out = []
        for index in indices:
            out.append(abjad.select.leaf(argument, index))
        return out

    return selector


def patterned_leaf_index_selector(
    indices,
    period,
):
    def selector(argument):
        out = []
        index = []
        pattern = abjad.Pattern(indices=indices, period=period)
        leaves = abjad.select.leaves(argument)
        for i in range(len(leaves)):
            if pattern.matches_index(i, len(leaves)):
                index.append(i)
        for i in index:
            out.append(leaves[i])
        return out

    return selector


def patterned_tie_index_selector(
    indices,
    period,
):
    def selector(argument):
        out = []
        index = []
        pattern = abjad.Pattern(indices=indices, period=period)
        ties = abjad.select.logical_ties(argument)
        for i in range(len(ties)):
            if pattern.matches_index(i, len(ties)):
                index.append(i)
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
        return abjad.select.leaves(argument, grace=True)

    return selector


def exclude_graces():
    def selector(argument):
        return abjad.select.leaves(argument, grace=False)

    return selector
