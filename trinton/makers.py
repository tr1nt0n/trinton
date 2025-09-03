import abjad
import baca
import evans
import trinton
from abjadext import rmakers
from fractions import Fraction
from itertools import cycle
import quicktions
import math
import numpy
import datetime
import dataclasses
import struct
import typing
import pathlib
import os
import sys
import wave

# time signatures


def write_time_signatures(ts, target):
    for pair in ts:
        signature = abjad.TimeSignature(pair)
        skip = abjad.Skip((1, 1), multiplier=abjad.Multiplier(pair))
        abjad.attach(signature, skip)
        target.append(skip)


def make_ts_pair_list(numerators, denominators):
    out = []
    for numerator, denominator in zip(numerators, denominators):
        pair = (numerator, denominator)
        out.append(pair)

    return out


# empty score


def extract_instrument_name(instrument_class):
    instrument_string = str(instrument_class)

    out = ""

    for _ in instrument_string:
        if _ == "(":
            break

        out += _

    return out.lower()


def make_score_template(
    instruments,
    groups,
    outer_staff="StaffGroup",
    inner_staff=["GrandStaff"],
    staff_types=None,
):
    name_counts = {extract_instrument_name(_): 1 for _ in instruments}
    sub_group_counter = 1
    score = abjad.Score(
        [
            abjad.Staff(name="Global Context", lilypond_type="TimeSignatureContext"),
            abjad.StaffGroup(name="Staff Group", lilypond_type=outer_staff),
        ],
        name="Score",
    )
    grouped_voices = evans.Sequence(instruments).grouper(groups)
    if staff_types is None:
        staff_types = []
        for item in grouped_voices:
            if isinstance(item, list):
                staff_types.append(["Staff" for _ in item])
            else:
                staff_types.append("Staff")
    if len(inner_staff) == 1:
        inner_staff = [inner_staff[0] for _ in instruments]
    else:
        inner_staff = inner_staff

    for item, type, group in zip(grouped_voices, staff_types, inner_staff):
        if isinstance(item, list):
            sub_group = abjad.StaffGroup(
                name=f"sub group {sub_group_counter}",
                lilypond_type=inner_staff[sub_group_counter],
            )
            sub_group_counter += 1
            for sub_item, sub_type in zip(item, type):
                if 1 < instruments.count(sub_item):
                    name_string = f"{extract_instrument_name(sub_item)} {name_counts[extract_instrument_name(sub_item)]}"
                else:
                    name_string = f"{extract_instrument_name(sub_item)}"

                if sub_type != "TabStaff":
                    staff = abjad.Staff(
                        [
                            abjad.Voice(
                                name=f"{name_string} voice",
                            ),
                        ],
                        name=f"{name_string} staff",
                        lilypond_type=sub_type,
                    )
                else:
                    staff = abjad.Staff(
                        name=f"{name_string} staff",
                        lilypond_type=sub_type,
                    )
                sub_group.append(staff)
                name_counts[extract_instrument_name(sub_item)] += 1
            score["Staff Group"].append(sub_group)
        else:
            if 1 < instruments.count(item):
                name_string = f"{extract_instrument_name(item)} {name_counts[extract_instrument_name(item)]}"
            else:
                name_string = f"{extract_instrument_name(item)}"
            staff = abjad.Staff(
                [
                    abjad.Voice(
                        name=f"{name_string} voice",
                    ),
                ],
                name=f"{name_string} staff",
                lilypond_type=type,
            )
            score["Staff Group"].append(staff)
            name_counts[extract_instrument_name(item)] += 1
    return score


def make_empty_score(
    instruments,
    groups,
    time_signatures,
    outer_staff="StaffGroup",
    inner_staff=["GrandStaff"],
    staff_types=None,
    filler=abjad.Skip,
):
    score = make_score_template(
        instruments=instruments,
        groups=groups,
        outer_staff=outer_staff,
        inner_staff=inner_staff,
        staff_types=staff_types,
    )

    trinton.write_time_signatures(ts=time_signatures, target=score["Global Context"])

    for staff in abjad.select.components(score["Staff Group"], abjad.Staff):
        voices = abjad.select.components(staff, abjad.Voice)
        if len(voices) > 0:
            for voice in voices:
                if filler == abjad.Rest:
                    for time_signature in time_signatures:
                        if time_signature[0] % 9 != 0:
                            if (
                                time_signature[0] % 3 == 0
                                or time_signature[0] % 7 == 0
                                or trinton.is_power_of(a=time_signature[0], b=2) is True
                            ):
                                voice.append(filler(time_signature))
                            else:
                                if (
                                    time_signature[0] % 5 == 0
                                    and time_signature[0] != 15
                                ):
                                    numerator_list = []
                                    for _ in range(time_signature[0]):
                                        if sum(numerator_list) == time_signature[0]:
                                            pass
                                        else:
                                            numerator_list.append(3)
                                            numerator_list.append(2)
                                    for _ in numerator_list:
                                        voice.append(filler((_, time_signature[-1])))
                                else:
                                    first_rest = (3, time_signature[-1])
                                    voice.append(filler(first_rest))
                                    remainder = time_signature[0] - 3
                                    gap_range = int(remainder / 2)
                                    for _ in range(gap_range):
                                        voice.append(filler((2, time_signature[-1])))

                        if time_signature[0] % 9 == 0:
                            numerator_list = []
                            for _ in range(time_signature[0]):
                                if sum(numerator_list) == time_signature[0]:
                                    pass
                                else:
                                    numerator_list.append(3)
                            for _ in numerator_list:
                                voice.append(filler((_, time_signature[-1])))

                else:
                    for measure_filler in [
                        filler((1, 1), multiplier=_) for _ in time_signatures
                    ]:
                        voice.append(measure_filler)
        else:
            if filler == abjad.Rest:
                for time_signature in time_signatures:
                    if time_signature[0] % 9 != 0:
                        if (
                            time_signature[0] % 3 == 0
                            or time_signature[0] % 7 == 0
                            or trinton.is_power_of(a=time_signature[0], b=2) is True
                        ):
                            staff.append(filler(time_signature))
                        else:
                            if time_signature[0] % 5 == 0 and time_signature[0] != 15:
                                numerator_list = []
                                for _ in range(time_signature[0]):
                                    if sum(numerator_list) == time_signature[0]:
                                        pass
                                    else:
                                        numerator_list.append(3)
                                        numerator_list.append(2)
                                for _ in numerator_list:
                                    staff.append(filler((_, time_signature[-1])))
                            else:
                                first_rest = (3, time_signature[-1])
                                voice.append(filler(first_rest))
                                remainder = time_signature[0] - 3
                                gap_range = int(remainder / 2)
                                for _ in range(gap_range):
                                    staff.append(filler((2, time_signature[-1])))

                    if time_signature[0] % 9 == 0:
                        numerator_list = []
                        for _ in range(time_signature[0]):
                            if sum(numerator_list) == time_signature[0]:
                                pass
                            else:
                                numerator_list.append(3)
                        for _ in numerator_list:
                            staff.append(filler((_, time_signature[-1])))
            else:
                for measure_filler in [
                    filler((1, 1), multiplier=_) for _ in time_signatures
                ]:
                    staff.append(measure_filler)

    return score


# making rhythms


def make_rhythm_selections(rmaker, rmaker_commands):
    container = abjad.Container(rmaker)
    for command in rmaker_commands:
        command(container)
    music = abjad.mutate.eject_contents(container)
    return music


def append_rhythm_selections(voice, score, selections):
    relevant_voice = score[voice]
    for selection in selections:
        relevant_voice.append(selection)
    return selections


def make_and_append_rhythm_selections(score, voice_name, rmaker, rmaker_commands):
    def make_rhythm():
        container = abjad.Container(rmaker)
        for command in rmaker_commands:
            command(container)
        music = abjad.mutate.eject_contents(container)
        return music

    selections = make_rhythm()
    relevant_voice = score[voice_name]
    for selection in selections:
        relevant_voice.append(selection)
    return selections


def append_rests(score, voice, rests):
    for rest in rests:
        score[voice].append(rest)


def handwrite(score, voice, durations, pitch_list=None):
    def make_rhythm(divisions):
        nested_music = rmakers.note(divisions)
        container = abjad.Container(nested_music)
        music = abjad.mutate.eject_contents(container)
        return music

    sel = make_rhythm(divisions=durations)

    container = abjad.Container(sel)

    if pitch_list is not None:
        handler = evans.PitchHandler(pitch_list=pitch_list, forget=False)

        handler(abjad.select.leaves(container[:]))

        trinton.append_rhythm_selections(
            voice=voice, score=score, selections=container[:]
        )

    else:
        trinton.append_rhythm_selections(
            voice=voice, score=score, selections=container[:]
        )


def make_rhythms(
    voice,
    time_signature_indices,
    rmaker,
    commands=None,
    rewrite_meter=None,
    preprocessor=None,
):
    def rhythm_selections(divisions):
        commands_ = [
            *commands,
            trinton.treat_tuplets(),
        ]

        new_divisions = divisions
        if preprocessor is not None:
            new_divisions = [abjad.Duration(_.pair) for _ in new_divisions]
            new_divisions = preprocessor(new_divisions)
        nested_music = rmaker(new_divisions)
        container = abjad.Container(nested_music)
        for command in commands_:
            command(container)
        if rewrite_meter is not None:
            meter_command = evans.RewriteMeterCommand(boundary_depth=rewrite_meter)
            metered_staff = rmakers.wrap_in_time_signature_staff(
                container[:], divisions
            )
            meter_command(metered_staff)
            music = abjad.mutate.eject_contents(metered_staff)
        else:
            music = abjad.mutate.eject_contents(container)

        return music

    parentage = abjad.get.parentage(voice)
    outer_context = parentage.components[-1]
    global_context = outer_context["Global Context"]
    relevant_leaves = [global_context[i] for i in time_signature_indices]
    signature_instances = [
        abjad.get.indicator(_, abjad.TimeSignature) for _ in relevant_leaves
    ]
    new_selections = rhythm_selections(signature_instances)
    container = abjad.Container()
    if isinstance(new_selections, list):
        container.extend(new_selections)
    else:
        container.append(new_selections)
    leaves = abjad.select.leaves(voice)
    grouped_leaves = abjad.select.group_by_measure(leaves)
    relevant_groups = abjad.select.get(grouped_leaves, time_signature_indices)
    target_leaves = abjad.select.leaves(relevant_groups)
    abjad.mutate.replace(target_leaves, container[:])


def music_command(
    voice,
    measures,
    rmaker,
    rmaker_commands=None,
    rewrite_meter=None,
    non_power_of_two=False,
    preprocessor=None,
    pitch_handler=None,
    attachment_function=None,
):
    def rhythm_selections(divisions):
        commands_ = [
            *rmaker_commands,
            trinton.treat_tuplets(non_power_of_two=non_power_of_two),
        ]

        new_divisions = divisions
        if preprocessor is not None:
            new_divisions = [abjad.Duration(_.pair) for _ in new_divisions]
            new_divisions = preprocessor(new_divisions)
        nested_music = rmaker(new_divisions)
        container = abjad.Container(nested_music)
        for command in commands_:
            command(container)
        if rewrite_meter is not None:
            meter_command = evans.RewriteMeterCommand(boundary_depth=rewrite_meter)
            metered_staff = rmakers.wrap_in_time_signature_staff(
                container[:], divisions
            )
            meter_command(metered_staff)
            music = abjad.mutate.eject_contents(metered_staff)
        else:
            music = abjad.mutate.eject_contents(container)

        return music

    parentage = abjad.get.parentage(voice)
    outer_context = parentage.components[-1]
    global_context = outer_context["Global Context"]
    time_signature_indices = [_ - 1 for _ in measures]
    relevant_leaves = [global_context[i] for i in time_signature_indices]
    signature_instances = [
        abjad.get.indicator(_, abjad.TimeSignature) for _ in relevant_leaves
    ]
    new_selections = rhythm_selections(signature_instances)
    container = abjad.Container()
    if isinstance(new_selections, list):
        container.extend(new_selections)
    else:
        container.append(new_selections)

    if pitch_handler is not None:
        pitch_handler(container)

    if attachment_function is not None:
        attachment_function([*container])

    leaves = abjad.select.leaves(voice)
    grouped_leaves = abjad.select.group_by_measure(leaves)
    relevant_groups = abjad.select.get(grouped_leaves, time_signature_indices)
    target_leaves = abjad.select.leaves(relevant_groups)
    abjad.mutate.replace(target_leaves, container[:])


def replace_with_rhythm_selection(rhythmhandler, selector, preprolated=True):
    def replace(argument):
        selection = selector(argument)
        indicators = abjad.get.indicators(abjad.select.leaf(selection, 0))
        duration = abjad.get.duration(selection, preprolated=preprolated)
        rhythm_selections = rhythmhandler([duration])
        for indicator in indicators:
            abjad.attach(indicator, abjad.select.leaf(rhythm_selections, 0))
        rmakers.unbeam(rhythm_selections)
        abjad.mutate.replace(selection, rhythm_selections)

    return replace


def iteratively_replace_with_rhythm_selection(
    rhythmhandler, selector, preprolated=True
):
    def replace(argument):
        selections = selector(argument)
        for selection in selections:
            indicators = abjad.get.indicators(abjad.select.leaf(selection, 0))
            duration = abjad.get.duration(selection, preprolated=preprolated)
            rhythm_selections = rhythmhandler([duration])
            rmakers.unbeam(rhythm_selections)
            print("")
            print(rhythm_selections)
            print("")
            abjad.mutate.replace(selection, rhythm_selections)

    return replace


def make_music(
    selector_function=lambda _: trinton.select_target(_, (1, 3)),
    *args,
    preprocessor=None,
    voice=None,
    beam_meter=False,
):
    target = selector_function(voice)
    indicators = [_ for _ in abjad.get.indicators(abjad.select.leaf(target, 0))]
    selections = None
    groups = abjad.select.group_by_measure(target)
    parentage = abjad.get.parentage(voice)
    outer_context = parentage.components[-1]
    global_context = outer_context["Global Context"]
    relevant_leaves = selector_function(global_context)
    signature_instances = [
        abjad.get.indicator(_, abjad.TimeSignature) for _ in relevant_leaves
    ]
    for arg in args:
        target = selector_function(voice)
        if isinstance(arg, evans.RhythmHandler):
            if preprocessor is not None:
                durations = [abjad.Duration(_.pair) for _ in signature_instances]
                divisions = preprocessor(durations)
            else:
                divisions = signature_instances
            nested_music = arg(divisions)
            container = abjad.Container(nested_music)

            for indicator in indicators:
                abjad.detach(indicator, abjad.select.leaf(target, 0))
                abjad.attach(indicator, abjad.select.leaf(container, 0))

            selections = abjad.mutate.eject_contents(container)
            abjad.mutate.replace(target, selections)

        elif isinstance(arg, evans.RewriteMeterCommand):
            target_copy = abjad.mutate.copy(target[:])

            metered_staff = rmakers.wrap_in_time_signature_staff(
                target_copy, signature_instances
            )

            arg(metered_staff)

            selections = abjad.mutate.eject_contents(metered_staff)
            abjad.mutate.replace(target, selections)
        else:
            arg(target)

    if beam_meter is True:
        print("Beaming meter ...")
        target = selector_function(voice)
        target = abjad.select.leaves(target, grace=False)
        measures = abjad.select.group_by_measure(target)
        for i, shard in enumerate(measures):
            top_level_components = trinton.get_top_level_components_from_leaves(shard)
            shard = top_level_components
            met = abjad.Meter(signature_instances[i].pair)
            inventories = [
                x
                for x in enumerate(
                    abjad.Meter(signature_instances[i].pair).depthwise_offset_inventory
                )
            ]
            if signature_instances[i].denominator == 4:
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


def on_beat_grace_container(
    contents,
    anchor_voice_selection,
    *,
    anchor_voice_number=2,
    do_not_beam=None,
    do_not_slash=None,
    do_not_slur=None,
    do_not_stop_polyphony=None,
    font_size=-3,
    grace_voice_number=1,
    leaf_duration=None,
    name=None,
    no_stem_direction=False,
):
    def _site(n):
        return abjad.Tag(f"trinton.on_beat_grace_container({n})")

    if not abjad.mutate._are_contiguous_same_parent(
        anchor_voice_selection, ignore_before_after_grace=True
    ):
        message = "selection must be contiguous in same parent:\n"
        message += f"   {repr(anchor_voice_selection)}"
        raise Exception(message)
    on_beat_grace_container = abjad.OnBeatGraceContainer(
        contents, leaf_duration=leaf_duration, name=name
    )
    anchor_leaf = abjad._iterlib._get_leaf(anchor_voice_selection, 0)
    anchor_voice = abjad.parentage.Parentage(anchor_leaf).get(abjad.score.Voice)
    if anchor_voice.name is None:
        raise Exception(f"anchor voice must be named:\n   {repr(anchor_voice)}")
    anchor_voice_insert = abjad.score.Voice(name=f"{anchor_voice.name} Anchor")
    abjad.mutate.wrap(anchor_voice_selection, anchor_voice_insert)
    container = abjad.score.Container(simultaneous=True)
    abjad.mutate.wrap(anchor_voice_insert, container)
    container.insert(0, on_beat_grace_container)
    on_beat_grace_container._match_anchor_leaf()
    on_beat_grace_container._set_leaf_durations()
    insert_duration = anchor_voice_insert._get_duration()
    grace_container_duration = on_beat_grace_container._get_duration()
    if insert_duration < grace_container_duration:
        message = f"grace {repr(grace_container_duration)}"
        message += f" exceeds anchor {repr(insert_duration)}."
        raise Exception(message)
    if font_size is not None:
        string = rf"\set fontSize = #{font_size}"
        literal = abjad.LilyPondLiteral(string)
        abjad.attach(literal, on_beat_grace_container, tag=_site(1))
    if not do_not_beam:
        abjad.beam(on_beat_grace_container[:])
    if not do_not_slash:
        if len(container) == 1:
            literal = abjad.LilyPondLiteral(
                r"""\once \override Flag.stroke-style = #"grace" """, site="before"
            )
        else:
            literal = abjad.LilyPondLiteral(r"\my-hack-slash", site="before")
        abjad.attach(literal, on_beat_grace_container[0], tag=_site(2))
    if not do_not_slur:
        abjad.slur(on_beat_grace_container[:])
    voice_number_to_string = {
        1: r"\voiceOne",
        2: r"\voiceTwo",
        3: r"\voiceThree",
        4: r"\voiceFour",
    }
    first_grace = abjad._iterlib._get_leaf(on_beat_grace_container, 0)
    one_voice_literal = abjad.LilyPondLiteral(r"\oneVoice", site="absolute_before")
    string = voice_number_to_string.get(grace_voice_number, None)
    if string is not None:
        literal
        abjad.detach(one_voice_literal, anchor_leaf)
        abjad.attach(abjad.LilyPondLiteral(string), first_grace, tag=_site(3))
    string = voice_number_to_string.get(anchor_voice_number, None)
    if string is not None:
        abjad.detach(one_voice_literal, anchor_leaf)
        abjad.attach(abjad.LilyPondLiteral(string), anchor_leaf, tag=_site(4))
    if not do_not_stop_polyphony:
        last_anchor_leaf = abjad._iterlib._get_leaf(anchor_voice_selection, -1)
        next_leaf = abjad._iterlib._get_leaf(last_anchor_leaf, 1)
        if next_leaf is not None:
            literal = abjad.LilyPondLiteral(r"\oneVoice", site="absolute_before")
            abjad.attach(literal, next_leaf, tag=_site(5))
    return on_beat_grace_container


class OnBeatGraceHandler(evans.handlers.Handler):
    def __init__(
        self,
        number_of_attacks=[4, 5, 6],
        durations=[
            2,
            1,
            1,
            1,
            2,
            1,
            2,
            1,
            1,
        ],
        attack_number_forget=False,
        durations_forget=False,
        font_size=(-4),
        forced_multiplier=None,
        leaf_duration=(1, 28),
        boolean_vector=[1],
        vector_forget=False,
        attack_count=-1,
        durations_count=-1,
        vector_count=-1,
        name="On Beat Grace Handler",
    ):
        self.font_size = font_size
        self.forced_multiplier = forced_multiplier
        self.leaf_duration = leaf_duration
        self._attack_count = attack_count
        self._durations_count = durations_count
        self._vector_count = vector_count
        self.attack_number_forget = attack_number_forget
        self.durations_forget = durations_forget
        self.vector_forget = vector_forget
        self.attacks = evans.sequence.CyclicList(
            number_of_attacks, self.attack_number_forget, self._attack_count
        )
        self.durations = evans.sequence.CyclicList(
            durations, self.durations_forget, self._durations_count
        )
        self.boolean_vector = evans.sequence.CyclicList(
            boolean_vector, self.vector_forget, self._vector_count
        )
        self.name = name

    def __call__(self, selections):
        self.add_grace(selections)

    def add_grace(self, selections):
        ties = abjad.select.logical_ties(selections, pitched=True)
        vector = self.boolean_vector(r=len(ties))
        for value, tie in zip(vector, ties):
            if value == 1:
                repetitions = self.attacks(r=1)[0]
                list_ = []
                durs = self.durations(r=repetitions)
                for _ in durs:
                    list_.append(abjad.Note("c'", (_, 16)))
                sel = list_
                trinton.on_beat_grace_container(
                    sel,
                    tie[:],
                    leaf_duration=self.leaf_duration,
                    do_not_slur=False,
                    do_not_beam=False,
                    font_size=self.font_size,
                )
        if self.forced_multiplier is not None:
            for grace in abjad.select.leaves(selections, grace=True):
                grace.multiplier = abjad.Multiplier(self.forced_multiplier)

    def name(self):
        return self.name

    def state(self):
        return dict(
            [
                ("attack_count", self.attacks.state()),
                ("vector_count", self.boolean_vector.state()),
            ]
        )


# extraction


def render_file(score, segment_path, build_path, segment_name, includes):
    print("Rendering file ...")
    score_block = abjad.Block(name="score")
    score_block.items.append(score)
    assembled_includes = [f'\\include "{path}"' for path in includes]
    assembled_includes.append(score_block)
    file = abjad.LilyPondFile(
        items=assembled_includes,
    )
    score_string = abjad.tag.deactivate(
        abjad.lilypond(file, tags=True), abjad.Tag("+PARTS")
    )
    score_string = score_string[0]
    score_file = abjad.LilyPondFile(items=[score_string])
    parts_string = abjad.tag.deactivate(
        abjad.lilypond(file, tags=True), abjad.Tag("+SCORE")
    )
    parts_string = parts_string[0]
    parts_file = abjad.LilyPondFile(items=[parts_string])
    directory = segment_path
    pdf_path = pathlib.Path(f"{directory}/illustration{segment_name}.pdf")
    ly_path = pathlib.Path(f"{directory}/illustration{segment_name}.ly")
    parts_path = pathlib.Path(f"{build_path}/{segment_name}_parts.ly")
    if pdf_path.exists():
        pdf_path.unlink()
    if ly_path.exists():
        ly_path.unlink()
    if parts_path.exists():
        parts_path.unlink()
    print("Persisting ...")
    abjad.persist.as_ly(score_file, ly_path, tags=True)
    abjad.persist.as_ly(parts_file, parts_path, tags=True)
    if ly_path.exists():
        print("Rendering ...")
        os.system(f"run-lilypond {ly_path}")
    if pdf_path.exists():
        print("Opening ...")
        os.system(f"open {pdf_path}")
    with open(ly_path) as pointer_1:
        score_lines = pointer_1.readlines()
        lines = score_lines[14:-1]
        with open(f"{build_path}/{segment_name}.ly", "w") as fp:
            fp.writelines(lines)
    with open(parts_path) as pointer_1:
        score_lines = pointer_1.readlines()
        lines = score_lines[14:-1]
        with open(f"{build_path}/{segment_name}_parts.ly", "w") as fp:
            fp.writelines(lines)


def render_parts(score, part_name, build_path, segment_name, includes):
    print("Rendering file ...")
    score_block = abjad.Block(name="score")
    score_block.items.append(score)
    assembled_includes = [f'\\include "{path}"' for path in includes]
    assembled_includes.append(score_block)
    file = abjad.LilyPondFile(
        items=assembled_includes,
    )
    music_string = abjad.tag.deactivate(
        abjad.lilypond(file, tags=True), abjad.Tag("+SCORE")
    )
    music_string = music_string[0]
    lily_file = abjad.LilyPondFile(items=[music_string])
    pdf_path = pathlib.Path(f"{build_path}/{part_name}_part.pdf")
    segment_path = pathlib.Path(f"{build_path}/{segment_name}_parts.ly")
    part_path = pathlib.Path(f"{build_path}/{part_name}_part.ly")
    if pdf_path.exists():
        pdf_path.unlink()
    if segment_path.exists():
        segment_path.unlink()
    print("Persisting ...")
    abjad.persist.as_ly(lily_file, segment_path, tags=True)
    with open(segment_path) as pointer_1:
        score_lines = pointer_1.readlines()
        lines = score_lines[14:-1]
        with open(f"{segment_path}", "w") as fp:
            fp.writelines(lines)
    if part_path.exists():
        print("Rendering ...")
        os.system(f"run-lilypond {part_path}")
    if pdf_path.exists():
        print("Opening ...")
        os.system(f"open {pdf_path}")


def extract_parts(score):
    print("Extracting parts ...")
    for count, staff in enumerate(
        abjad.iterate.components(score["Staff Group"], abjad.Staff)
    ):
        t = rf"\tag #'voice{count + 1}"
        literal = abjad.LilyPondLiteral(t, "before")
        container = abjad.Container()
        abjad.attach(literal, container)
        abjad.mutate.wrap(staff, container)
    for count, group in enumerate(
        abjad.iterate.components(score["Staff Group"], abjad.StaffGroup)
    ):
        t = rf"\tag #'group{count + 1}"
        literal = abjad.LilyPondLiteral(t, "before")
        container = abjad.Container()
        abjad.attach(literal, container)
        abjad.mutate.wrap(group, container)


def _extract_voice_info(score):
    score_pitches = []
    score_durations = []
    for voice in abjad.select.components(score, abjad.Voice):
        pitches = []
        durations = []
        for tie in abjad.select.logical_ties(voice):
            dur = abjad.get.duration(tie)
            durations.append(str(dur))
            if isinstance(tie[0], abjad.Rest):
                sub_pitches = ["Rest()"]
            else:
                if abjad.get.annotation(tie[0], "ratio"):
                    sub_pitches = [abjad.get.annotation(tie[0], "ratio")]
                else:
                    sub_pitches = [p.hertz for p in abjad.get.pitches(tie[0])]
            if 1 < len(sub_pitches):
                pitches.append([str(s) for s in sub_pitches])
            elif 0 == len(sub_pitches):
                pitches.append("Rest()")
            else:
                pitches.append(str(sub_pitches[0]))
        score_pitches.append(pitches)
        score_durations.append(durations)
    return [_ for _ in zip(score_pitches, score_durations)]


# synthesis


def make_sc_file(score, tempo, current_directory):

    info = _extract_voice_info(score)
    lines = "s.boot;\ns.quit;\n\n("

    for i, voice in enumerate(info):
        lines += f"\n\t// voice {i + 1}\n\t\tPbind(\n\t\t\t\\freq, Pseq(\n"

        lines += "\t\t\t\t[\n"
        for chord in voice[0]:
            lines += "\t\t\t\t\t[\n"
            if isinstance(chord, list):
                for _ in chord:
                    if _ == "Rest()":
                        lines += f"\t\t\t\t\t\t{_},\n"
                    else:
                        if _[0] == "[":
                            lines += f"\t\t\t\t\t\t{_[2:-2]},\n"
                        else:
                            lines += f"\t\t\t\t\t\t{_},\n"
            else:
                if chord == "Rest()":
                    lines += f"\t\t\t\t\t\t{chord},\n"
                else:
                    if chord[0] == "[":
                        lines += f"\t\t\t\t\t\t{chord[2:-2]},\n"
                    else:
                        lines += f"\t\t\t\t\t\t{chord},\n"
            lines += "\t\t\t\t\t],\n"
        lines += "\t\t\t\t],\n"
        lines += "\t\t\t),\n"
        lines += "\t\t\t\\dur, Pseq(\n\t\t\t\t[\n"
        for dur in voice[1]:
            lines += f"\t\t\t\t\t{quicktions.Fraction(dur) * 4} * {quicktions.Fraction(60, tempo[-1])},\n"
        lines += "\t\t\t\t]\n"
        lines += "\t\t\t,1),\n"
        lines += f"\t\t\t\\amp, {1 / len(info)},\n"
        lines += "\t\t\t\\legato, 1,\n\t\t).play;"

    lines += ")"

    with open(
        f'{current_directory}/voice_to_sc_{str(datetime.datetime.now()).replace(" ", "-").replace(":", "-").replace(".", "-")}.scd',
        "w",
    ) as fp:
        fp.writelines(lines)


def make_combination_tone_wav(
    file_name, combination_tones, partial_pairs, sample_rate=44100
):
    print("writing files . . .")
    text_record = open(f"{file_name}_notes.txt", "w")
    sound_file = open(f"{file_name}.bin", "wb")
    print(
        "Frequency 1\tFrequency 2\tPartial 1\tPartial 2\tCombination Tone",
        file=text_record,
    )

    if len(combination_tones) > len(partial_pairs):
        partial_pairs = cycle(partial_pairs)
    else:
        combination_tones = cycle(combination_tones)

    for combination_tone, partial_pair in zip(combination_tones, partial_pairs):
        if isinstance(combination_tone, abjad.NamedPitch):
            combination_tone = combination_tone.hertz
        else:
            combination_tone = combination_tone

        dt = 1 / sample_rate  # seconds

        t = 0

        gain = 0

        freq_1 = combination_tone * partial_pair[0]
        freq_2 = combination_tone * partial_pair[-1]

        print(
            "\t",
            freq_1,
            "\t",
            freq_2,
            "\t",
            partial_pair[0],
            "\t",
            partial_pair[-1],
            "\t",
            combination_tone,
            file=text_record,
        )

        for _ in range(0, 200000):
            v_1 = math.sin(t * freq_1 * 2 * math.pi)
            v_2 = math.sin(t * freq_2 * 2 * math.pi)
            faded_v_1 = v_1 * gain
            faded_v_2 = v_2 * gain
            bin_v_1 = int(faded_v_1 * 32767)
            bin_v_2 = int(faded_v_2 * 32767)
            sound_file.write(bin_v_1.to_bytes(2, "little", signed=True))
            sound_file.write(bin_v_2.to_bytes(2, "little", signed=True))
            if _ < 1000:
                if gain < 1:
                    gain = gain + (1 / 1000)

            if _ > 199000:
                if gain > 0:
                    gain = gain - (1 / 1000)

            t = t + dt

    text_record.close()
    sound_file.close()

    print("finished writing files")


# fermate


def fermata_measures(
    score,
    measures,
    fermata="middle-fermata",
    voice_names=None,
    font_size=10,
    clef_whitespace=True,
    blank=True,
    last_measure=False,
    padding=None,
    extra_offset=2.5,
    tag=abjad.Tag("+SCORE"),
):
    measures = [_ - 1 for _ in measures]

    leaves = trinton.make_leaf_selection(
        score=score, voice="Global Context", leaves=measures
    )

    for leaf in leaves:
        leaf_duration = abjad.get.duration(leaf)
        mm_rest = abjad.MultimeasureRest(1, multiplier=leaf_duration)

        transparent_literal = abjad.LilyPondLiteral(
            r"\once \override MultiMeasureRest.transparent = ##t",
            "before",
        )
        fermata_markup = abjad.Markup(f"\{fermata}")
        fermata_markup = abjad.bundle(
            fermata_markup, rf"- \tweak font-size #'{font_size}"
        )
        if padding is not None:
            fermata_markup = abjad.bundle(
                fermata_markup, rf"- \tweak padding {padding}"
            )
        invisible_ts_command = abjad.LilyPondLiteral(
            r"\once \override Score.TimeSignature.stencil = ##f",
            "before",
        )
        before_barline_command = abjad.LilyPondLiteral(
            r"\once \override Score.BarLine.transparent = ##f", "absolute_before"
        )
        after_barline_command = abjad.LilyPondLiteral(
            r"\once \override Score.BarLine.transparent = ##f", "absolute_after"
        )
        leaf_ts = abjad.get.indicator(leaf, abjad.TimeSignature)
        leaf_indicators = [
            _
            for _ in abjad.get.indicators(leaf)
            if not isinstance(_, abjad.TimeSignature)
        ]

        abjad.attach(transparent_literal, mm_rest)
        abjad.attach(invisible_ts_command, mm_rest)
        abjad.attach(before_barline_command, mm_rest)
        abjad.attach(after_barline_command, mm_rest)
        abjad.attach(leaf_ts, mm_rest)
        abjad.attach(fermata_markup, mm_rest, direction=abjad.DOWN)
        for indicator in leaf_indicators:
            abjad.attach(indicator, mm_rest)

        abjad.mutate.replace(leaf, mm_rest)

    if blank is True:

        if voice_names is not None:
            voices = [score[_] for _ in voice_names]
        else:
            component_voices = abjad.select.components(
                score["Staff Group"], abjad.Voice
            )
            voices = []

            for voice in component_voices:
                if voice.name[-6:] == "Anchor" or voice.name[:-4] == "temp":
                    pass
                else:
                    voices.append(voice)

        for voice in voices:
            all_measures = abjad.select.group_by_measure(abjad.select.leaves(voice))

            start_command = abjad.LilyPondLiteral(
                r"\stopStaff \once \override Staff.StaffSymbol.line-count = #0 \startStaff",
                "before",
            )

            stop_command = abjad.LilyPondLiteral(r"\stopStaff \startStaff", "after")
            invisibility_literal = abjad.LilyPondLiteral(
                [
                    r"\once \override MultiMeasureRest.transparent = ##t",
                    r"\once \override Rest.transparent = ##t",
                ],
                "before",
            )

            for measure in measures:
                selection = trinton.select_target(voice, (measure + 1,))
                relevant_leaf = selection[0]
                abjad.attach(start_command, relevant_leaf, tag=tag)
                abjad.attach(invisibility_literal, relevant_leaf, tag=tag)
                if last_measure is False:
                    abjad.attach(stop_command, relevant_leaf, tag=tag)

    if clef_whitespace is True:
        if voice_names is not None:
            voices = [score[_] for _ in voice_names]
        else:
            voices = abjad.select.components(score["Staff Group"], abjad.Voice)

        for voice in voices:
            all_measures = abjad.select.group_by_measure(abjad.select.leaves(voice))

            clef_whitespace_literal = abjad.LilyPondLiteral(
                [
                    r"\once \override Staff.Clef.X-extent = ##f",
                    rf"\once \override Staff.Clef.extra-offset = #'(-{extra_offset} . 0)",
                ],
                site="absolute_before",
            )

            for measure in measures:
                selection = trinton.select_target(voice, (measure + 1,))
                relevant_leaf = selection[0]
                next_leaf = abjad.select.with_next_leaf(relevant_leaf)[-1]
                if abjad.get.has_indicator(next_leaf, abjad.Clef):
                    abjad.attach(clef_whitespace_literal, next_leaf, tag=tag)


def make_fermata_measure(selection):
    duration = abjad.Duration((1, 4))
    skip = abjad.MultimeasureRest(1, multiplier=duration)
    transparent_command = abjad.LilyPondLiteral(
        r"\once \override MultiMeasureRest.transparent = ##t",
        "before",
    )
    temp_container = abjad.Container()
    temp_container.append(skip)
    original_leaves = abjad.select.leaves(selection)
    if abjad.get.has_indicator(original_leaves[0], abjad.TimeSignature):
        regular_rest = abjad.Rest(1, multiplier=duration / 2)
        first_skip = abjad.Skip(1, multiplier=duration / 2)
        temp_container = abjad.Container()
        temp_container.extend([first_skip, regular_rest])
        new_sig = abjad.TimeSignature((1, 4))
        abjad.attach(new_sig, temp_container[0])
        transparent_sig = abjad.LilyPondLiteral(
            r"\once \override Score.TimeSignature.transparent = ##t",
            "before",
        )
        transparent_rest = abjad.LilyPondLiteral(
            r"\once \override Rest.transparent = ##t",
            "before",
        )
        abjad.attach(transparent_sig, temp_container[0])
        abjad.attach(transparent_rest, temp_container[1])
    else:
        start_command = abjad.LilyPondLiteral(
            r"\stopStaff \once \override Staff.StaffSymbol.line-count = #0 \startStaff",
            "before",
        )
        stop_command = abjad.LilyPondLiteral(r"\stopStaff \startStaff", "after")
        abjad.attach(start_command, temp_container[0])
        abjad.attach(stop_command, temp_container[0])
    abjad.attach(transparent_command, temp_container[0])
    abjad.mutate.replace(original_leaves, temp_container[:])


def populate_fermata_measures(score, voices, leaves, fermata_measures=None):
    for voice in voices:
        measures = abjad.select.group_by_measure(abjad.select.leaves(score[voice]))

        if fermata_measures is not None:

            for measure in fermata_measures:

                trinton.make_fermata_measure(measures[measure])

        else:
            trinton.make_fermata_measure(measures[-1])

    for voice, l in zip(voices, leaves):
        if voice == "Global Context":
            pass
        else:
            trinton.attach_multiple(
                score=score,
                voice=voice,
                leaves=l,
                attachments=[
                    abjad.Markup(r'\markup \huge { \musicglyph "scripts.ufermata" }'),
                    abjad.LilyPondLiteral(
                        r"\once \override Score.BarLine.transparent = ##f", "after"
                    ),
                    abjad.LilyPondLiteral(
                        r"\once \override Score.BarLine.transparent = ##f", "before"
                    ),
                ],
            )


# dictionary makers


def cache_leaves(score):
    voices = abjad.select.components(score, abjad.Voice)
    lists = [[voice.name, abjad.select.group_by_measure(voice)] for voice in voices]
    measure_dicts = [dict(zip(list(range(1, len(l[1]) + 1)), l[1])) for l in lists]
    dictionary = dict(zip([l[0] for l in lists], measure_dicts))
    return dictionary


# indicator makers


def make_custom_dynamic(dynamic, direction=None):
    if direction == abjad.UP:
        return abjad.LilyPondLiteral(
            rf'^ #(make-dynamic-script (markup #:whiteout #:italic "{dynamic}"))',
            "closing",
        )
    else:
        return abjad.LilyPondLiteral(
            rf'_ #(make-dynamic-script (markup #:whiteout #:italic "{dynamic}"))',
            site="closing",
        )
