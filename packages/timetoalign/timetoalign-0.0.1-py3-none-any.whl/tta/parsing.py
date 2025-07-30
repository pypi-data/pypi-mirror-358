import json
import warnings
from collections import defaultdict
from itertools import zip_longest
from typing import Collection, Dict, Iterable, Optional, Tuple, Type, overload

import mido
import numpy as np
import pandas as pd
import partitura.performance as ptp
import partitura.score as pts
from partitura.utils import get_time_units_from_note_array, iter_subclasses
from partitura.utils.globals import TIME_UNITS
from partitura.utils.music import rec_collapse_rests, seconds_to_midi_ticks

from processing.metaframes import DF, Meta, pd_concat
from processing.tta.utils import make_argument_iterable

# region MIDI

CC_PURPOSE = {
    0: "Bank Select (MSB)",
    1: "Modulation Wheel (MSB)",
    2: "Breath Controller (MSB)",
    3: "Undefined (MSB)",
    4: "Foot Controller (MSB)",
    5: "Portamento Time (MSB)",
    6: "Data Entry (MSB)",
    7: "Channel Volume (MSB)",
    8: "Balance (MSB)",
    9: "Undefined (MSB)",
    10: "Pan (MSB)",
    11: "Expression Controller (MSB)",
    12: "Effect Control 1 (MSB)",
    13: "Effect Control 2 (MSB)",
    14: "Undefined (MSB)",
    15: "Undefined (MSB)",
    16: "General Purpose Controller 1 (MSB)",
    17: "General Purpose Controller 2 (MSB)",
    18: "General Purpose Controller 3 (MSB)",
    19: "General Purpose Controller 4 (MSB)",
    20: "Undefined (MSB)",
    21: "Undefined (MSB)",
    22: "Undefined (MSB)",
    23: "Undefined (MSB)",
    24: "Undefined (MSB)",
    25: "Undefined (MSB)",
    26: "Undefined (MSB)",
    27: "Undefined (MSB)",
    28: "Undefined (MSB)",
    29: "Undefined (MSB)",
    30: "Undefined (MSB)",
    31: "Undefined (MSB)",
    32: "Bank Select (LSB)",
    33: "Modulation Wheel (LSB)",
    34: "Breath Controller (LSB)",
    35: "Undefined (LSB)",
    36: "Foot Controller (LSB)",
    37: "Portamento Time (LSB)",
    38: "Data Entry (LSB)",
    39: "Channel Volume (LSB)",
    40: "Balance (LSB)",
    41: "Undefined (LSB)",
    42: "Pan (LSB)",
    43: "Expression Controller (LSB)",
    44: "Effect Control 1 (LSB)",
    45: "Effect Control 2 (LSB)",
    46: "Undefined (LSB)",
    47: "Undefined (LSB)",
    48: "General Purpose Controller 1 (LSB)",
    49: "General Purpose Controller 2 (LSB)",
    50: "General Purpose Controller 3 (LSB)",
    51: "General Purpose Controller 4 (LSB)",
    52: "Undefined (LSB)",
    53: "Undefined (LSB)",
    54: "Undefined (LSB)",
    55: "Undefined (LSB)",
    56: "Undefined (LSB)",
    57: "Undefined (LSB)",
    58: "Undefined (LSB)",
    59: "Undefined (LSB)",
    60: "Undefined (LSB)",
    61: "Undefined (LSB)",
    62: "Undefined (LSB)",
    63: "Undefined (LSB)",
    64: "Sustain Pedal",
    65: "Portamento",
    66: "Sostenuto Pedal",
    67: "Soft Pedal",
    68: "Legato Footswitch",
    69: "Hold 2 Pedal",
    70: "Sound Variation",
    71: "Resonance (Timbre)",
    72: "Release Time",
    73: "Attack Time",
    74: "Brightness (Filter Cutoff)",
    75: "Sound Controller 6",  # Default: Decay Time (some implementations)
    76: "Sound Controller 7",  # Default: Vibrato Rate (some implementations)
    77: "Sound Controller 8",  # Default: Vibrato Depth (some implementations)
    78: "Sound Controller 9",  # Default: Vibrato Delay (some implementations)
    79: "Sound Controller 10",  # Default: Undefined
    80: "General Purpose Controller 5",
    81: "General Purpose Controller 6",
    82: "General Purpose Controller 7",
    83: "General Purpose Controller 8",
    84: "Portamento Control",
    85: "Undefined",
    86: "Undefined",
    87: "Undefined",
    88: "High Resolution Velocity Prefix",
    89: "Undefined",
    90: "Undefined",
    91: "Effects 1 Depth (Reverb Send Level)",
    92: "Effects 2 Depth (Tremolo Depth)",
    93: "Effects 3 Depth (Chorus Depth)",
    94: "Effects 4 Depth (Detune Depth)",
    95: "Effects 5 Depth (Phaser Depth)",
    96: "Data Increment",
    97: "Data Decrement",
    98: "Non-Registered Parameter Number (NRPN) LSB",
    99: "Non-Registered Parameter Number (NRPN) MSB",
    100: "Registered Parameter Number (RPN) LSB",
    101: "Registered Parameter Number (RPN) MSB",
    102: "Undefined",
    103: "Undefined",
    104: "Undefined",
    105: "Undefined",
    106: "Undefined",
    107: "Undefined",
    108: "Undefined",
    109: "Undefined",
    110: "Undefined",
    111: "Undefined",
    112: "Undefined",
    113: "Undefined",
    114: "Undefined",
    115: "Undefined",
    116: "Undefined",
    117: "Undefined",
    118: "Undefined",
    119: "Undefined",
    120: "All Sound Off",
    121: "Reset All Controllers",
    122: "Local Control",
    123: "All Notes Off",
    124: "Omni Mode Off",
    125: "Omni Mode On",
    126: "Mono Mode (Poly Off)",
    127: "Poly Mode (Mono Off)",
}


def midi_to_df(midi_filepath, parse_durations=True, on0_means_off=True) -> DF:
    """
    Converts a MIDI file into a DataFrame carrying metadata and
    one event per row. For example, you may want to result.get_meta("ticks_per_beat").

    Args:
        midi_filepath (str): The path to the input MIDI file.
        parse_durations (bool):
            If True, parse the duration of each event, effectively eliminating note_off events.
        on0_means_off (bool):
            If true, note_on events with velocity 0 will be interpreted as note_off events.
    """
    midi_data = []
    mid = mido.MidiFile(midi_filepath)
    for i, track in enumerate(mid.tracks):
        absolute_time = 0
        active_note_events = {}
        for msg in track:
            absolute_time += msg.time
            event_info = dict(msg.dict(), absolute_time=absolute_time)
            if parse_durations:
                if msg.type == "note_on":
                    if msg.velocity > 0:
                        active_note_events[(msg.channel, msg.note)] = event_info
                    elif on0_means_off:
                        if (msg.channel, msg.note) in active_note_events:
                            event_info = active_note_events.pop((msg.channel, msg.note))
                            event_info["duration"] = (
                                absolute_time - event_info["absolute_time"]
                            )
                        else:
                            warnings.warn(
                                f"note_on event with velocity 0 was to be interpreted as note_off event "
                                f"but there was no {msg.note}-note active on {msg.channel}."
                            )
                elif msg.type == "note_off":
                    if (msg.channel, msg.note) in active_note_events:
                        event_info = active_note_events.pop((msg.channel, msg.note))
                        event_info["duration"] = (
                            absolute_time - event_info["absolute_time"]
                        )
                    else:
                        warnings.warn(
                            f"note_on event with velocity 0 was to be interpreted as note_off event "
                            f"but there was no {msg.note}-note active on {msg.channel}."
                        )
            midi_data.append(event_info)
            # end of message-wise loop
        if parse_durations and active_note_events:
            warning_msg = (
                f"{len(active_note_events)} events on track {i} have not been ended by note_off. "
                f"Their duration is set None."
            )
            if not on0_means_off:
                warning_msg += (
                    " Setting on0_means_off to True might solve this problem."
                )
            warnings.warn(warning_msg)
        # end of track-wise loop

    metadata = {}
    for attr_name in dir(mid):
        if attr_name.startswith("_") or attr_name in ("merged_track", "tracks"):
            continue
        try:
            attr_value = getattr(mid, attr_name)
            if callable(attr_value):
                continue
            metadata[attr_name] = attr_value
        except Exception:
            pass

    dtypes = dict(
        tempo="Int64",
        control="Int64",
        value="Int64",
        channel="Int64",
        program="Int64",
        note="Int64",
        velocity="Int64",
        duration="Int64",
    )

    # Create a pandas DataFrame with ._meta property
    df = DF(
        midi_data,
        meta=metadata,
    ).sort_values(["absolute_time", "type"])
    df = df.astype({col: typ for col, typ in dtypes.items() if col in df})
    if "control" in df:
        purpose_col_position = df.columns.get_loc("control") + 1
        df.insert(purpose_col_position, "control_purpose", df.control.map(CC_PURPOSE))
    return df


# endregion MIDI

# region parsing with partitura


def note_array_from_part_list(
    part_list,
    unique_id_per_part=True,
    include_pitch_spelling=False,
    include_key_signature=False,
    include_time_signature=False,
    include_metrical_position=False,
    include_grace_notes=False,
    include_staff=False,
    include_divs_per_quarter=False,
    merge_tied_notes=True,
):
    """
    Construct a structured Note array from a list of Part objects

    Parameters
    ----------
    part_list : list
       A list of `Part` or `PerformedPart` objects. All elements in
       the list must be of the same type (i.e., no mixing `Part`
       and `PerformedPart` objects in the same list.
    unique_id_per_part : bool (optional)
       Indicate from which part do each note come from in the note ids. Default is True.
    **kwargs : dict
         Additional keyword arguments to pass to `utils.music.note_array_from_part()`

    Returns
    -------
    note_array: structured array
        A structured array containing pitch, onset, duration, voice
        and id for each note in each part of the `part_list`. The note
        ids in this array include the number of the part to which they
        belong.
    """
    from partitura.performance import PerformedPart
    from partitura.score import Part, PartGroup

    kwargs = dict(
        include_pitch_spelling=include_pitch_spelling,
        include_key_signature=include_key_signature,
        include_time_signature=include_time_signature,
        include_metrical_position=include_metrical_position,
        include_grace_notes=include_grace_notes,
        include_staff=include_staff,
        include_divs_per_quarter=include_divs_per_quarter,
        merge_tied_notes=merge_tied_notes,
    )
    is_score = False
    note_array = []
    for i, part in enumerate(part_list):
        if isinstance(part, (Part, PartGroup)):
            # set include_divs_per_quarter, to correctly merge different divs
            kwargs["include_divs_per_quarter"] = True
            is_score = True
            if isinstance(part, Part):
                na = note_array_from_part(part, **kwargs)
            elif isinstance(part, PartGroup):
                na = note_array_from_part_list(
                    part.children, unique_id_per_part=unique_id_per_part, **kwargs
                )
        elif isinstance(part, PerformedPart):
            na = part.note_array()
        if unique_id_per_part and len(part_list) > 1:
            # Update id with part number
            na["id"] = np.array(
                ["P{0:02d}_".format(i) + nid for nid in na["id"]], dtype=na["id"].dtype
            )
        note_array.append(na)

    if is_score:
        # rescale if parts have different divs
        divs_per_parts = [
            part_na[0]["divs_pq"] for part_na in note_array if len(part_na)
        ]
        lcm = np.lcm.reduce(divs_per_parts)
        time_multiplier_per_part = [int(lcm / d) for d in divs_per_parts]
        for na, time_mult in zip(note_array, time_multiplier_per_part):
            na["onset_div"] = na["onset_div"] * time_mult
            na["duration_div"] = na["duration_div"] * time_mult
            na["divs_pq"] = na["divs_pq"] * time_mult

    # concatenate note_arrays
    note_array = np.hstack(note_array)

    onset_unit, _ = get_time_units_from_note_array(note_array)

    # sort by onset and pitch
    pitch_sort_idx = np.argsort(note_array["pitch"])
    note_array = note_array[pitch_sort_idx]
    onset_sort_idx = np.argsort(note_array[onset_unit], kind="mergesort")
    note_array = note_array[onset_sort_idx]

    return note_array


def rest_array_from_part_list(
    part_list,
    unique_id_per_part=True,
    include_pitch_spelling=False,
    include_key_signature=False,
    include_time_signature=False,
    include_grace_notes=False,
    include_staff=False,
    include_divs_per_quarter=False,
    collapse=False,
):
    """
    Construct a structured Rest array from a list of Part objects

    Parameters
    ----------
    part_list : list
       A list of `Part` or `PerformedPart` objects. All elements in
       the list must be of the same type.
    unique_id_per_part : bool (optional)
       Indicate from which part do each rest come from in the rest ids.
    include_pitch_spelling: bool (optional)
       Include pitch spelling information in rest array.
       This is a dummy attribute and returns zeros everywhere.
       Default is False.
    include_key_signature: bool (optional)
       Include key signature information in output rest array.
       Only valid if parts in `part_list` are `Part` objects.
       See `rest_array_from_part` for more info.
       Default is False.
    include_time_signature : bool (optional)
       Include time signature information in output rest array.
       Only valid if parts in `part_list` are `Part` objects.
       See `rest_array_from_part` for more info.
       Default is False.
    include_grace_notes : bool (optional)
        If `True`,  includes grace note information, i.e. "" for every rest).
        Default is False
    include_staff : bool (optional)
        If `True`,  includes note staff number.
        Default is False
    include_divs_per_quarter : bool (optional)
        If `True`,  include the number of divs (e.g. MIDI ticks,
        MusicXML ppq) per quarter note of the current part.
        Default is False

    Returns
    -------
    rest_array: structured array
        A structured array containing pitch (always zero), onset, duration, voice
        and id for each rest in each part of the `part_list`. The rest
        ids in this array include the number of the part to which they
        belong.
    """
    from partitura.score import Part, PartGroup

    rest_array = []
    for i, part in enumerate(part_list):
        if isinstance(part, (Part, PartGroup)):
            if isinstance(part, Part):
                na = rest_array_from_part(
                    part=part,
                    include_pitch_spelling=include_pitch_spelling,
                    include_key_signature=include_key_signature,
                    include_time_signature=include_time_signature,
                    include_grace_notes=include_grace_notes,
                    include_staff=include_staff,
                    include_divs_per_quarter=include_divs_per_quarter,
                    collapse=collapse,
                )
            elif isinstance(part, PartGroup):
                na = rest_array_from_part_list(
                    part_list=part.children,
                    unique_id_per_part=unique_id_per_part,
                    include_pitch_spelling=include_pitch_spelling,
                    include_key_signature=include_key_signature,
                    include_time_signature=include_time_signature,
                    include_grace_notes=include_grace_notes,
                    include_staff=include_staff,
                    include_divs_per_quarter=include_divs_per_quarter,
                    collapse=collapse,
                )
        if unique_id_per_part:
            # Update id with part number
            na["id"] = np.array(
                ["P{0:02d}_".format(i) + nid for nid in na["id"]], dtype=na["id"].dtype
            )
        rest_array.append(na)

    # concatenate note_arrays
    rest_array = np.hstack(rest_array)

    onset_unit, _ = get_time_units_from_note_array(rest_array)

    # sort by onset and pitch
    pitch_sort_idx = np.argsort(rest_array["pitch"])
    rest_array = rest_array[pitch_sort_idx]
    onset_sort_idx = np.argsort(rest_array[onset_unit], kind="mergesort")
    rest_array = rest_array[onset_sort_idx]

    return rest_array


def event_array_from_part_list(
    part_list,
    include_key_signature=False,
    include_time_signature=False,
    include_metrical_position=False,
    include_staff=False,
    include_divs_per_quarter=False,
    include_type=True,
):
    """
    Construct a structured Event array from a list of Part objects

    Parameters
    ----------
    part_list : list
       A list of `Part` or `PerformedPart` objects. All elements in
       the list must be of the same type (i.e., no mixing `Part`
       and `PerformedPart` objects in the same list.
    unique_id_per_part : bool (optional)
       Indicate from which part do each note come from in the note ids. Default is True.
    **kwargs : dict
         Additional keyword arguments to pass to `utils.music.note_array_from_part()`

    Returns
    -------
    note_array: structured array
        A structured array containing pitch, onset, duration, voice
        and id for each note in each part of the `part_list`. The note
        ids in this array include the number of the part to which they
        belong.
    """
    from partitura.performance import PerformedPart
    from partitura.score import Part, PartGroup

    kwargs = dict(
        include_key_signature=include_key_signature,
        include_time_signature=include_time_signature,
        include_metrical_position=include_metrical_position,
        include_staff=include_staff,
        include_divs_per_quarter=include_divs_per_quarter,
        include_type=include_type,
    )
    is_score = False
    event_array = []
    for i, part in enumerate(part_list):
        if isinstance(part, (Part, PartGroup)):
            # set include_divs_per_quarter, to correctly merge different divs
            kwargs["include_divs_per_quarter"] = True
            is_score = True
            if isinstance(part, Part):
                e_arr = event_array_from_part(part, **kwargs)
            elif isinstance(part, PartGroup):
                e_arr = event_array_from_part_list(part.children, **kwargs)
        elif isinstance(part, PerformedPart):
            e_arr = part.note_array()
        event_array.append(e_arr)

    if is_score:
        # rescale if parts have different divs
        divs_per_parts = [
            part_na[0]["divs_pq"] for part_na in event_array if len(part_na)
        ]
        lcm = np.lcm.reduce(divs_per_parts)
        time_multiplier_per_part = [int(lcm / d) for d in divs_per_parts]
        for e_arr, time_mult in zip(event_array, time_multiplier_per_part):
            e_arr["onset_div"] = e_arr["onset_div"] * time_mult
            e_arr["duration_div"] = e_arr["duration_div"] * time_mult
            e_arr["divs_pq"] = e_arr["divs_pq"] * time_mult

    # concatenate note_arrays
    event_array = np.hstack(event_array)

    onset_unit, _ = get_time_units_from_note_array(event_array)

    # sort by onset and pitch
    onset_sort_idx = np.argsort(event_array[onset_unit], kind="mergesort")
    event_array = event_array[onset_sort_idx]

    return event_array


def slice_notearray_by_time(
    note_array, start_time, end_time, time_unit="auto", clip_onset_duration=True
):
    """
    Get a slice of a structured note array by time

    Parameters
    ----------
    note_array : structured array
        Structured array with score information.
    start_time : float
        Starting time
    end_time : float
        End time
    time_unit : {'auto', 'beat', 'quarter', 'second', 'div'} optional
        Time unit. If 'auto', the default time unit will be inferred
        from the note_array.
    clip_onset_duration : bool optional
        Clip duration of the notes in the array to fit within the
        specified window

    Returns
    -------
    note_array_slice : stuctured array
        Structured array with only the score information between
        `start_time` and `end_time`.

    TODO
    ----
    * adjust onsets and duration in other units
    """

    if time_unit not in TIME_UNITS + ["auto"]:
        raise ValueError(
            "`time_unit` must be 'beat', 'quarter', "
            "'sec', 'div' or 'auto', but is "
            "{0}".format(time_unit)
        )
    if time_unit == "auto":
        onset_unit, duration_unit = get_time_units_from_note_array(note_array)
    else:
        onset_unit, duration_unit = [
            "{0}_{1}".format(d, time_unit) for d in ("onset", "duration")
        ]

    onsets = note_array[onset_unit]
    offsets = note_array[onset_unit] + note_array[duration_unit]

    starting_idxs = set(np.where(onsets >= start_time)[0])
    ending_idxs = set(np.where(onsets < end_time)[0])

    prev_starting_idxs = set(np.where(onsets < start_time)[0])
    sounding_after_start_idxs = set(np.where(offsets > start_time)[0])

    active_idx = np.array(
        list(
            starting_idxs.intersection(ending_idxs).union(
                prev_starting_idxs.intersection(sounding_after_start_idxs)
            )
        )
    )
    active_idx.sort()

    if len(active_idx) == 0:
        # If there are no elements, return an empty array
        note_array_slice = np.empty(0, dtype=note_array.dtype)
    else:
        note_array_slice = note_array[active_idx]

    if clip_onset_duration and len(active_idx) > 0:
        psi = np.where(note_array_slice[onset_unit] < start_time)[0]
        note_array_slice[psi] = start_time
        adj_offsets = np.clip(
            note_array_slice[onset_unit] + note_array_slice[duration_unit],
            a_min=None,
            a_max=end_time,
        )
        note_array_slice[duration_unit] = adj_offsets - note_array_slice[onset_unit]

    return note_array_slice


def note_array_from_part(
    part,
    include_pitch_spelling=False,
    include_key_signature=False,
    include_time_signature=False,
    include_metrical_position=False,
    include_grace_notes=False,
    include_staff=False,
    include_divs_per_quarter=False,
    include_type=True,
    merge_tied_notes=True,
):
    """
    Create a structured array with note information
    from a `Part` object.

    Parameters
    ----------
    part : partitura.score.Part
        An object representing a score part.
    include_pitch_spelling : bool (optional)
        It's a dummy attribute for consistancy between note_array_from_part and note_array_from_part_list.
        Default is False
    include_pitch_spelling : bool (optional)
        If `True`, includes pitch spelling information for each
        note. Default is False
    include_key_signature : bool (optional)
        If `True`, includes key signature information, i.e.,
        the key signature at the onset time of each note (all
        notes starting at the same time have the same key signature).
        Default is False
    include_time_signature : bool (optional)
        If `True`,  includes time signature information, i.e.,
        the time signature at the onset time of each note (all
        notes starting at the same time have the same time signature).
        Default is False
    include_metrical_position : bool (optional)
        If `True`,  includes metrical position information, i.e.,
        the position of the onset time of each note with respect to its
        measure (all notes starting at the same time have the same metrical
        position).
        Default is False
    include_grace_notes : bool (optional)
        If `True`,  includes grace note information, i.e. if a note is a
        grace note and the grace type "" for non grace notes).
        Default is False
    include_staff : bool (optional)
        If `True`,  includes staff information
        Default is False
    include_divs_per_quarter : bool (optional)
        If `True`,  include the number of divs (e.g. MIDI ticks,
        MusicXML ppq) per quarter note of the current part.
        Default is False

    Returns
    -------
    note_array : structured array
        A structured array containing note information. The fields are
            * 'onset_beat': onset time of the note in beats
            * 'duration_beat': duration of the note in beats
            * 'onset_quarter': onset time of the note in quarters
            * 'duration_quarter': duration of the note in quarters
            * 'onset_div': onset of the note in divs (e.g., MIDI ticks,
              divisions in MusicXML)
            * 'duration_div': duration of the note in divs
            * 'pitch': MIDI pitch of a note.
            * 'voice': Voice number of a note (if given in the score)
            * 'id': Id of the note

        If `include_pitch_spelling` is True:
            * 'step': name of the note ("C", "D", "E", "F", "G", "A", "B")
            * 'alter': alteration (0=natural, -1=flat, 1=sharp,
              2=double sharp, etc.)
            * 'octave': octave of the note.

        If `include_key_signature` is True:
            * 'ks_fifths': Fifths starting from C in the circle of fifths
            * 'mode': major or minor

        If `include_time_signature` is True:
            * 'ts_beats': number of beats in a measure
            * 'ts_beat_type': type of beats (denominator of the time signature)
            * 'ts_mus_beat' : number of musical beats is it's set, otherwise ts_beats

        If `include_metrical_position` is True:
            * 'is_downbeat': 1 if the note onset is on a downbeat, 0 otherwise
            * 'rel_onset_div': number of divs elapsed from the beginning of the note measure
            * 'tot_measure_divs' : total number of divs in the note measure

        If 'include_grace_notes' is True:
            * 'is_grace': 1 if the note is a grace 0 otherwise
            * 'grace_type' : the type of the grace notes "" for non grace notes

        If 'include_staff' is True:
            * 'staff' : the staff number for each note

        If 'include_divs_per_quarter' is True:
            * 'divs_pq': the number of divs per quarter note
    Examples
    --------
    >>> from partitura import load_musicxml, EXAMPLE_MUSICXML
    >>> from partitura.utils import note_array_from_part
    >>> part = load_musicxml(EXAMPLE_MUSICXML)
    >>> note_array_from_part(part, True, True, True) # doctest: +NORMALIZE_WHITESPACE
    array([(0., 4., 0., 4.,  0, 48, 69, 1, 'n01', 'A', 0, 4, 0, 1, 4, 4),
           (2., 2., 2., 2., 24, 24, 72, 2, 'n02', 'C', 0, 5, 0, 1, 4, 4),
           (2., 2., 2., 2., 24, 24, 76, 2, 'n03', 'E', 0, 5, 0, 1, 4, 4)],
          dtype=[('onset_beat', '<f4'),
                 ('duration_beat', '<f4'),
                 ('onset_quarter', '<f4'),
                 ('duration_quarter', '<f4'),
                 ('onset_div', '<i4'),
                 ('duration_div', '<i4'),
                 ('pitch', '<i4'),
                 ('voice', '<i4'),
                 ('id', '<U256'),
                 ('step', '<U256'),
                 ('alter', '<i4'),
                 ('octave', '<i4'),
                 ('ks_fifths', '<i4'),
                 ('ks_mode', '<i4'),
                 ('ts_beats', '<i4'),
                 ('ts_beat_type', '<i4')])
    """
    if include_time_signature:
        time_signature_map = part.time_signature_map
    else:
        time_signature_map = None

    if include_key_signature:
        key_signature_map = part.key_signature_map
    else:
        key_signature_map = None

    if include_metrical_position:
        metrical_position_map = part.metrical_position_map
    else:
        metrical_position_map = None

    if include_divs_per_quarter:
        divs_per_quarter = get_divs_per_quarter(part)
    else:
        divs_per_quarter = None

    note_array = note_array_from_note_list(
        note_list=part.notes_tied,
        beat_map=part.beat_map,
        quarter_map=part.quarter_map,
        time_signature_map=time_signature_map,
        key_signature_map=key_signature_map,
        metrical_position_map=metrical_position_map,
        include_pitch_spelling=include_pitch_spelling,
        include_grace_notes=include_grace_notes,
        include_staff=include_staff,
        divs_per_quarter=divs_per_quarter,
        include_type=include_type,
        merge_tied_notes=merge_tied_notes,
    )

    return note_array


def note_array_performed_part(part: ptp.PerformedPart) -> np.ndarray:
    """Structured array containing performance information.
    The fields are 'id', 'pitch', 'onset_tick', 'duration_tick',
    'onset_sec', 'duration_sec', 'track', 'channel', and 'velocity'.
    """
    return note_array_from_performed_note_list(
        notes=part.notes,
        ppq=part.ppq,
        mpq=part.mpq,
    )


def note_array_from_performed_note_list(
    notes: Iterable[ptp.PerformedNote],
    ppq: int = 480,
    mpq: int = 500000,
) -> np.ndarray:

    fields = [
        ("onset_sec", "f4"),
        ("duration_sec", "f4"),
        ("onset_tick", "i4"),
        ("duration_tick", "i4"),
        ("pitch", "i4"),
        ("velocity", "i4"),
        ("track", "i4"),
        ("channel", "i4"),
        ("id", "U256"),
    ]
    note_array = []
    for n in notes:
        note_on_tick, duration_tick, note_on_sec, duration_sec = get_pnote_durations(
            n, ppq, mpq
        )
        note_array.append(
            (
                note_on_sec,
                duration_sec,
                note_on_tick,
                duration_tick,
                n["midi_pitch"],
                n["velocity"],
                n.get("track", 0),
                n.get("channel", 1),
                n["id"],
            )
        )

    note_array = np.array(note_array, dtype=fields)
    tick_sort_idx = np.argsort(note_array["onset_tick"])
    note_array = note_array[tick_sort_idx]
    return note_array


def get_pnote_durations(pnote, ppq, mpq):
    note_on_sec = pnote["note_on"]
    note_on_tick = pnote.get(
        "note_on_tick",
        seconds_to_midi_ticks(pnote["note_on"], mpq=mpq, ppq=ppq),
    )
    offset = pnote.get("sound_off", pnote["note_off"])
    duration_sec = offset - note_on_sec
    duration_tick = (
        pnote.get(
            seconds_to_midi_ticks(pnote["sound_off"], mpq=mpq, ppq=ppq),
            seconds_to_midi_ticks(pnote["note_off"], mpq=mpq, ppq=ppq),
        )
        - note_on_tick
    )
    return note_on_tick, duration_tick, note_on_sec, duration_sec


def rest_array_from_part(
    part,
    include_pitch_spelling=False,
    include_key_signature=False,
    include_time_signature=False,
    include_metrical_position=False,
    include_grace_notes=False,
    include_staff=False,
    include_divs_per_quarter=False,
    collapse=False,
    include_type=True,
):
    """
    Create a structured array with rest information
    from a `Part` object Similar to note_array.

    Parameters
    ----------
    part : partitura.score.Part
        An object representing a score part.
    include_pitch_spelling : bool (optional)
        It's a dummy attribute for consistancy between rest_array_from_part and rest_array_from_part_list.
        Default is False
    include_key_signature : bool (optional)
        If `True`, includes key signature information, i.e.,
        the key signature at the onset time of each rest (all
        notes starting at the same time have the same key signature).
        Default is False
    include_time_signature : bool (optional)
        If `True`,  includes time signature information, i.e.,
        the time signature at the onset time of each rest (all
        rests starting at the same time have the same time signature).
        Default is False
    include_metrical_position : bool (optional)
        If `True`,  includes metrical position information, i.e.,
        the position of the onset time of each note with respect to its
        measure.
        Default is False
    include_grace_notes : bool (optional)
        If `True`,  includes grace note information, i.e. the grace type is "" for all rests).
        Default is False
    include_divs_per_quarter : bool (optional)
        If `True`,  include the number of divs (e.g. MIDI ticks,
        MusicXML ppq) per quarter note of the current part.
        Default is False
    collapse : bool (optional)
        If 'True', collapses consecutive rest onsets on the same voice, to a single rest of their combined duration.
        Default is False

    Returns
    -------
    rest_array : structured array
        A structured array containing rest information (pitch is always 0).
    """
    if include_time_signature:
        time_signature_map = part.time_signature_map
    else:
        time_signature_map = None

    if include_key_signature:
        key_signature_map = part.key_signature_map
    else:
        key_signature_map = None

    if include_metrical_position:
        metrical_position_map = part.metrical_position_map
    else:
        metrical_position_map = None

    if include_divs_per_quarter:
        divs_per_quarter = get_divs_per_quarter(part)
    else:
        divs_per_quarter = None

    rest_array = rest_array_from_rest_list(
        rest_list=part.rests,
        beat_map=part.beat_map,
        quarter_map=part.quarter_map,
        time_signature_map=time_signature_map,
        key_signature_map=key_signature_map,
        metrical_position_map=metrical_position_map,
        include_pitch_spelling=include_pitch_spelling,
        include_grace_notes=include_grace_notes,
        include_staff=include_staff,
        divs_per_quarter=divs_per_quarter,
        collapse=collapse,
        include_type=include_type,
    )

    return rest_array


def note_array_from_note_list(
    note_list: Iterable[pts.Note] | Iterable[tuple[pts.Note, str]],
    beat_map=None,
    quarter_map=None,
    time_signature_map=None,
    key_signature_map=None,
    metrical_position_map=None,
    include_pitch_spelling=False,
    include_grace_notes=False,
    include_staff=False,
    divs_per_quarter=None,
    include_type=True,
    merge_tied_notes=True,
):
    """
    Create a structured array with note information
    from a a list of `Note` objects.

    Parameters
    ----------
    note_list : list of `Note` objects
        A list of `Note` objects containing score information.
    beat_map : callable or None
        A function that maps score time in divs to score time in beats.
        If `None` is given, the output structured array will not
        include this information.
    quarter_map: callable or None
        A function that maps score time in divs to score time in quarters.
        If `None` is given, the output structured array will not
        include this information.
    time_signature_map: callable or None (optional)
        A function that maps score time in divs to the time signature at
        that time (in terms of number of beats and beat type).
        If `None` is given, the output structured array will not
        include this information.
    key_signature_map: callable or None (optional)
        A function that maps score time in divs to the key signature at
        that time (in terms of fifths and mode).
        If `None` is given, the output structured array will not
        include this information.
    metrical_position_map: callable or None (optional)
        A function that maps score time in divs to the position in
        the measure at that time.
        If `None` is given, the output structured array will not
        include the metrical position information.
    include_pitch_spelling : bool (optional)
        If `True`, includes pitch spelling information for each
        note. Default is False
    include_grace_notes : bool (optional)
        If `True`,  includes grace note information, i.e. if a note is a
        grace note has one of the types "appoggiatura, acciaccatura, grace" and
        the grace type "" for non grace notes).
        Default is False
    include_staff : bool (optional)
        If `True`,  includes the staff number for every note.
        Default is False
    divs_per_quarter : int or None (optional)
        The number of divs (e.g. MIDI ticks, MusicXML ppq) per quarter
        note of the current part.
        Default is None
    include_type: bool


    Returns
    -------
    note_array : structured array
        A structured array containing note information. The fields are
            * 'onset_beat': onset time of the note in beats.
              Included if `beat_map` is not `None`.
            * 'duration_beat': duration of the note in beats.
              Included if `beat_map` is not `None`.
            * 'onset_quarter': onset time of the note in quarters.
              Included if `quarter_map` is not `None`.
            * 'duration_quarter': duration of the note in quarters.
              Included if `quarter_map` is not `None`.
            * 'onset_div': onset of the note in divs (e.g., MIDI ticks,
              divisions in MusicXML)
            * 'duration_div': duration of the note in divs
            * 'pitch': MIDI pitch of a note.
            * 'voice': Voice number of a note (if given in the score)
            * 'id': Id of the note
            * 'step': name of the note ("C", "D", "E", "F", "G", "A", "B").
              Included if `include_pitch_spelling` is `True`.
            * 'alter': alteration (0=natural, -1=flat, 1=sharp,
              2=double sharp, etc.). Included if `include_pitch_spelling`
              is `True`.
            * 'octave': octave of the note. Included if `include_pitch_spelling`
              is `True`.
            * 'is_grace' : Is the note a grace note. Yes if true.
            * 'grace_type' : The type of grace note. "" for non grace notes.
            * 'ks_fifths': Fifths starting from C in the circle of fifths.
              Included if `key_signature_map` is not `None`.
            * 'mode': major or minor. Included If `key_signature_map` is
              not `None`.
            * 'ts_beats': number of beats in a measure. If `time_signature_map`
               is True.
            * 'ts_beat_type': type of beats (denominator of the time signature).
              If `include_time_signature` is True.
            * 'is_downbeat': 1 if the note onset is on a downbeat, 0 otherwise.
               If `measure_map` is not None.
            * 'rel_onset_div': number of divs elapsed from the beginning of the
               note measure. If `measure_map` is not None.
            * 'tot_measure_div' : total number of divs in the note measure
               If `measure_map` is not None.
            * 'staff' : number of note staff.
            * 'divs_pq' : number of parts per quarter note.
    """
    has_type = False
    for note in note_list:
        has_type = isinstance(note, tuple)
    if include_type:
        fields = [("event_type", "U256")]
    else:
        fields = []
    if beat_map is not None:
        # Preserve the order of the fields
        fields += [("onset_beat", "f4"), ("duration_beat", "f4")]

    if quarter_map is not None:
        fields += [("onset_quarter", "f4"), ("duration_quarter", "f4")]
    fields += [
        ("onset_div", "i4"),
        ("duration_div", "i4"),
        ("pitch", "i4"),
        ("voice", "i4"),
        ("id", "U256"),
    ]

    # fields for pitch spelling
    if include_pitch_spelling:
        fields += [("step", "U256"), ("alter", "i4"), ("octave", "i4")]

    # fields for pitch spelling
    if include_grace_notes:
        fields += [("is_grace", "b"), ("grace_type", "U256")]

    # fields for key signature
    if key_signature_map is not None:
        fields += [("ks_fifths", "i4"), ("ks_mode", "i4")]

    # fields for time signature
    if time_signature_map is not None:
        fields += [("ts_beats", "i4"), ("ts_beat_type", "i4"), ("ts_mus_beats", "i4")]

    # fields for metrical position
    if metrical_position_map is not None:
        fields += [
            ("is_downbeat", "i4"),
            ("rel_onset_div", "i4"),
            ("tot_measure_div", "i4"),
        ]
    # field for staff
    if include_staff:
        fields += [("staff", "i4")]

    # field for divs_pq
    if divs_per_quarter:
        fields += [("divs_pq", "i4")]

    note_array = []
    for note in note_list:
        note_info = tuple()
        if has_type:
            note, note_type = note
        if merge_tied_notes and note.tie_prev is not None:
            # skip the note event if it is tied to the previous note
            # this emulates Part.notes_tied behaviour even with a full note list
            continue
        if include_type:
            if not has_type:
                note_type = note.__class__.__name__
            note_info += (note_type,)

        note_on_div = note.start.t
        if merge_tied_notes:
            note_off_div = note.start.t + note.duration_tied
        else:
            note_off_div = note.start.t + note.duration
        note_dur_div = note_off_div - note_on_div

        if beat_map is not None:
            note_on_beat, note_off_beat = beat_map([note_on_div, note_off_div])
            note_dur_beat = note_off_beat - note_on_beat

            note_info += (note_on_beat, note_dur_beat)

        if quarter_map is not None:
            note_on_quarter, note_off_quarter = quarter_map([note_on_div, note_off_div])
            note_dur_quarter = note_off_quarter - note_on_quarter

            note_info += (note_on_quarter, note_dur_quarter)

        note_info += (
            note_on_div,
            note_dur_div,
            note.midi_pitch,
            note.voice if note.voice is not None else -1,
            note.id,
        )

        if include_pitch_spelling:
            step = note.step
            alter = note.alter if note.alter is not None else 0
            octave = note.octave

            note_info += (step, alter, octave)

        if include_grace_notes:
            is_grace = hasattr(note, "grace_type")
            if is_grace:
                grace_type = note.grace_type
            else:
                grace_type = ""
            note_info += (is_grace, grace_type)

        if key_signature_map is not None:
            fifths, mode = key_signature_map(note.start.t)

            note_info += (fifths, mode)

        if time_signature_map is not None:
            beats, beat_type, mus_beats = time_signature_map(note.start.t)

            note_info += (beats, beat_type, mus_beats)

        if metrical_position_map is not None:
            rel_onset_div, tot_measure_div = metrical_position_map(note.start.t)

            is_downbeat = 1 if rel_onset_div == 0 else 0

            note_info += (is_downbeat, rel_onset_div, tot_measure_div)

        if include_staff:
            note_info += ((note.staff if note.staff else 0),)

        if divs_per_quarter:
            note_info += (divs_per_quarter,)

        note_array.append(note_info)

    note_array = np.array(note_array, dtype=fields)

    # Sanitize voice information
    no_voice_idx = np.where(note_array["voice"] == -1)[0]
    try:
        max_voice = note_array["voice"].max()
    except ValueError:  # raised if `note_array["voice"]` is empty.
        note_array["voice"] = 0
        max_voice = 0
    note_array["voice"][no_voice_idx] = max_voice + 1

    # sort by onset and pitch
    onset_unit, _ = get_time_units_from_note_array(note_array)
    pitch_sort_idx = np.argsort(note_array["pitch"])
    note_array = note_array[pitch_sort_idx]
    onset_sort_idx = np.argsort(note_array[onset_unit], kind="mergesort")
    note_array = note_array[onset_sort_idx]

    return note_array


def rest_array_from_rest_list(
    rest_list: Iterable[pts.Rest] | Iterable[tuple[pts.Rest, str]],
    beat_map=None,
    quarter_map=None,
    time_signature_map=None,
    key_signature_map=None,
    metrical_position_map=None,
    include_pitch_spelling=False,
    include_grace_notes=False,
    include_staff=False,
    divs_per_quarter=None,
    collapse=False,
    include_type=True,
):
    """
    Create a structured array with rest information
    from a list of `Rest` objects.

    Parameters
    ----------
    rest_list : list of `Rest` objects
        A list of `Rest` objects containing score information.
    beat_map : callable or None
        A function that maps score time in divs to score time in beats.
        If `None` is given, the output structured array will not
        include this information.
    quarter_map: callable or None
        A function that maps score time in divs to score time in quarters.
        If `None` is given, the output structured array will not
        include this information.
    time_signature_map: callable or None (optional)
        A function that maps score time in divs to the time signature at
        that time (in terms of number of beats and beat type).
        If `None` is given, the output structured array will not
        include this information.
    key_signature_map: callable or None (optional)
        A function that maps score time in divs to the key signature at
        that time (in terms of fifths and mode).
        If `None` is given, the output structured array will not
        include this information.
    metrical_position_map: callable or None (optional)
        A function that maps score time in divs to the position in
        the measure at that time.
        If `None` is given, the output structured array will not
        include the metrical position information.
    include_pitch_spelling : bool (optional)
        If `True`, includes pitch spelling information for each
        rest. This is a dummy attribute and returns zeros everywhere.
        Default is False
    include_grace_notes : bool (optional)
        If `True`,  includes grace note information, i.e. "" for all rests).
        Default is False
    include_staff : bool (optional)
        If `True`,  includes the staff number for every note.
        Default is False
    divs_per_quarter : int or None (optional)
        The number of divs (e.g. MIDI ticks, MusicXML ppq) per quarter
        note of the current part.
        Default is None
    collapse : bool (optional)
        If `True`, joins rests on consecutive onsets on the same voice and combines their durations.
        Keeps the id of the first one.
        Default is False
    include_type: bool

    Returns
    -------
    rest_array : structured array
        A structured array containing rest information. Pitch is set to 0.
    """
    has_type = False
    for rest in rest_list:
        has_type = isinstance(rest, tuple)
    if include_type:
        fields = [("event_type", "U256")]
    else:
        fields = []
    if beat_map is not None:
        # Preserve the order of the fields
        fields += [("onset_beat", "f4"), ("duration_beat", "f4")]

    if quarter_map is not None:
        fields += [("onset_quarter", "f4"), ("duration_quarter", "f4")]
    fields += [
        ("onset_div", "i4"),
        ("duration_div", "i4"),
        ("pitch", "i4"),
        ("voice", "i4"),
        ("id", "U256"),
    ]

    # fields for pitch spelling
    if include_pitch_spelling:
        fields += [("step", "U256"), ("alter", "i4"), ("octave", "i4")]

    # fields for pitch spelling
    if include_grace_notes:
        fields += [("is_grace", "b"), ("grace_type", "U256")]

    # fields for key signature
    if key_signature_map is not None:
        fields += [("ks_fifths", "i4"), ("ks_mode", "i4")]

    # fields for time signature
    if time_signature_map is not None:
        fields += [("ts_beats", "i4"), ("ts_beat_type", "i4"), ("ts_mus_beats", "i4")]

    # fields for metrical position
    if metrical_position_map is not None:
        fields += [
            ("is_downbeat", "i4"),
            ("rel_onset_div", "i4"),
            ("tot_measure_div", "i4"),
        ]
    # fields for staff
    if include_staff:
        fields += [("staff", "i4")]

    # field for divs_pq
    if divs_per_quarter:
        fields += [("divs_pq", "i4")]

    rest_array = []
    for rest in rest_list:
        rest_info = tuple()
        if has_type:
            rest, rest_type = rest
        if include_type:
            if not has_type:
                rest_type = rest.__class__.__name__
            rest_info += (rest_type,)
        rest_on_div = rest.start.t
        rest_off_div = rest.start.t + rest.duration_tied
        rest_dur_div = rest_off_div - rest_on_div

        if beat_map is not None:
            note_on_beat, note_off_beat = beat_map([rest_on_div, rest_off_div])
            note_dur_beat = note_off_beat - note_on_beat

            rest_info += (note_on_beat, note_dur_beat)

        if quarter_map is not None:
            note_on_quarter, note_off_quarter = quarter_map([rest_on_div, rest_off_div])
            note_dur_quarter = note_off_quarter - note_on_quarter

            rest_info += (note_on_quarter, note_dur_quarter)

        rest_info += (
            rest_on_div,
            rest_dur_div,
            0,
            rest.voice if rest.voice is not None else -1,
            rest.id,
        )

        if include_pitch_spelling:
            step = 0
            alter = 0
            octave = 0

            rest_info += (step, alter, octave)

        if include_grace_notes:
            is_grace = hasattr(rest, "grace_type")
            if is_grace:
                grace_type = rest.grace_type
            else:
                grace_type = ""
            rest_info += (is_grace, grace_type)

        if key_signature_map is not None:
            fifths, mode = key_signature_map(rest.start.t)

            rest_info += (fifths, mode)

        if time_signature_map is not None:
            beats, beat_type, mus_beats = time_signature_map(rest.start.t)

            rest_info += (beats, beat_type, mus_beats)

        if metrical_position_map is not None:
            rel_onset_div, tot_measure_div = metrical_position_map(rest.start.t)

            is_downbeat = 1 if rel_onset_div == 0 else 0

            rest_info += (is_downbeat, rel_onset_div, tot_measure_div)

        if include_staff:
            rest_info += ((rest.staff if rest.staff else 0),)

        if divs_per_quarter:
            rest_info += (divs_per_quarter,)

        rest_array.append(rest_info)

    rest_array = np.array(rest_array, dtype=fields)

    # Sanitize voice information
    if rest_list:
        no_voice_idx = np.where(rest_array["voice"] == -1)[0]
        max_voice = rest_array["voice"].max()
        rest_array["voice"][no_voice_idx] = max_voice + 1

    # sort by onset and pitch
    onset_unit, _ = get_time_units_from_note_array(rest_array)
    pitch_sort_idx = np.argsort(rest_array["pitch"])
    rest_array = rest_array[pitch_sort_idx]
    onset_sort_idx = np.argsort(rest_array[onset_unit], kind="mergesort")
    rest_array = rest_array[onset_sort_idx]

    if collapse:
        rest_array = rec_collapse_rests(rest_array)
    return rest_array


def get_starting_objects_from_point(pt: pts.TimePoint):
    """Helper that can be mapped on the part._points array"""
    return pt.starting_objects


def get_event_dict(
    parts: (
        pts.Part | ptp.PerformedPart | Iterable[pts.Part] | Iterable[ptp.PerformedPart]
    ),
) -> dict[Type[pts.TimedObject], set[pts.TimedObject]]:
    """Iterates through all TimePoints in a part merging the respective {cls -> {instances}} dicts."""
    if isinstance(parts, (pts.Part, ptp.PerformedPart)):
        parts = [parts]
    sparts, pparts = [], []
    for p in parts:
        if isinstance(p, pts.Part):
            sparts.append(p)
        elif isinstance(p, ptp.PerformedPart):
            pparts.append(p)
        else:
            raise TypeError(f"Expected Part or PerformedPart, got {type(p)}")
    events = defaultdict(set)
    for pp in pparts:
        events[ptp.PerformedNote].update(pp.notes)
    if not sparts:
        return dict(events)
    points = np.concatenate([p._points for p in sparts])
    iter_all_event_dicts = map(get_starting_objects_from_point, points)
    for cls2instances in iter_all_event_dicts:
        for cls, instances in cls2instances.items():
            if instances:
                events[cls].update(instances)
    return dict(events)


def get_performed_notes(
    parts: ptp.PerformedPart | Iterable[ptp.PerformedPart],
    ppq: int = 480,
    mpq: int = 500000,
) -> set[ptp.PerformedNote]:
    """Iterates through all PerformedNotes and adds timing information."""
    parts = make_argument_iterable(parts)
    pnotes = set()
    for p in parts:
        if not isinstance(p, ptp.PerformedPart):
            raise TypeError(f"Expected Part or PerformedPart, got {type(p)}")
        for pnote in p.notes:
            note_on_tick, duration_tick, note_on_sec, duration_sec = (
                get_pnote_durations(pnote, ppq, mpq)
            )
            pnote.pnote_dict.update(
                dict(
                    onset_tick=note_on_tick,
                    duration_tick=duration_tick,
                    onset_sec=note_on_sec,
                    duration_sec=duration_sec,
                )
            )
            pnotes.add(pnote)
    return pnotes


def get_events_from_event_dict(
    event_dict: dict[Type[pts.TimedObject], set[pts.TimedObject]],
    included_classes: Optional[Iterable[Type[pts.TimedObject]]] = None,
    excluded_classes: Optional[Iterable[Type[pts.TimedObject]]] = None,
    include_type: bool = True,
) -> set[pts.TimedObject] | set[tuple[pts.TimedObject, str]]:
    event_set = set()
    if included_classes is None:
        selected_classes = list(event_dict.keys())
    else:
        if not isinstance(included_classes, Iterable):
            included_classes = [included_classes]
        selected_classes = [c for c in included_classes if c in event_dict]
    if excluded_classes is not None:
        if not isinstance(excluded_classes, Iterable):
            excluded_classes = [excluded_classes]
        for cls in excluded_classes:
            if cls in selected_classes:
                selected_classes.remove(cls)
    for cls in selected_classes:
        if include_type:
            c_str = cls.__name__
            event_set.update((e, c_str) for e in event_dict[cls])
        else:
            event_set.update(event_dict[cls])
    return event_set


def get_filtered_event_set(
    part: pts.Part, include_type: bool = True
) -> set[pts.TimedObject]:
    """
    Equivalent to `[e for e in part.iter_all() if not isinstance(e, (pts.Rest, pts.Note))]`
    but roughly twice as fast"""
    event_dict = get_event_dict(part)
    excluded_classes = [pts.Rest, pts.Note] + list(iter_subclasses(pts.Note))
    return get_events_from_event_dict(
        event_dict, excluded_classes=excluded_classes, include_type=include_type
    )


def event_array_from_part(
    part,
    event_list: Optional[list[pts.TimedObject]] = None,
    include_key_signature=False,
    include_time_signature=False,
    include_metrical_position=False,
    include_staff=False,
    include_divs_per_quarter=False,
    include_type=True,
):
    if include_time_signature:
        time_signature_map = part.time_signature_map
    else:
        time_signature_map = None

    if include_key_signature:
        key_signature_map = part.key_signature_map
    else:
        key_signature_map = None

    if include_metrical_position:
        metrical_position_map = part.metrical_position_map
    else:
        metrical_position_map = None

    if include_divs_per_quarter:
        divs_per_quarter = get_divs_per_quarter(part)
    else:
        divs_per_quarter = None

    if event_list is None:
        event_list = list(get_filtered_event_set(part))
    events_array = event_array_from_event_list(
        event_list=event_list,
        beat_map=part.beat_map,
        quarter_map=part.quarter_map,
        time_signature_map=time_signature_map,
        key_signature_map=key_signature_map,
        metrical_position_map=metrical_position_map,
        include_staff=include_staff,
        divs_per_quarter=divs_per_quarter,
        include_type=include_type,
    )

    return events_array


def event_array_from_event_list(
    event_list: Iterable[pts.TimedObject] | Iterable[tuple[pts.TimedObject, str]],
    beat_map=None,
    quarter_map=None,
    time_signature_map=None,
    key_signature_map=None,
    metrical_position_map=None,
    include_staff=False,
    divs_per_quarter=None,
    include_type=True,
):
    has_type = False
    for event in event_list:
        has_type = isinstance(event, tuple)
    if include_type:
        fields = [("event_type", "U256")]
    else:
        fields = []
    if beat_map is not None:
        # Preserve the order of the fields
        fields += [("onset_beat", "f4"), ("duration_beat", "f4")]

    if quarter_map is not None:
        fields += [("onset_quarter", "f4"), ("duration_quarter", "f4")]
    fields += [
        ("onset_div", "i4"),
        ("duration_div", "i4"),
    ]

    # fields for key signature
    if key_signature_map is not None:
        fields += [("ks_fifths", "i4"), ("ks_mode", "i4")]

    # fields for time signature
    if time_signature_map is not None:
        fields += [("ts_beats", "i4"), ("ts_beat_type", "i4"), ("ts_mus_beats", "i4")]

    # fields for metrical position
    if metrical_position_map is not None:
        fields += [
            ("is_downbeat", "i4"),
            ("rel_onset_div", "i4"),
            ("tot_measure_div", "i4"),
        ]
    # field for staff
    if include_staff:
        fields += [("staff", "i4")]

    # field for divs_pq
    if divs_per_quarter:
        fields += [("divs_pq", "i4")]

    event_array = []
    for timed_object in event_list:
        event_info = tuple()
        if has_type:
            timed_object, event_type = timed_object
        if include_type:
            if not has_type:
                event_type = timed_object.__class__.__name__
            event_info += (event_type,)
        note_on_div = timed_object.start.t
        note_off_div = -1 if timed_object.end is None else timed_object.end.t
        note_dur_div = -1 if timed_object.duration is None else timed_object.duration

        if beat_map is not None:
            note_on_beat, note_off_beat = beat_map([note_on_div, note_off_div])
            note_dur_beat = note_off_beat - note_on_beat

            event_info += (note_on_beat, note_dur_beat)

        if quarter_map is not None:
            note_on_quarter, note_off_quarter = quarter_map([note_on_div, note_off_div])
            note_dur_quarter = note_off_quarter - note_on_quarter

            event_info += (note_on_quarter, note_dur_quarter)

        event_info += (
            note_on_div,
            note_dur_div,
        )

        if key_signature_map is not None:
            fifths, mode = key_signature_map(note_on_div)

            event_info += (fifths, mode)

        if time_signature_map is not None:
            beats, beat_type, mus_beats = time_signature_map(note_on_div)

            event_info += (beats, beat_type, mus_beats)

        if metrical_position_map is not None:
            rel_onset_div, tot_measure_div = metrical_position_map(note_on_div)

            is_downbeat = 1 if rel_onset_div == 0 else 0

            event_info += (is_downbeat, rel_onset_div, tot_measure_div)

        if include_staff:
            if hasattr(timed_object, "staff") and timed_object.staff:
                event_info += (timed_object.staff,)
            else:
                event_info += (0,)

        if divs_per_quarter:
            event_info += (divs_per_quarter,)

        event_array.append(event_info)

    event_array = np.array(event_array, dtype=fields)

    # sort by onset
    onset_unit, _ = get_time_units_from_note_array(event_array)
    onset_sort_idx = np.argsort(event_array[onset_unit], kind="mergesort")
    event_array = event_array[onset_sort_idx]

    return event_array


def event_df_from_part(
    part: pts.Part,
    event_dict: Optional[dict[Type[pts.TimedObject], list[pts.TimedObject]]] = None,
    note_array=True,
    rest_array=True,
    event_array=True,
    include_pitch_spelling=False,
    include_key_signature=False,
    include_time_signature=False,
    include_metrical_position=False,
    include_grace_notes=False,
    include_staff=False,
    include_divs_per_quarter=False,
    merge_tied_notes=True,
    collapse_rests=True,
    include_type=True,
    meta: Optional[Meta | dict] = None,
) -> DF:
    n_arrays = sum([note_array, rest_array, event_array])
    if not n_arrays:
        raise ValueError(
            "At least one of note_array, rest_array or event_array must be True"
        )
    if meta is None:
        meta = {}
    if include_time_signature:
        time_signature_map = part.time_signature_map
    else:
        time_signature_map = None

    if include_key_signature:
        key_signature_map = part.key_signature_map
    else:
        key_signature_map = None

    if include_metrical_position:
        metrical_position_map = part.metrical_position_map
    else:
        metrical_position_map = None

    div_pq = get_divs_per_quarter(part)
    meta["ticks_per_quarter"] = div_pq
    divs_per_quarter = div_pq if include_divs_per_quarter else None

    if event_dict is None:
        event_dict = get_event_dict(part)

    if isinstance(part, ptp.PerformedPart):
        note_array = note_array_from_performed_note_list(
            event_dict.get(ptp.PerformedNote, [])
        )
        return DF(note_array, meta=meta)

    note_classes = [pts.Note] + list(iter_subclasses(pts.Note))
    rest_classes = [pts.Rest]

    dfs = {}
    if note_array:
        note_set = get_events_from_event_dict(
            event_dict, note_classes, include_type=include_type
        )
        arr = note_array_from_note_list(
            note_list=note_set,
            beat_map=part.beat_map,
            quarter_map=part.quarter_map,
            time_signature_map=time_signature_map,
            key_signature_map=key_signature_map,
            metrical_position_map=metrical_position_map,
            include_pitch_spelling=include_pitch_spelling,
            include_grace_notes=include_grace_notes,
            include_staff=include_staff,
            divs_per_quarter=divs_per_quarter,
            include_type=include_type,
            merge_tied_notes=merge_tied_notes,
        )
        dfs["note"] = pd.DataFrame(arr)
    if rest_array:
        rest_set = get_events_from_event_dict(
            event_dict, rest_classes, include_type=include_type
        )
        arr = rest_array_from_rest_list(
            rest_list=rest_set,
            beat_map=part.beat_map,
            quarter_map=part.quarter_map,
            time_signature_map=time_signature_map,
            key_signature_map=key_signature_map,
            metrical_position_map=metrical_position_map,
            include_pitch_spelling=include_pitch_spelling,
            include_grace_notes=include_grace_notes,
            include_staff=include_staff,
            divs_per_quarter=divs_per_quarter,
            collapse=collapse_rests,
            include_type=include_type,
        )
        dfs["rest"] = pd.DataFrame(arr)
    if event_array:
        event_set = get_events_from_event_dict(
            event_dict,
            excluded_classes=note_classes + rest_classes,
            include_type=include_type,
        )
        arr = event_array_from_event_list(
            event_list=event_set,
            beat_map=part.beat_map,
            quarter_map=part.quarter_map,
            time_signature_map=time_signature_map,
            key_signature_map=key_signature_map,
            metrical_position_map=metrical_position_map,
            include_staff=include_staff,
            divs_per_quarter=divs_per_quarter,
            include_type=include_type,
        )
        dfs["other"] = pd.DataFrame(arr)
    if n_arrays == 1:
        return list(dfs.values())[0]
    dfs = {k: v for k, v in dfs.items() if not v.empty}
    if len(dfs) < 2:
        return list(dfs.values())[0]  # return the first of the empty frames
    df = pd_concat(dfs, names=["event_category", "ix"], meta=meta).sort_values(
        "onset_div"
    )
    df = df.reset_index(level=0, drop=False)
    df = df.reset_index(level=0, drop=True)
    return df


def event_df_from_part_list(
    parts: list[pts.Part | ptp.PerformedPart],
    note_array=True,
    rest_array=True,
    event_array=True,
    include_pitch_spelling=False,
    include_key_signature=False,
    include_time_signature=False,
    include_metrical_position=False,
    include_grace_notes=False,
    include_staff=False,
    include_divs_per_quarter=False,
    merge_tied_notes=True,
    collapse_rests=True,
    include_type=True,
    meta: Optional[Meta | dict] = None,
) -> DF:
    parts = make_argument_iterable(parts)
    if not parts:
        raise ValueError("No parts were given.")
    div_pq_values = {get_divs_per_quarter(p) for p in parts}
    if len(div_pq_values) != 1:
        raise ValueError(
            f"All parts must have the same divs_per_quarter value, got {div_pq_values}"
        )
    # div_pq = div_pq_values.pop()
    # meta["ticks_per_quarter"] = div_pq
    dfs = []
    for part in parts:
        dfs.append(
            event_df_from_part(
                part=part,
                note_array=note_array,
                rest_array=rest_array,
                event_array=event_array,
                include_pitch_spelling=include_pitch_spelling,
                include_key_signature=include_key_signature,
                include_time_signature=include_time_signature,
                include_metrical_position=include_metrical_position,
                include_grace_notes=include_grace_notes,
                include_staff=include_staff,
                include_divs_per_quarter=include_divs_per_quarter,
                merge_tied_notes=merge_tied_notes,
                collapse_rests=collapse_rests,
                include_type=include_type,
                meta=meta,
            )
        )
    if len(dfs) == 1:
        return dfs[0]
    df = pd_concat(dfs, meta=meta).sort_values("onset_div")
    return df


def get_divs_per_quarter(part: pts.Part | ptp.PerformedPart):
    """Get the number of divisions per quarter note for a part.
    Raises NotImplementedError if the part has multiple quarter_durations.
    This will not happen for a PerformedPart because it is always a unique value.
    """
    try:
        parts_quarter_times = part._quarter_times
    except AttributeError:
        return part.ppq
    parts_quarter_durations = part._quarter_durations
    if not len(parts_quarter_durations) == 1:
        raise NotImplementedError(
            "Parts changing their quarter_durations midway are currently not supported. Found quarter_durations",
            parts_quarter_durations,
            "at times",
            parts_quarter_times,
        )
    divs_per_quarter = parts_quarter_durations[0]
    return divs_per_quarter


# endregion parsing with partitura

# region JSON formats


@overload
def explode_nested_json(
    first_level_df: DF,
    column2type: dict[str, str] | str | list,
    type_column_name: Optional[str] = None,
    prepend_column_names: bool = True,
    **kwargs,
) -> DF: ...


@overload
def explode_nested_json(
    first_level_df: pd.DataFrame,
    column2type: dict[str, str] | str | list,
    type_column_name: Optional[str] = None,
    prepend_column_names: bool = True,
    **kwargs,
) -> pd.DataFrame: ...


def explode_nested_json(
    first_level_df: DF | pd.DataFrame,
    column2type: dict[str, str] | str | list,
    type_column_name: Optional[str] = None,
    prepend_column_names: bool = True,
    **kwargs,
) -> DF | pd.DataFrame:
    """Explodes columns containing JSON arrays, joins them onto the other existing columns,
    and concatenates the resulting dataframes.

    Args:
        first_level_df:
            A DataFrame resulting from pd.json_normalize which has at least one column containing JSON arrays.
            The index needs to be unique.
        column2type:
            A mapping of an arbitrary type name to the column to be exploded using pd.json_normalize.
            The type names are only relevant when type_column_name is specified, which is usually a good idea
            when exploding multiple columns.
            Otherwise, this argument can simply be a column name or a list of them.
        type_column_name:
            Name of the indicator column that specifies from which exploded column a record comes.
        prepend_column_names:
            By default, the column name is prepended to the new columns resulting from the explosion.
            Pass False to prevent that.
        kwargs:
            Keyword arguments passed to pd.json_normalize when exploding any array.

    Returns:
        A Dataframe with one row per item in the JSON arrays in the specified columns.
        If type_column_name is specified, it comes with an indicator column of that name.
    """
    drop_type_column = not bool(type_column_name)
    if isinstance(column2type, str):
        column2type = {column2type: column2type}
    elif isinstance(column2type, list):
        column2type = {name: name for name in column2type}
    assert all(
        col in first_level_df.columns for col in column2type.keys()
    ), f"Not all columns specified in type2column are present: {first_level_df.columns}"
    assert (
        first_level_df.index.is_unique
    ), "Dataframe index needs to be unique. Please de-duplicate/reset."

    def explode_arrays(df: pd.DataFrame) -> Optional[pd.DataFrame]:
        """Takes a single-row DataFrame and json_normalizes the specified columns,
        returning a DataFrame that has one row per item per JSON array.
        """
        dfs = {}
        row = df.iloc[0]
        for column, event_type in column2type.items():
            try:
                exploded_array = pd.json_normalize(row[column], **kwargs)
                if prepend_column_names:
                    exploded_array.columns = [
                        f"{column}.{col}" for col in exploded_array
                    ]
                dfs[event_type] = exploded_array
            except Exception:
                continue
        if not dfs:
            return
        names = [type_column_name] if type_column_name else None
        return pd.concat(dfs, names=names).droplevel(-1)

    second_level_df = (
        first_level_df.groupby(level=0)
        .apply(explode_arrays)
        .reset_index(level=-1, drop=drop_type_column)
    )
    result = (
        first_level_df.drop(columns=column2type.keys())
        .join(second_level_df, rsuffix="_exploded")
        .reset_index(drop=True)
    )
    if isinstance(first_level_df, DF):
        return DF(result, meta=first_level_df.get_meta())
    return result


def explode_multiply_nested_arrays(
    df: DF | pd.DataFrame,
    explosion_path: Collection[str | Collection[str]],
    type_column_name: Optional[str] = None,
    prepend_column_names: bool = True,
    **kwargs,
) -> DF | pd.DataFrame:
    """Like explode_nested_json(), but allows for "explosion_paths", meaning that this function
    takes a list where for each string element it behaves exactly like explode_nested_json(), but
    for each list of strings, explode_nested_json() is called in a loop. In other words:

        explode_multiply_nested_arrays(df, [["a", "b", "c"], "d", ["e", "f"]]) is equivalent to:
            explode_nested_json(
                explode_nested_json(
                    explode_nested_json(df, ["a", "d", "e"]),
                    ["b", "f"]
                ), "c"
            )

    When prepend_column_names is True, paths look like this: ["measure", "measure.voice"] because
    the nested arrays are children of previously exploded arrays.
    """
    paths_to_explode = [
        [path] if isinstance(path, str) else path for path in explosion_path
    ]
    assert all(
        path[0] in df.columns for path in paths_to_explode
    ), f"Not all columns specified in explosion_path {explosion_path} are present: {df.columns}"
    exploded_df = df
    for columns_at_level in zip_longest(*paths_to_explode):
        cols = [col for col in columns_at_level if col]
        n_items = len(cols)
        n_paths = n_items - sum(isinstance(col, str) for col in cols)
        if n_paths > 1 and n_items > 1:
            # there are more paths to resolve at this level
            exploded_df = explode_multiply_nested_arrays(
                exploded_df,
                explosion_path=cols,
                type_column_name=type_column_name,
                prepend_column_names=prepend_column_names,
                **kwargs,
            )
        else:
            if n_paths == 1 and n_items == 1:
                cols = cols[0]
            if type_column_name is None:
                type_column_name = "item_type" if len(cols) > 1 else None
            exploded_df = explode_nested_json(
                exploded_df,
                column2type=cols,
                type_column_name=type_column_name,
                **kwargs,
            )
    return exploded_df


def recursively_explode_all_arrays(df):
    """Recursively calls explode_multiply_nested_arrays() on the dataframe as long as it still contains columns where
    the first element is a list.
    """
    column_has_arrays = df.bfill().iloc[0].map(type) == list
    if column_has_arrays.any():
        array_cols = df.columns[column_has_arrays].tolist()
        result = explode_multiply_nested_arrays(df, [array_cols]).dropna(
            axis=1, how="all"
        )
        return recursively_explode_all_arrays(result)
    return df


def turn_json_into_dfs(
    json_like: dict | list,
    metadata: Optional[dict] = None,
    prefix: str = "",
    remove_keys: Optional[Collection[str]] = None,
) -> Dict[str, DF | dict]:
    """Recurses through the JSON structure, collecting literal values as metadata,
    and turning each array into a DF, that is a DataFrame with a ._meta property.
    Nodes that do not contain any array are returned as simple dict.
    """

    def parse_array(
        json_array: list,
        metadata: Meta | dict,
        xml_node: str,
    ) -> DF:
        df = pd.json_normalize(json_array)
        return DF(df, meta=Meta(metadata, xml_node=xml_node))

    result = {}
    if metadata:
        metadata = Meta(metadata)
    else:
        metadata = Meta()
    if not remove_keys:
        remove_keys = []
    elif isinstance(remove_keys, str):
        remove_keys = [remove_keys]
    if isinstance(json_like, list):
        return {prefix: parse_array(json_like, metadata=metadata, xml_node=prefix)}
    children: Dict[str, Tuple[list | dict, str]] = {}
    for key, value in json_like.items():
        # collect metadata first in order to pass it to the lower levels
        if not value or key in remove_keys:
            continue
        if isinstance(value, dict):
            children[key] = (value, "dict")
        elif isinstance(value, list):
            children[key] = (value, "list")
        else:
            record_prefix = f"{prefix}.{key}" if prefix else key
            metadata[record_prefix] = value
    for key, (value, value_type) in children.items():
        record_prefix = f"{prefix}.{key}" if prefix else key
        if value_type == "list":
            result[record_prefix] = parse_array(
                value, metadata=metadata, xml_node=record_prefix
            )
        else:
            result.update(
                turn_json_into_dfs(
                    value,
                    metadata=metadata,
                    prefix=record_prefix,
                    remove_keys=remove_keys,
                )
            )
    if not result and metadata:
        return {prefix: metadata}
    return result


def explode_all_array_columns(
    df: DF,
    type_column_name: Optional[str] = None,
    prepend_column_names: bool = True,
    exclude_columns: Optional[Collection[str]] = None,
) -> DF:
    """type_column_name = None (default) means automatic behaviour:
    add "item_type" column only when more than one array columns are exploded and have to
    to be distinguished.
    """
    if not exclude_columns:
        exclude_columns = []
    array_cols = [
        column
        for column, value in df.iloc[0].items()
        if isinstance(value, list) and column not in exclude_columns
    ]
    if not array_cols:
        return df
    if type_column_name is None:
        type_column_name = "item_type" if len(array_cols) > 1 else None
    return explode_nested_json(
        df,
        column2type=array_cols,
        type_column_name=type_column_name,
        prepend_column_names=prepend_column_names,
    )


def fully_explode_json(
    json_like: dict | list,
    remove_keys: Optional[Collection[str]] = None,
    exclude_columns: Optional[Collection[str]] = None,
) -> Dict[str, DF | dict]:
    """Like turn_json_into_dfs() but in addition, this function explodes columns
    containing JSON arrays.
    """
    dfs = turn_json_into_dfs(json_like, remove_keys=remove_keys)
    result = {}
    for key, df in dfs.items():
        if isinstance(df, dict):
            result[key] = df
        else:
            result[key] = explode_all_array_columns(df, exclude_columns=exclude_columns)
    return result


def partially_explode_json(
    json_like: dict | list,
    explosion_paths: Collection[str | Collection[str]],
    remove_keys: Optional[Collection[str]] = None,
) -> Dict[str, DF | dict]:
    """Like turn_json_into_dfs() but in addition, this function explodes selected columns
    containing JSON arrays.
    """
    columns_to_explode = [
        [path] if isinstance(path, str) else path for path in explosion_paths
    ]
    dfs = turn_json_into_dfs(json_like, remove_keys=remove_keys)
    result = {}
    for key, df in dfs.items():
        if isinstance(df, dict):
            result[key] = df
            continue
        explosion_path = [path for path in columns_to_explode if path[0] in df.columns]
        if not explosion_path:
            result[key] = df
            continue
        exploded_df = explode_multiply_nested_arrays(df, explosion_path)
        result[key] = exploded_df
    return result


def load_json_file(filepath: str) -> dict | list:
    with open(filepath, encoding="utf-8") as f:
        d = json.load(f)
    return d


TILIA_COLUMN_DTYPES = dict(
    time=float,
    level="Int64",
    measure="Int64",
    beat="Int64",
    start_beat="Int64",
    end_beat="Int64",
    start_measure="Int64",
    end_measure="Int64",
    page_number="Int64",
    label="string",
    comments="string",
)


def update_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    dtypes = {
        col: dtype for col, dtype in TILIA_COLUMN_DTYPES.items() if col in df.columns
    }
    df = df.astype(dtypes)
    return df


def parse_tilia_json(filepath) -> DF:
    assert not filepath.endswith(
        ".tla"
    ), "This function parses JSON exported from TiLiA, not .tla files!"
    tla_json = load_json_file(filepath)
    df = fully_explode_json(tla_json)["timelines"]
    df = df.rename(columns={"kind": "timeline", "components.kind": "component"})
    df = df.rename(columns=lambda c: c.replace("components.", ""))
    return update_dtypes(df)


# endregion JSON formats
