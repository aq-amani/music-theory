import re
from note import Note
from note import basic_notes
import pygame.time
import playback as pb


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
all_scale_info = {
    "Chromatic" 	: {"signature" : [S,S,S,S,S,S,S,S,S,S,S,S],     "info" : "All 12 notes in an octave"},
    "Major"  		: {"signature" : [T,T,S,T,T,T,S], 		"info" : "The Do Re Me sequence that everyone knows"},
    "Minor" 		: {"signature" : [T,S,T,T,S,T,T], 		"info" : ""},
    "Diminished"  	: {"signature" : [T,S,T,S,T,S,T],		"info" : ""},
    "Augmented" 	: {"signature" : [T*S,S,T*S,S,T*S,S,T*S],	"info" : ""},
    "Major_pentatonic"  : {"signature" : [T,T,T*S,T,T*S],		"info" : ""},
    "Minor_pentatonic"  : {"signature" : [T*S,T,T,T*S,T],		"info" : ""},
    "Blues" 		: {"signature" : [T*S,T,S,S,T*S,T],		"info" : ""},
}

# Chord signatures
all_chord_info = {
    ##Signatures are respective to the major scale.
    ## Major, minor, dim, aug Triads are all 1,3,5 respective to their own scale.
    "Major_triad" 	: {"signature" : [1,3,5],		"info" : "Happy (-^o^-)"},
    "Minor_triad" 	: {"signature" : [1,'b3',5], 		"info" : "Sad (;_;)"},
    "Power" 		: {"signature" : [1,5,8], 		"info" : "Powerful \m/ Used a lot in rock/metal"},
    "Diminished" 	: {"signature" : [1,'b3','b5'], 	"info" : "Unpleasant dramatic sad (/O;)"},
    "Augmented" 	: {"signature" : [1,3,'5#'], 		"info" : "Mysterious uneasy reality-altering-like ('O')!?"},
    "Suspended_2" 	: {"signature" : [1,2,5], 		"info" : ""},
    "Suspended_4" 	: {"signature" : [1,4,5], 		"info" : ""},
    "Major_7th" 	: {"signature" : [1,3,5,7], 		"info" : ""},
    "Minor_7th" 	: {"signature" : [1,'b3',5,'b7'], 	"info" : ""},
    "Dominant_7th" 	: {"signature" : [1,3,5,'b7'], 		"info" : ""},
    "Half_diminished" 	: {"signature" : [1,'b3','b5','b7'], 	"info" : "Kind of Jazzy feel. AKA minor 7th flat 5(m7b5)"},
    "Whole_diminished" 	: {"signature" : [1,'b3','b5',6], 	"info" : "Kind of Jazzy feel. AKA diminished 7th"},
    #Last index of diminished 7th usually expressed as 'bb7' but this script doesn't support double flats. 'bb7' is 6 on a major scale.
    "Major_9th" 	: {"signature" : [1,3,5,7,9], 		"info" : "5th note can be ommited without much sound difference"},
    "Minor_9th" 	: {"signature" : [1,'b3',5,'b7',9], 	"info" : "5th note can be ommited without much sound difference"},
    "Dominant_9th" 	: {"signature" : [1,3,5,'b7',9], 	"info" : "5th note can be ommited without much sound difference"},
}

# Circle of fifths and keys for chord progressions
circle_of_fifths = ['C', 'G', 'D', 'A', 'E', 'B', 'F#', 'C#', 'G#', 'D#', 'A#', 'F']
minor_flag = False
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

def get_chord_in_key(key_index, degree):
    """Obtains a chord from the set of chords in a key based on its degree

    Arguments:
    key_index -- index of the key chord within the circle_of_fifths list
    degree -- degree of chord (1st ~ 7th)
    """
    degree_info = minor_key_degree_info if minor_flag else major_key_degree_info
    chord_index = key_index + degree_info[degree]['offset']

    if chord_index < 0:
        chord_index += 12
    else:
        chord_index = chord_index % 12
    return circle_of_fifths[chord_index]

def construct_scale(root_note, scale_signature, scale_length=None):
    """Construct a musical scale from a root note

    Arguments:
    root_note -- A root note object from class Note
    scale_signature -- array of frequency ratios between consecutive notes on the scale
    scale_length -- Defaults to standard scale length. Specify when needing non-standard scale length (ex.: span multiple octaves)
    """
    if not scale_length:
        # If not specified, default to standard scale length
        scale_length = len(scale_signature)
    scale_notes = [root_note]
    note = root_note
    for i in range(scale_length):
        halfstep_count = 1 if scale_signature[i % len(scale_signature)] == S else 2 if scale_signature[i % len(scale_signature)] == T else 3
        note = note.get_next_step_note(halfstep_count)
        scale_notes.append(note)

    return scale_notes

def construct_chord(chord_signature, base_scale_notes):
    """Construct a wave from a combination of simultaneous notes(chord)

    Arguments:
    chord_signature -- indexes of notes within the base scale
    base_scale_notes -- a list of Note objects representing a reference scale from where notes are picked up to form chords
    """
    chord_notes = []
    for index in chord_signature:
        index_s = int(re.findall(r'\d+', index)[0]) if type(index) is str else index
        note = note_modifier(index, base_scale_notes[index_s-1])
        chord_notes.append(note)
    return chord_notes

def note_modifier(note_index, note):
    """Returns a modified Note object after sharpening or flattening the note based on # or b modifiers

    Arguments:
    note_index -- Note position index on the major scale
    note -- Note object to flatten or to sharpen
    """
    if type(note_index) is str:
        i = int(re.findall(r'\d+', note_index)[0])
        if 'b' in note_index:
           modified_note = note.get_next_step_note(-1)
        elif '#' in note_index:
           modified_note = note.get_next_step_note(1)
    else:
        modified_note = note
    return modified_note

def print_chord(name, root_note, signature, chord_notes):
    """Prints the chord information in a nicely formatted string

    Arguments:
    name -- chord name
    root_note -- Note object representing the root note
    signature -- chord signature (list of indexes on a major scale)
    chord_notes -- List of Note objects out of which the chord is constructed
    """
    positions = '|'.join(f'{str(i):^7}' for i in signature)
    note_names = '|'.join(f'{note_alt_name_appender(n.name):^7}' for n in chord_notes)
    lines = '+'.join(f'{"-------":7}' for n in chord_notes)
    print(f'|\n|_{name} {note_alt_name_appender(root_note.name)} chord..:',
    f'\n{"  Chord info: ":12}{all_chord_info[name]["info"]}',
    f'\n{"":12}+{lines}+\n{"positions":12}|{positions}|\n{"":12}+{lines}+'
    f'\n{"Note names":12}|{note_names}|\n{"":12}+{lines}+')

def print_scale(root_note, scale_name, scale_notes, scale_signature, mode='Ionian'):
    """Prints the scale information in a nicely formatted string"""
    positions = '|'.join(f'{str(i):^7}' for i in range(1,len(scale_notes)+1))
    note_names = '|'.join(f'{note_alt_name_appender(n.name):^7}' for n in scale_notes)
    signature = '--|--'.join(f'{"S" if s == S else "T" if s==T else "T.S":^3}' for s in scale_signature)
    lines = '+'.join(f'{"-------":7}' for n in scale_notes)
    print(
    f'|\n|_{note_alt_name_appender(root_note.name)} {scale_name} scale',
    f'in {mode} mode.. :' if mode != 'Ionian' else '(default Ionian mode).. :',
    f'\n{"":15}+{lines}+\n{"positions":15}|{positions}|\n{"":15}+{lines}+',
    f'\n{"Note names":15}|{note_names}|\n{"":15}+{lines}+',
    # Print scale signature only when we are in Ionian (default) as signature becomes irrlevant with other modes
    f'\n{"Scale Signature":19}|--{signature}--|' if mode == 'Ionian' else '')

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

def construct_and_play_chord(root_note, chord_name, one_root=False):
    """Constructs a chord and Plays it

    Arguments:
    root_note -- Note object representing the root note
    chord_name -- name of the chord as defined in all_chord_info dict
    one_root -- True if running this function for one single root and therefore only needing to print the reference scale once
    """
    scale_notes = construct_scale(root_note, all_scale_info['Major']['signature'], 9)
    chord_notes = construct_chord(all_chord_info[chord_name]['signature'], scale_notes)
    if not one_root:
        print_ref_scale(scale_notes)
    print_chord(chord_name, root_note, all_chord_info[chord_name]['signature'], chord_notes)
    pb.play_chord(chord_notes)

def construct_and_play_scale(root_note, scale_name, mode_name, ms = 300):
    """Constructs a scale and Plays it

    Arguments:
    root_note -- Note object representing the root note
    scale_name -- name of the scale to play.
    mode_name -- name of the musical mode mode as defined in the mode_info dict, in which to play the chord (Ionian, Dorian..etc)
    ms -- length in milliseconds for each note
    """
    scale_length = len(all_scale_info[scale_name]['signature']) + mode_info[mode_name] - 1
    scale_notes = construct_scale(root_note, all_scale_info[scale_name]['signature'], scale_length)
    if scale_name == 'Major' and mode_name != 'Ionian':
        scale_notes = get_modal_scale(scale_notes, mode_info[mode_name])
    print_scale(root_note, scale_name, scale_notes, all_scale_info[scale_name]['signature'], mode_name)
    pb.play_scale(scale_notes, ms)

def get_modal_scale(scale_notes, mode):
    """Return the scale after applying a musical mode to it

    Arguments:
    scale_notes -- A list of Note objects of which the scale to transform is made
    mode -- int representing mode value as in mode_info dict
    """
    return scale_notes[mode-1:]

def scale_command_processor(root_name, scale_name, octave, mode_name, ms = 200):
    """Plays single or multiple scales depending on the input

    Arguments:
    root_name -- name of the root note (C, D ..etc or 'all')
    scale_name -- name of the scale to play. 'all' to play all scales
    octave -- octave at which to play the scale
    mode_name -- name of the musical mode mode as defined in the mode_info dict, in which to play the chord (Ionian, Dorian..etc)
    ms -- length in milliseconds for each note
    """
    print(f'\nPlaying [{scale_name}] scale(s) with [{root_name}] as root note(s) in the [{mode_name}] mode')
    if 'all' not in (root_name, scale_name):
        # Play specific scale at specific root
        construct_and_play_scale(Note(root_name, octave), scale_name, mode_name)
    elif root_name == 'all' and scale_name !='all':
        # Play specific scale at all roots
        for root_name in basic_notes.keys():
            construct_and_play_scale(Note(root_name, octave), scale_name, mode_name)
            pygame.time.delay(200)
    elif root_name != 'all' and scale_name =='all':
        # Play all scales for a specific root
        for scale_name in all_scale_info.keys():
            construct_and_play_scale(Note(root_name, octave), scale_name, mode_name)
            pygame.time.delay(200)
    else:
        # Play all scales at all roots -- very long
        for scale_name in all_scale_info.keys():
            print(f'\n** {scale_name} scales **')
            for note_name in basic_notes.keys():
                construct_and_play_scale(Note(note_name, octave), scale_name, mode_name)
                pygame.time.delay(200)

def chord_command_processor(root_name, chord_name, octave):
    """Plays a single or multiple chords depending on input

    Arguments:
    root_name -- name of the root note (C, D ..etc or 'all')
    chord_name -- name of the chord to play. 'all' to play all chords
    octave -- octave at which to play the chord
    """
    print(f'\nPlaying [{chord_name}] chord(s) with [{root_name}] as root note(s)')
    if 'all' not in (root_name, chord_name):
        construct_and_play_chord(Note(root_name, octave), chord_name)
    elif root_name == 'all' and chord_name !='all':
        # Play specific chord at all roots
        for root_name in basic_notes.keys():
            construct_and_play_chord(Note(root_name, octave), chord_name)
            pygame.time.delay(200)
    elif root_name != 'all' and chord_name =='all':
        # Play all chords for a specific root
        scale_notes = construct_scale(Note(root_name, octave), all_scale_info['Major']['signature'], 9)
        print_ref_scale(scale_notes)
        for chord_name in all_chord_info.keys():
            construct_and_play_chord(Note(root_name, octave), chord_name, one_root=True)
            pygame.time.delay(200)
    else:
        # Play all chords at all roots -- very long
        for chord_name in all_chord_info.keys():
            print(f'\n** {chord_name} chords **')
            for note_name in basic_notes.keys():
                construct_and_play_chord(Note(note_name, octave), chord_name)
                pygame.time.delay(200)

def note_processor(note_name, octave):
    """Plays a single note

    Arguments:
    note_name -- name of the note (C, D, F# ..etc )
    octave -- octave at which to play the note
    """
    note = Note(note_name, octave)
    print(f'\n|_Playing {note_alt_name_appender(note.name)} note in octave {note.octave} | Frequency: {note.frequency} Hz\n')
    pb.play_note(note, 700)

def command_processor(args):
    """Main command processor

    Arguments:
    args -- flags and input passed to the script
    """
    print(header)
    if(args['keyboard']):
        print(piano_keys)
    if(args['midi']):
        pb.MIDI = True
    if args['scale']:
        if args['scale'] != list(all_scale_info.keys())[0] and args['mode'] != list(mode_info)[0]:
            parser.error("**Scales other than the Major scale do not support modes other than Ionian (default scale as is)**")
        pb.REVERSE_SCALE = True
        scale_command_processor(args['root'], args['scale'], args['octave'], args['mode'])
    elif args['chord']:
        if args['mode'] != list(mode_info)[0]:
            parser.error("**Modes other than the default Ionian are not supported for chords**")
        pb.ARPEGGIATE = True
        chord_command_processor(args['root'], args['chord'], args['octave'])
    elif args['note']:
        if args['mode'] != list(mode_info)[0]:
            parser.error("**Modes other than the default Ionian are not supported for notes**")
        print_note_info(args['octave'])
        note_processor(args['note'], args['octave'])
    elif args['list']:
        list_supported_values()
    elif args['progression']:
        key = args['key']
        progression = args['progression']
        chord_progression_processor(key, progression)
    elif args['tutorial']:
        import sensei_mode

def chord_progression_processor(key, progression):
    """Plays a progression of chords

    Arguments:
    key -- Key in which to play the progression (C, Dm ..etc)
    progression -- list of integers(1~7) representing the degree of each chord within the key
    """
    global minor_flag
    if 'm' in key:
        minor_flag = True
    key = re.sub('m', '', key)
    print(f'Playing the following progression in {key} {"minor" if minor_flag else "Major"} : {progression}')
    key_index = circle_of_fifths.index(key)
    degree_info = minor_key_degree_info if minor_flag else major_key_degree_info
    for degree in progression:
        degree = int(degree)
        chord = get_chord_in_key(key_index, degree)
        print(degree, chord)
        type = degree_info[degree]['type']
        chord_command_processor(chord, type, 4)

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

def list_supported_values():
    """Lists available values for the different options"""
    print('## Supported notes (-n options)')
    for n in basic_notes.keys():
        print('|_',n, f'({basic_notes[n]["alt_name"]})' if basic_notes[n]["alt_name"] else '')
    print('\n## Supported scales (-s options)')
    for s in list(all_scale_info.keys()):
        print('|_',s)
    print('\n## Supported chords (-c options)')
    for c in list(all_chord_info.keys()):
        print('|_',c)
    print('\n## Supported musical modes (-m options)')
    for m in list(mode_info.keys()):
        print('|_',m)

if __name__ == '__main__':
    print(header)
