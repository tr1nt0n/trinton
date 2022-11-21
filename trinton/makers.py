import abjad
import baca
import evans
import trinton
from abjadext import rmakers
from fractions import Fraction
from itertools import cycle
import quicktions
import numpy
import datetime
import dataclasses
import typing
import pathlib
import os

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
    inner_staff="GrandStaff",
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
    for item, type in zip(grouped_voices, staff_types):
        if isinstance(item, list):
            sub_group = abjad.StaffGroup(
                name=f"sub group {sub_group_counter}", lilypond_type=inner_staff
            )
            sub_group_counter += 1
            for sub_item, sub_type in zip(item, type):
                if 1 < instruments.count(sub_item):
                    name_string = f"{extract_instrument_name(sub_item)} {name_counts[extract_instrument_name(sub_item)]}"
                else:
                    name_string = f"{extract_instrument_name(sub_item)}"
                staff = abjad.Staff(
                    [
                        abjad.Voice(
                            name=f"{name_string} voice",
                        ),
                    ],
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
    inner_staff="GrandStaff",
    staff_types=None,
):
    score = make_score_template(
        instruments=instruments,
        groups=groups,
        outer_staff=outer_staff,
        inner_staff=inner_staff,
        staff_types=staff_types,
    )

    trinton.write_time_signatures(ts=time_signatures, target=score["Global Context"])

    for voice in abjad.select.components(score["Staff Group"], abjad.Voice):
        for rest in [abjad.Skip((1, 1), multiplier=_) for _ in time_signatures]:
            voice.append(rest)

    return score


def annotate_leaves(score, prototype=abjad.Leaf):
    for voice in abjad.select.components(score, abjad.Voice):
        if prototype is not None:
            abjad.label.with_indices(voice, prototype=prototype)
        else:
            abjad.label.with_indices(voice)


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


def make_music(
    selector_function=lambda _: select_target(_, (1, 3)),
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


# extraction


def render_file(score, segment_path, build_path, segment_name, includes):
    print("Rendering file ...")
    score_block = abjad.Block(name="score")
    score_block.items.append(score)
    assembled_includes = [f'\\include "{path}"' for path in includes]
    assembled_includes.append(score_block)
    score_file = abjad.LilyPondFile(
        items=assembled_includes,
    )
    directory = segment_path
    pdf_path = pathlib.Path(f"{directory}/illustration{segment_name}.pdf")
    ly_path = pathlib.Path(f"{directory}/illustration{segment_name}.ly")
    if pdf_path.exists():
        pdf_path.unlink()
    if ly_path.exists():
        ly_path.unlink()
    print("Persisting ...")
    abjad.persist.as_ly(score_file, ly_path)
    if ly_path.exists():
        print("Rendering ...")
        os.system(f"run-lilypond {ly_path}")
    if pdf_path.exists():
        print("Opening ...")
        os.system(f"open {pdf_path}")
    with open(ly_path) as pointer_1:
        score_lines = pointer_1.readlines()
        lines = score_lines[6:-1]
        with open(f"{build_path}/{segment_name}.ly", "w") as fp:
            fp.writelines(lines)


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


# fermate


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
