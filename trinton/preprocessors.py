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


def fuse_eighths_preprocessor(groups):
    def preprocessor(divisions):
        def eighths(
            sequence,
            *,
            compound=None,
            remainder=None,
        ):
            assert isinstance(sequence, list), repr(sequence)
            sequence = baca.sequence.split_divisions(
                sequence, [(1, 8)], cyclic=True, compound=compound, remainder=remainder
            )
            return sequence

        duration = abjad.sequence.sum(divisions)
        divisions = [duration]
        divisions = [eighths([_]) for _ in divisions]
        divisions = abjad.sequence.flatten(divisions, depth=-1)
        divisions = abjad.sequence.partition_by_counts(
            divisions, groups, cyclic=True, overhang=True
        )
        return [sum(_) for _ in divisions]

    return preprocessor


def fuse_sixteenths_preprocessor(groups):
    def preprocessor(divisions):
        def eighths(
            sequence,
            *,
            compound=None,
            remainder=None,
        ):
            assert isinstance(sequence, list), repr(sequence)
            sequence = baca.sequence.split_divisions(
                sequence, [(1, 16)], cyclic=True, compound=compound, remainder=remainder
            )
            return sequence

        duration = abjad.sequence.sum(divisions)
        divisions = [duration]
        divisions = [eighths([_]) for _ in divisions]
        divisions = abjad.sequence.flatten(divisions, depth=-1)
        divisions = abjad.sequence.partition_by_counts(
            divisions, groups, cyclic=True, overhang=True
        )
        return [sum(_) for _ in divisions]

    return preprocessor


def thirty_seconds(
    sequence,
    *,
    compound: abjad.typings.Duration = None,
    remainder: int = None,
):
    assert isinstance(sequence, list), repr(sequence)
    sequence = baca.sequence.split_divisions(
        sequence, [(1, 32)], cyclic=True, compound=compound, remainder=remainder
    )
    return sequence


def fuse_thirty_seconds_preprocessor(groups):
    def preprocessor(divisions):
        duration = abjad.sequence.sum(divisions)
        divisions = [duration]
        divisions = [thirty_seconds([_]) for _ in divisions]
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
