import re
from note import Note
from note import basic_notes

S = 2**(1/12) # Semi-tone frequency multiplier
T = S ** 2 # Full-tone frequency multiplier
# Mode info
# Modes: Where you start playing at a scale.
mode_info = {
    "Ionian" 		: 1, # Same as Major scale
    "Dorian" 		: 2,
    "Phrygian" 		: 3,
    "Lydian" 		: 4,
    "Mixolydian" 	: 5,
    "Aeolian" 		: 6,
    "Locrian" 		: 7,
}
# Scale signatures
# The last interval is between last note and next octave first note
all_scale_info = {
    "Chromatic" 	: {"signature" : [S,S,S,S,S,S,S,S,S,S,S,S],     "info" : "All 12 notes in an octave"},
    "Major"  		: {"signature" : [T,T,S,T,T,T,S], 		"info" : "The Do Re Me sequence that everyone knows"},
    "Minor" 		: {"signature" : [T,S,T,T,S,T,T], 		"info" : "Aeolian mode of the Major scale"},
    "Harmonic_minor"    : {"signature" : [T,S,T,T,S,T*S,S],             "info" : ""},
    "Phrygian_dominant" : {"signature" : [S,T*S,S,T,S,T,T],             "info" : "Mixolydian mode of the harmonic minor scale"},
    "Double_harmonic"   : {"signature" : [S,T*S,S,T,S,T*S,S],           "info" : "AKA Byzantine scale"},
    "Diminished"  	: {"signature" : [T,S,T,S,T,S,T,S],		"info" : "An octatonic scale"},
    "Augmented" 	: {"signature" : [T*S,S,T*S,S,T*S,S],		"info" : "A hexatonic scale"},
    "Major_pentatonic"  : {"signature" : [T,T,T*S,T,T*S],		"info" : ""},
    "Minor_pentatonic"  : {"signature" : [T*S,T,T,T*S,T],		"info" : ""},
    "Blues" 		: {"signature" : [T*S,T,S,S,T*S,T],		"info" : ""},
}

# Chord signatures
all_chord_info = {
    ##Signatures are respective to the major scale.
    ## Major, minor, dim, aug Triads are all 1,3,5 respective to their own scale.
    "Major_triad" 	: {"signature" : [1,3,'P5'],		"info" : "Happy (-^o^-)"},
    "Minor_triad" 	: {"signature" : [1,'m3',5], 		"info" : "Sad (;_;)"},
    "Power" 		: {"signature" : [1,5,8], 		"info" : "Powerful \m/ Used a lot in rock/metal"},
    "Diminished" 	: {"signature" : [1,'b3','D5'], 	"info" : "Unpleasant dramatic sad (/O;)"},
    "Augmented" 	: {"signature" : [1,3,'A5'], 		"info" : "Mysterious uneasy reality-altering-like ('O')!?"},
    "Suspended_2" 	: {"signature" : [1,2,5], 		"info" : ""},
    "Suspended_4" 	: {"signature" : [1,4,5], 		"info" : ""},
    # Add chords
    "Major_add2"         : {"signature" : [1,2,3,5],            "info" : ""},
    "Minor_add2"         : {"signature" : [1,2,'b3',5],         "info" : ""},
    "Major_add9"         : {"signature" : [1,3,5,9],            "info" : "Same as add2 but 2nd degree is an octave higher"},
    "Minor_add9"         : {"signature" : [1,'b3',5,9],         "info" : "Same as add2 but 2nd degree is an octave higher"},
    # Power variations
    "Power_m6"	         : {"signature" : [1,5,'b6'],           "info" : "with a minor 6th"},
    "Power_m3m6"         : {"signature" : [1,'b3',5,'b6'],      "info" : "with a minor 3rd and minor 6th"},
    "Power_M2m3"         : {"signature" : [1,2,'b3',5],    	"info" : "with a major 2nd and minor 3rd"},
    "Power_m2m3"         : {"signature" : [1,'b2','b3',5],  	"info" : "with a minor 2nd and minor 3rd"},
    "Power_M7"	         : {"signature" : [1,5,7],              "info" : "with a major 7th"},
    # 6ths
    "Major_6th"         : {"signature" : [1,3,5,6],             "info" : ""},
    "Minor_6th"         : {"signature" : [1,'b3',5,6],	        "info" : ""},
    # 7ths
    "Major_7th" 	: {"signature" : [1,3,5,7], 		"info" : ""},
    "Minor_7th" 	: {"signature" : [1,'b3',5,'b7'], 	"info" : ""},
    "Dominant_7th" 	: {"signature" : [1,3,5,'b7'], 		"info" : ""},
    "m7b5"	 	: {"signature" : [1,'b3','b5','b7'], 	"info" : "Kind of Jazzy feel. AKA minor 7th flat 5(m7b5)/ Half_diminished"},
    "Diminished_7th" 	: {"signature" : [1,'b3','b5',6], 	"info" : "Kind of Jazzy feel. AKA Whole_diminished diminished 7th. Last index usually expressed as 'bb7'"},
    "7sus4"	        : {"signature" : [1,4,5,'b7'],	        "info" : ""},
    # 9ths
    "Major_9th" 	: {"signature" : [1,3,5,7,9], 		"info" : "5th note can be ommited without much sound difference"},
    "Minor_9th" 	: {"signature" : [1,'b3',5,'b7',9], 	"info" : "5th note can be ommited without much sound difference"},
    "Dominant_9th" 	: {"signature" : [1,3,5,'b7',9], 	"info" : "5th note can be ommited without much sound difference"},
}

major_key_degree_info = {
    1  : {"offset" : 0, "type" : "Major_triad", "possible_types" : ["Major_triad", "Major_7th", "Suspended_2", "Suspended_4"]},
    2  : {"offset" : 2, "type" : "Minor_triad", "possible_types" : ["Minor_triad", "Minor_7th", "Suspended_2", "Suspended_4"]},
    3  : {"offset" : 4, "type" : "Minor_triad", "possible_types" : ["Minor_triad", "Minor_7th", "Suspended_4"]},
    4  : {"offset" : -1, "type" : "Major_triad","possible_types" : ["Major_triad", "Major_7th", "Suspended_2"]},
    5  : {"offset" : 1, "type" : "Major_triad", "possible_types" : ["Major_triad", "Major_7th", "Suspended_2", "Suspended_4"]},
    6  : {"offset" : 3, "type" : "Minor_triad", "possible_types" : ["Minor_triad", "Minor_7th", "Suspended_2", "Suspended_4"]},
    7  : {"offset" : 5, "type" : "Diminished",  "possible_types" : ["Diminished", "Half_diminished"]},
}

minor_key_degree_info = {
    1  : {"offset" : 0, "type" : "Minor_triad", "possible_types" : ["Minor_triad", "Minor_7th", "Suspended_2", "Suspended_4"]},
    2  : {"offset" : 2, "type" : "Diminished",  "possible_types" : ["Diminished", "Half_diminished"]},
    3  : {"offset" : -3, "type" : "Major_triad", "possible_types" : ["Major_triad", "Major_7th", "Suspended_2", "Suspended_4"]},
    4  : {"offset" : -1, "type" : "Minor_triad", "possible_types" : ["Minor_triad", "Minor_7th", "Suspended_2", "Suspended_4"]},
    5  : {"offset" : 1, "type" : "Minor_triad", "possible_types" : ["Minor_triad", "Minor_7th", "Suspended_2"]},
    6  : {"offset" : -4, "type" : "Major_triad", "possible_types" : ["Major_triad", "Major_7th", "Suspended_2"]},
    7  : {"offset" : -2, "type" : "Major_triad", "possible_types" : ["Major_triad", "Major_7th", "Suspended_2", "Suspended_4"]},
}

# interval name to chromatic position
# modifiers: m,b,D--> -1, A--> +1, M,P-->number as is
interval_to_position_map = {
    1                : 0,
    2                : 2,
    3                : 4,
    4                : 5,
    5                : 7,
    6                : 9,
    7                : 11,
}

piano_keys = """
Piano keyboard reference:

|-S-|
 ___________________________
|  | | | |  |  | | | | | |  |
|  |C| |D|  |  |F| |G| |A|  |
|  |#| |#|  |  |#| |#| |#|  |
|  |_| |_|  |  |_| |_| |_|  |
|   |   |   |   |   |   |   |
| C | D | E | F | G | A | B |
|___|___|___|___|___|___|___|
  |-T-|

S: Semintone
T: Full Tone
"""

header = """
Music Theory python lab
(c) 2021 Amani AbuQdais
https://github.com/aq-amani/music-theory
 ___________________________
|  | | | |  |  | | | | | |  |
|  |C| |D|  |  |F| |G| |A|  |
|  |#| |#|  |  |#| |#| |#|  |
|  |_| |_|  |  |_| |_| |_|  |
|   |   |   |   |   |   |   |
| C | D | E | F | G | A | B |
|___|___|___|___|___|___|___|
/////////////////////////////
"""

def construct_scale(root_name, scale_name, mode_name, octave=4, scale_length=None):
    """Construct a musical scale from a root note

    Arguments:
    root_name -- name of root note
    scale_name -- name of the scale
    mode_name -- name of the musical mode mode as defined in the mode_info dict, in which to play the chord (Ionian, Dorian..etc)
    scale_length -- Defaults to standard scale length. Specify when needing non-standard scale length (ex.: span multiple octaves)
    """
    root_note = Note(root_name, octave) if root_name != 'all' else 'all'
    scale_signature = all_scale_info[scale_name]['signature'] if scale_name != 'all' else 'all'
    if not scale_length:
        # If not specified, default to standard scale length
        scale_length = len(scale_signature) + 1
    if mode_name != 'Ionian':
        if len(scale_signature) != 7:
            raise ValueError("Error: Modes not supported for non-heptatonic scales")
        scale_signature = get_modal_scale_signature(scale_name, mode_name)
    scale_notes = [root_note]
    note = root_note
    for i in range(scale_length - 1):
        halfstep_count = 1 if scale_signature[i % len(scale_signature)] == S else 2 if scale_signature[i % len(scale_signature)] == T else 3
        note = note.get_next_step_note(halfstep_count)
        scale_notes.append(note)

    return scale_notes

def construct_chord(root_name, chord_name, octave=4):
    """Construct a wave from a combination of simultaneous notes(chord)

    Arguments:
    root_name -- name of root note
    chord_name -- name of the chord
    """
    root_note = Note(root_name, octave) if root_name != 'all' else 'all'
    chord_signature = all_chord_info[chord_name]['signature'] if chord_name != 'all' else 'all'
    base_scale_notes = construct_scale(root_name, 'Major', 'Ionian', octave, 9)
    chord_notes = []

    for index in chord_signature:
        index_s = int(re.findall(r'\d+', index)[0]) if type(index) is str else index
        note = note_modifier(index, base_scale_notes[index_s-1])
        chord_notes.append(note)
    return chord_notes

def note_modifier(note_index, note):
    """Returns a modified Note object after sharpening or flattening the note based on # or b modifiers
       modifiers: m(minor),b(flat),D(diminished)--> -1,
                  A(augmented), # (sharp)--> +1,
                  M(major),P(Perfect)--> 0 (number as is)
    Arguments:
    note_index -- Note position index on the major scale
    note -- Note object to flatten or to sharpen
    """
    modifier = 0
    if type(note_index) is str:
        i = int(re.findall(r'\d+', note_index)[0])
        if 'b' in note_index  or 'm' in note_index or 'D' in note_index:
           modifier = -1
        elif '#' in note_index or 'A' in note_index:
           modifier = 1
    modified_note = note.get_next_step_note(modifier)
    return modified_note

def intervals_to_chrom_positions(intervals):
    """Returns a list of chromatic positions from a list of musical intervals(m2,P5..)
       modifiers: m(minor),b(flat),D(diminished)--> -1,
                  A(augmented), # (sharp)--> +1,
                  M(major),P(Perfect)--> 0 (number as is)

    Arguments:
    intervals -- a list of intervals. ex.: ['1','m3','P5']
    """
    positions = []
    for i in intervals:
        modifier = 0
        if type(i) is str:
            n = int(re.findall(r'\d+', i)[0])
            if 'b' in i or 'm' in i or 'D' in i:
               modifier = -1
            elif '#' in i or 'A' in i:
               modifier = 1
        else:
            n = i
        # if intervals exceeding one octave were provided restart counting at 1
        if n > 7:
            n = n%7
        positions.append(interval_to_position_map[n] + modifier)
    return positions

def tone_to_chrom_positions(signature):
    """Returns a list of chromatic positions from a list of tone,semitone (T, S) signatures

    Arguments:
    signature -- a list of tone/semitone values representing a signatureex.: [T,S,T*S]
    """
    pos = 0
    positions = []
    positions.append(pos)
    # exclude the last interval (last note- next octave first note interval)
    for i in signature[:-1]:
        if i == S:
            pos += 1
        elif i == T:
            pos += 2
        elif i == T*S:
            pos += 3
        else:
            print('Error. Unexpected signature element.')
        positions.append(pos)
    return positions

def print_chord(root_name, chord_name, chord_notes):
    """Prints the chord information in a nicely formatted string

    Arguments:
    root_name -- Root name
    chord_name -- chord name
    chord_notes -- List of Note objects out of which the chord is constructed
    """
    signature = all_chord_info[chord_name]['signature']
    positions = '|'.join(f'{str(i):^7}' for i in signature)
    note_names = '|'.join(f'{note_alt_name_appender(n.name):^7}' for n in chord_notes)
    lines = '+'.join(f'{"-------":7}' for n in chord_notes)
    print(f'|\n|_{chord_name} {note_alt_name_appender(root_name)} chord..:',
    f'\n{"  Chord info: ":12}{all_chord_info[chord_name]["info"]}',
    f'\n{"":12}+{lines}+\n{"positions":12}|{positions}|\n{"":12}+{lines}+'
    f'\n{"Note names":12}|{note_names}|\n{"":12}+{lines}+')

def print_scale(root_name, scale_name, scale_notes, mode='Ionian'):
    """Prints the scale information in a nicely formatted string"""
    scale_signature = all_scale_info[scale_name]['signature']
    positions = '|'.join(f'{str(i):^7}' for i in range(1,len(scale_notes)+1))
    note_names = '|'.join(f'{note_alt_name_appender(n.name):^7}' for n in scale_notes)
    signature = '--|--'.join(f'{"S" if s == S else "T" if s==T else "T.S":^3}' for s in scale_signature)
    lines = '+'.join(f'{"-------":7}' for n in scale_notes)
    print(
    f'|\n|_{note_alt_name_appender(root_name)} {mode}' if mode != 'Ionian' else f'|\n|_{note_alt_name_appender(root_name)}',
    f'of the {scale_name} scale.. :' if mode != 'Ionian' else f'{scale_name} scale.. :',
    f'\n{"":15}+{lines}+\n{"positions":15}|{positions}|\n{"":15}+{lines}+',
    f'\n{"Note names":15}|{note_names}|\n{"":15}+{lines}+',
    f'\n{"Scale Signature":19}|--{signature}--|')

def print_ref_scale(scale_notes):
    """Prints the reference scale (an extended major scale) based on which a chord is constructed"""
    positions = '|'.join(f'{str(i):^7}' for i in range(1,len(scale_notes)+1))
    note_names = '|'.join(f'{note_alt_name_appender(n.name):^7}' for n in scale_notes)
    lines = '+'.join(f'{"-------":7}' for n in scale_notes)
    print(f'\nBase Major scale (extended) with position numbers:\n+{lines}+\n|{positions}|\n+{lines}+\n|{note_names}|\n+{lines}+')

def print_note_info(octave):
    """Prints a table of notes and their frequencies at a certain octave"""
    start_note = Note('C', octave)
    note_list = start_note.get_consecutive_notes(12)
    note_names = '|'.join(f'{n.name+"|"+n.alt_name if n.alt_name else n.name:^9}' for n in note_list)
    frequencies = '|'.join(f'{n.frequency:^9}' for n in note_list)
    lines = '+'.join(f'{"---------":9}' for i in note_list)
    print(
    f'\nOctave : {octave}',
    f'\n{"":15}+{lines}+\n{"Note names":15}|{note_names}|\n{"":15}+{lines}+',
    f'\n{"Frequencies(Hz)":15}|{frequencies}|\n{"":15}+{lines}+\n')

def get_modal_scale_signature(scale_name, mode_name):
    """Return the modal scale signature by left rotating the signature according to the mode value
       Ex.: Dorian starts from the second position hence a left rotation by 1

    Arguments:
    scale_name -- name of the scale
    mode_name -- name of the mode
    """
    signature = all_scale_info[scale_name]['signature']
    mode_index = mode_info[mode_name]
    # left rotate by mode value-1
    modal_signature = signature[mode_index-1:]+signature[:mode_index-1]
    return modal_signature

def get_chord_list_from_progression(key, progression):
    """Returns a list of chords representing a chord progression

    Arguments:
    key -- Key in which to play the progression (C, Dm ..etc)
    progression -- list of integers(1~7) representing the degree of each chord within the key
    """
    chord_list = []
    type_list = []
    if 'm' in key:
        base_scale_name = 'Minor'
        key = re.sub('m', '', key)
        degree_info = minor_key_degree_info
    else:
        base_scale_name = 'Major'
        degree_info = major_key_degree_info
    base_scale = construct_scale(root_name=key, scale_name=base_scale_name, mode_name='Ionian', octave=4)
    for degree in progression:
        degree = int(degree)
        chord_list.append(base_scale[degree-1].name)
        type_list.append(degree_info[degree]['type'])
    return chord_list, type_list

def note_alt_name_appender(note_name):
    """Returns a string of note_name and its alternative name if one exists
    Only to be used when printing notes.
    returned string format: <note_name>|<alternative_name>
    """
    # Make sure that note_name is converted to the # notation instead of b notation if needed
    # to use it as a key to access the basic_notes dict
    note_name = note_alt_name_converter(note_name)
    if basic_notes[note_name]['alt_name']:
        note_name = f'{note_name}|{basic_notes[note_name]["alt_name"]}'
    return note_name

def note_alt_name_converter(note_name):
    """Returns the note_name key in basic_notes, if a note is passed using the alt_name notation
    Ex.: Eb returns D#
    """
    if 'b' in note_name:
        for basic_name, note_info in basic_notes.items():
            if note_info['alt_name'] == note_name:
                note_name = basic_name
                break
    return note_name

if __name__ == '__main__':
    print(header)
