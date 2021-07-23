import abjad
import evans

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

# def write_time_signatures(ts):
#     for pair in ts:
#         signature = abjad.TimeSignature(pair)
#         skip = abjad.Skip((1, 1), multiplier=abjad.Multiplier(pair))
#         abjad.attach(signature, skip)
#         score["Global Context"].append(skip)
