import abjad
import baca
import evans
import trinton


def fuse_preprocessor(groups):
    def preprocessor(divisions):
        divisions = abjad.sequence.partition_by_counts(
            divisions, groups, cyclic=True, overhang=True
        )
        return [sum(_) for _ in divisions]

    return preprocessor


def fuse_quarters_preprocessor(groups):
    def preprocessor(divisions):
        duration = abjad.sequence.sum(divisions)
        divisions = [duration]
        divisions = [baca.sequence.quarters([_]) for _ in divisions]
        divisions = abjad.sequence.flatten(divisions, depth=-1)
        divisions = abjad.sequence.partition_by_counts(
            divisions, groups, cyclic=True, overhang=True
        )
        return [sum(_) for _ in divisions]

    return preprocessor


def pure_quarters_preprocessor():
    def preprocessor(divisions):
        divisions = [baca.sequence.quarters([_]) for _ in divisions]
        divisions = abjad.sequence.flatten(divisions, depth=-1)
        return divisions

    return preprocessor


def quarters_preprocessor(groups):
    def preprocessor(divisions):
        divisions = [baca.sequence.quarters([_]) for _ in divisions]
        temp = []
        for measure in divisions:
            partitions = abjad.sequence.flatten(measure, depth=-1)
            partitions = abjad.sequence.partition_by_counts(
                partitions,
                (3, 1, 2),
                cyclic=True,
                overhang=True,
            )
            sums = [sum(_) for _ in partitions]
            temp.append(sums)
        divisions = abjad.sequence.flatten(temp, depth=-1)
        return divisions

    return preprocessor
