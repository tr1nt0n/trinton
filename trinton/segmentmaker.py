import abjad
import evans
import trinton
from abjadext import rmakers
import pathlib
import os

def make_score_template(instruments, groups):
    name_counts = {_.name: 1 for _ in instruments}
    sub_group_counter = 1
    score = abjad.Score(
        [
            abjad.Staff(name="Global Context", lilypond_type="TimeSignatureContext"),
            abjad.StaffGroup(name="Staff Group", lilypond_type="ChoirStaff"),
        ],
        name="Score",
    )
    grouped_voices = evans.Sequence(instruments).grouper(groups)
    for item in grouped_voices:
        if isinstance(item, list):
            sub_group = abjad.StaffGroup(name=f"sub group {sub_group_counter}", lilypond_type="PianoStaff")
            sub_group_counter += 1
            for sub_item in item:
                if 1 < instruments.count(sub_item):
                    name_string = f"{sub_item.name} {name_counts[sub_item.name]}"
                else:
                    name_string = f"{sub_item.name}"
                staff = abjad.Staff(
                    [abjad.Voice(name=f"{name_string} voice")],
                    name=f"{name_string} staff",
                )
                sub_group.append(staff)
                name_counts[sub_item.name] += 1
            score["Staff Group"].append(sub_group)
        else:
            if 1 < instruments.count(item):
                name_string = f"{item.name} {name_counts[item.name]}"
            else:
                name_string = f"{item.name}"
            staff = abjad.Staff(
                [abjad.Voice(name=f"{name_string} voice")],
                name=f"{name_string} staff",
            )
            score["Staff Group"].append(staff)
            name_counts[item.name] += 1
    return score

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

def beam_meter(components, meter, offset_depth, include_rests=True):
    r"""
    .. container:: example
        >>> pre_tuplet_notes = abjad.Staff("c'8 c'8 c'8")
        >>> tuplet = abjad.Tuplet((2, 3), "c'8 r8 c'8")
        >>> post_tuplet_notes = abjad.Staff("c'8 c'8 c'8")
        >>> staff = abjad.Staff()
        >>> for _ in [pre_tuplet_notes[:], tuplet, post_tuplet_notes[:]]:
        ...     staff.append(_)
        ...
        >>> evans.beam_meter(components=staff[:], meter=abjad.Meter((4, 4)), offset_depth=1)
        >>> score = abjad.Score([staff])
        >>> moment = "#(ly:make-moment 1 25)"
        >>> abjad.setting(score).proportional_notation_duration = moment
        >>> file = abjad.LilyPondFile(
        ...     items=[score],
        ...     includes=["abjad.ily"],
        ...     global_staff_size=16,
        ... )
        ...
        >>> abjad.show(file) # doctest: +SKIP
        .. docs::
            >>> print(abjad.lilypond(staff))
            \new Staff
            {
                \override Staff.Stem.stemlet-length = 0.75
                c'8
                [
                \revert Staff.Stem.stemlet-length
                c'8
                ]
                c'8
                \times 2/3 {
                    \override Staff.Stem.stemlet-length = 0.75
                    c'8
                    [
                    r8
                    \revert Staff.Stem.stemlet-length
                    c'8
                    ]
                }
                c'8
                \override Staff.Stem.stemlet-length = 0.75
                c'8
                [
                \revert Staff.Stem.stemlet-length
                c'8
                ]
            }
    """
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

    tup_list = [tup for tup in abjad.select(components).components(abjad.Tuplet)]
    for t in tup_list:
        if isinstance(abjad.get.parentage(t).components[1], abjad.Tuplet) is False:
            first_leaf = abjad.select(t).leaf(0)
            if not hasattr(first_leaf._overrides, "Beam"):
                abjad.beam(
                    t[:],
                    beam_rests=include_rests,
                    stemlet_length=0.75,
                    beam_lone_notes=False,
                    selector=abjad.select().leaves(grace=False),
                )
        else:
            continue

    non_tup_list = []
    for leaf in abjad.select(components).leaves():
        if isinstance(abjad.get.parentage(leaf).components[1], abjad.Tuplet) is False:
            non_tup_list.append(leaf)

    beamed_groups = []
    for i in enumerate(offset_timespans):
        beamed_groups.append([])

    for i, span in enumerate(offset_timespans):
        for group in (
            abjad.select(non_tup_list[:])
            .leaves()
            .group_by(
                predicate=lambda x: abjad.get.timespan(x).happens_during_timespan(span)
            )
        ):
            if abjad.get.timespan(group).happens_during_timespan(span) is True:
                beamed_groups[i].append(group[:])

    for subgroup in beamed_groups:
        subgrouper = abjad.select(subgroup).group_by_contiguity()
        for beam_group in subgrouper:
            # if not all(isinstance(leaf, abjad.Rest) for leaf in beam_group)
            abjad.beam(
                beam_group[:],
                beam_rests=include_rests,
                stemlet_length=0.75,
                beam_lone_notes=False,
                selector=abjad.select().leaves(grace=False),
            )

def beam_score_without_splitting(target):
        global_skips = [_ for _ in abjad.select(target["Global Context"]).leaves()]
        sigs = []
        for skip in global_skips:
            for indicator in abjad.get.indicators(skip):
                if isinstance(indicator, abjad.TimeSignature):
                    sigs.append(indicator)
        print("Beaming meter ...")
        for voice in abjad.iterate(target["Staff Group"]).components(abjad.Voice):
            measures = abjad.select(voice[:]).leaves().group_by_measure()
            for i, shard in enumerate(measures):
                top_level_components = get_top_level_components_from_leaves(shard)
                shard = abjad.Selection(top_level_components)
                met = abjad.Meter(sigs[i].pair)
                inventories = [
                    x
                    for x in enumerate(
                        abjad.Meter(sigs[i].pair).depthwise_offset_inventory
                    )
                ]
                if sigs[i].denominator == 4:
                    beam_meter(
                        components=shard[:],
                        meter=met,
                        offset_depth=inventories[-1][0],
                        include_rests=False,
                        # include_rests=False,
                    )
                else:
                    beam_meter(
                        components=shard[:],
                        meter=met,
                        offset_depth=inventories[-2][0],
                        include_rests=False,
                        # include_rests=False,
                    )
        for trem in abjad.select(target).components(abjad.TremoloContainer):
            if abjad.StartBeam() in abjad.get.indicators(trem[0]):
                abjad.detach(abjad.StartBeam(), trem[0])
            if abjad.StopBeam() in abjad.get.indicators(trem[-1]):
                abjad.detach(abjad.StopBeam(), trem[-1])

def rewrite_meter_without_splitting(target):
        global_skips = [_ for _ in abjad.select(target["Global Context"]).leaves()]
        sigs = []
        for skip in global_skips:
            for indicator in abjad.get.indicators(skip):
                if isinstance(indicator, abjad.TimeSignature):
                    sigs.append(indicator)
        for voice in abjad.select(target["Staff Group"]).components(abjad.Voice):
            voice_dur = abjad.get.duration(voice)
            time_signatures = sigs
            durations = [_.duration for _ in time_signatures]
            sig_dur = sum(durations)
            assert voice_dur == sig_dur, (voice_dur, sig_dur)
            shards = abjad.select(voice[:]).leaves().group_by_measure()
            for i, shard in enumerate(shards):
                if voice.name == "violin 1 voice":
                    print(i)
                if not all(
                    isinstance(leaf, (abjad.Rest, abjad.MultimeasureRest, abjad.Skip))
                    for leaf in abjad.select(shard).leaves()
                ):
                    time_signature = sigs[i]
                    top_level_components = get_top_level_components_from_leaves(shard)
                    shard = abjad.Selection(top_level_components)
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

def render_file(score, segment_path, build_path, segment_name, includes):
        print("Rendering file ...")
        score_block = abjad.Block(name="score")
        score_block.items.append(score)
        score_file = abjad.LilyPondFile(
            items=[score_block], includes=includes
        )
        directory = segment_path
        pdf_path = pathlib.Path(f"{directory}/illustration{segment_name}.pdf")
        ly_path = pathlib.Path(f"{directory}/illustration{segment_name}.ly")
        if pdf_path.exists():
            pdf_path.unlink()
        if ly_path.exists():
            ly_path.unlink()
        print("Persisting ...")
        abjad.persist.as_pdf(
            score_file,
            ly_path,
        )
        if pdf_path.exists():
            print("Opening ...")
            os.system(f"open {pdf_path}")
        with open(ly_path) as pointer_1:
            score_lines = pointer_1.readlines()
            lines = score_lines[13:-1]
            with open(f"{build_path}/{segment_name}.ly", "w") as fp:
                fp.writelines(lines)

def attach(voice, leaves, attachment):
    if leaves == all:
        for leaf in abjad.select(voice).leaves(pitched=True):
            abjad.attach(attachment, leaf)
    else:
        for number in leaves:
            sel = abjad.select(voice).leaf(number)
            abjad.attach(attachment, sel)

def write_time_signatures(ts, target):
    for pair in ts:
        signature = abjad.TimeSignature(pair)
        skip = abjad.Skip((1, 1), multiplier=abjad.Multiplier(pair))
        abjad.attach(signature, skip)
        target.append(skip)

def write_text_span(voice, begin_text, end_text, start_leaf, stop_leaf, padding):
    start_text_span = abjad.StartTextSpan(
        left_text=abjad.Markup(begin_text),
        right_text=abjad.Markup(end_text),
        style="dashed-line-with-arrow",
    )
    abjad.tweak(start_text_span).staff_padding = padding
    trinton.attach(
        voice,
        start_leaf,
        start_text_span
    )
    trinton.attach(
        voice,
        stop_leaf,
        abjad.StopTextSpan()
    )

def write_slur(voice, start_slur, stop_slur):
    for leaf in start_slur:
        trinton.attach(
            voice,
            [leaf],
            abjad.StartPhrasingSlur()
        )
    for leaf in stop_slur:
        trinton.attach(
            voice,
            [leaf],
            abjad.StopPhrasingSlur()
        )

def change_notehead(voice, leaves, notehead):
    if leaves == all:
        for _ in abjad.select(voice).leaves(pitched=True):
            abjad.tweak(_.note_head).style = notehead
    else:
        for _ in leaves:
            abjad.tweak(abjad.select(voice).leaf(_).note_head).style = notehead

def pitched_notehead_change(voice, pitches, notehead):
    for leaf in abjad.select(voice).leaves(pitched=True):
        for pitch in pitches:
            if leaf.written_pitch.number == pitch:
                abjad.tweak(leaf.note_head).style = notehead

def write_markup(voice, leaf, string, down):
    if down == True:
        markup = abjad.Markup(string, direction=abjad.Down)
        trinton.attach(
            voice,
            leaf,
            markup
        )
    else:
        markup = abjad.Markup(string, direction=abjad.Up)
        trinton.attach(
            voice,
            leaf,
            markup
        )

def annotate_leaves(score, prototype=abjad.Leaf):
    for voice in abjad.select(score).components(abjad.Voice):
        if prototype is not None:
            abjad.Label(voice).with_indices(prototype=prototype)
        else:
            abjad.Label(voice).with_indices()

def make_rhythm_selections(stack, durations):
    selections = stack(durations)
    return selections

def append_rhythm_selections(voice, score, selections):
    relevant_voice = score[voice]
    relevant_voice.append(selections)

def make_and_append_rhythm_selections(score, voice_name, stack, durations):
    selections = stack(durations)
    relevant_voice = score[voice_name]
    relevant_voice.append(selections)

def append_rests(score, voice, rests):
    for rest in rests:
        score[voice].append(rest)

def handwrite(score, voice, durations, pitch_list):
    stack = rmakers.stack(
        rmakers.NoteRhythmMaker(),
    )

    sel = trinton.make_rhythm_selections(
        stack=stack,
        durations=durations,
    )

    container = abjad.Container(sel)

    if pitch_list is not None:
        handler = evans.PitchHandler(
            pitch_list=pitch_list,
            forget=False
        )

        handler(abjad.select(container[:]).leaves())

        trinton.append_rhythm_selections(
            voice=voice,
            score=score,
            selections=container[:]
        )

    else:
        trinton.append_rhythm_selections(
            voice=voice,
            score=score,
            selections=container[:]
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

def repeats(score, start_leaf, stop_leaf):
    trinton.attach(
        voice=score,
        leaves=start_leaf,
        attachment=abjad.BarLine(".|:")
    )

    trinton.attach(
        voice=score,
        leaves=stop_leaf,
        attachment=abjad.BarLine(":|.")
    )

def tuplet_brackets(score, all_staves):
    new_brackets = evans.NoteheadBracketMaker()

    for staff in all_staves:
        new_brackets(score[staff])

def write_startmarkups(score, voices, markups):
    for voice, markup in zip(voices, markups):
        start_markup = abjad.StartMarkup(markup=markup)

        trinton.attach(
            voice=score[voice],
            leaves=[0],
            attachment=start_markup,
        )

def write_marginmarkups(score, voices, markups):
    for voice, markup in zip(voices, markups):
        margin_markup = abjad.MarginMarkup(markup=markup)

        trinton.attach(
            voice=score[voice],
            leaves=[0],
            attachment=margin_markup,
        )

def transparent_accidentals(score, voice, leaves):
    if leaves == all:
        for leaf in abjad.select(score[voice]).leaves(pitched=True):
            abjad.tweak(leaf.note_head).Accidental.transparent=True

    else:
        for leaf in leaves:
            sel = abjad.select(score[voice]).leaf(leaf)
            abjad.tweak(sel.note_head).Accidental.transparent=True

def rewrite_meter(target):
    print("Rewriting meter ...")
    global_skips = [_ for _ in abjad.select(target["Global Context"]).leaves()]
    sigs = []
    for skip in global_skips:
        for indicator in abjad.get.indicators(skip):
            if isinstance(indicator, abjad.TimeSignature):
                sigs.append(indicator)
    for voice in abjad.select(target["Staff Group"]).components(abjad.Voice):
        voice_dur = abjad.get.duration(voice)
        time_signatures = sigs#[:-1]
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

def beam_score(target):
    global_skips = [_ for _ in abjad.select(target["Global Context"]).leaves()]
    sigs = []
    for skip in global_skips:
        for indicator in abjad.get.indicators(skip):
            if isinstance(indicator, abjad.TimeSignature):
                sigs.append(indicator)
    print("Beaming meter ...")
    for voice in abjad.iterate(target["Staff Group"]).components(abjad.Voice):
        for i, shard in enumerate(abjad.mutate.split(voice[:], sigs)):
            met = abjad.Meter(sigs[i].pair)
            inventories = [
                x
                for x in enumerate(
                    abjad.Meter(sigs[i].pair).depthwise_offset_inventory
                )
            ]
            if sigs[i].denominator == 4:
                beam_meter(
                    components=shard[:],
                    meter=met,
                    offset_depth=inventories[-1][0],
                    include_rests=False,
                    # include_rests=False,
                )
            else:
                beam_meter(
                    components=shard[:],
                    meter=met,
                    offset_depth=inventories[-2][0],
                    include_rests=False,
                    # include_rests=False,
                )
    for trem in abjad.select(target).components(abjad.TremoloContainer):
        if abjad.StartBeam() in abjad.get.indicators(trem[0]):
            abjad.detach(abjad.StartBeam(), trem[0])
        if abjad.StopBeam() in abjad.get.indicators(trem[-1]):
            abjad.detach(abjad.StopBeam(), trem[-1])

def unmeasured_stem_tremolo(selections):
    for leaf in selections:
        if leaf.written_duration == abjad.Duration(1, 64):
            abjad.attach(abjad.StemTremolo(512), leaf)

        elif leaf.written_duration == abjad.Duration(1, 32):
            abjad.attach(abjad.StemTremolo(256), leaf)

        elif leaf.written_duration == abjad.Duration(3, 32):
            abjad.attach(abjad.StemTremolo(256), leaf)

        elif leaf.written_duration == abjad.Duration(1, 16):
            abjad.attach(abjad.StemTremolo(128), leaf)

        elif leaf.written_duration == abjad.Duration(3, 16):
            abjad.attach(abjad.StemTremolo(64), leaf)

        elif leaf.written_duration == abjad.Duration(1, 8):
            abjad.attach(abjad.StemTremolo(64), leaf)

        elif leaf.written_duration == abjad.Duration(1, 4):
            abjad.attach(abjad.StemTremolo(32), leaf)

        elif leaf.written_duration == abjad.Duration(3, 8):
            abjad.attach(abjad.StemTremolo(32), leaf)

        elif leaf.written_duration == abjad.Duration(1, 2):
            abjad.attach(abjad.StemTremolo(32), leaf)

        elif leaf.written_duration == abjad.Duration(3, 4):
            abjad.attach(abjad.StemTremolo(32), leaf)

        elif leaf.written_duration == abjad.Duration(1, 1):
            abjad.attach(abjad.StemTremolo(32), leaf)

def attach_multiple(score, voice, attachments, leaves):
    for attachment in attachments:
        trinton.attach(
            voice=score[voice],
            leaves=leaves,
            attachment=attachments,
        )
