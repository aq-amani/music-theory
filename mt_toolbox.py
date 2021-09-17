from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame, pygame.sndarray
import numpy
import scipy.signal
import re
from note import Note
from note import basic_notes

sample_rate = 44100
sampling = 4096    # or 16384

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
def sine_wave(hz, peak, n_samples=sample_rate):
    """Compute N samples of a sine wave with given frequency and peak amplitude.
       Defaults to one second.

    Arguments:
    hz -- sinewave frequency
    peak -- amplitude of wave
    n_samples -- sample rate
    """
    length = sample_rate / float(hz)
    omega = numpy.pi * 2 / length
    xvalues = numpy.arange(int(length)) * omega
    onecycle = peak * numpy.sin(xvalues)
    return numpy.resize(onecycle, (n_samples,)).astype(numpy.int16)

def construct_scale(root_note, scale_signature, scale_length=None):
    """Construct a musical scale from a root note

    Arguments:
    root_name -- root note name of the scale
    scale_signature -- array of frequency ratios between consecutive notes on the scale
    octave -- octave at which to construct the scale with.
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

def construct_chord(chord_signature, base_scale, base_scale_notation):
    """Construct a wave from a combination of simultaneous notes(chord)

    Arguments:
    chord_signature -- indexes of notes within the base scale
    base_scale -- reference scale from where notes are picked up to form chords (note frequencies)
    base_scale_notation -- list of note names
    """
    chord_wave = 0
    chord_notation = []
    for index in chord_signature:
        index_s = int(re.findall(r'\d+', index)[0]) if type(index) is str else index
        note_f, note_name = note_modifier(index, base_scale, base_scale_notation[index_s-1])
        chord_wave = sum([chord_wave, sine_wave(note_f, sampling)])
        chord_notation.append(note_name)
    return chord_wave, chord_notation

def note_modifier(note_index, base_scale, note_name):
    """Returns the frequecy of after sharpening or flattening the note based on # or b modifiers

    Arguments:
    note_index -- Note position index on the major scale
    base_scale -- reference scale from where notes are picked up to form chords
    """
    note_names = list(basic_notes.keys())
    basic_notes_index = note_names.index(note_name)
    if type(note_index) is str:
        i = int(re.findall(r'\d+', note_index)[0])
        if 'b' in note_index:
           note_f = flatten(base_scale[i-1])
           basic_notes_index -= 1
        elif '#' in note_index:
           note_f = sharpen(base_scale[i-1])
           basic_notes_index += 1
    else:
        note_f = base_scale[note_index-1]
    return note_f, note_names[basic_notes_index%len(note_names)]

def play_chord(chord_wave, chord_signature, base_scale):
    """Play a combination of notes simultaneously (chord)

    Arguments:
    chord_wave -- wave object constructed from summing multiple waves representing single notes
    chord_signature -- indexes of notes within the base scale
    base_scale -- reference scale from where notes are picked up to form chords
    """
    print('Chord is now being played..')
    play_wave(chord_wave, 700)
    pygame.time.delay(100)
    print('Single notes of the chord are now being played separately..')
    for index in chord_signature:
        note_f, note_name = note_modifier(index, base_scale, 'C')
        play_wave(sine_wave(note_f, sampling), 500)
    pygame.time.delay(100)
    print('Chord is now being played again..')
    play_wave(chord_wave, 700)

def sharpen(note_f):
    """Increase the note frequency by a half step. Ex.: C becomes C# (C sharp)

    Arguments:
    note_f -- frequency of note in Hz
    """
    return note_f * S

def flatten(note_f):
    """Drop the note frequency by a half step. Ex.: C becomes Cb (C flat)

    Arguments:
    note_f -- frequency of note in Hz
    """

    return note_f / S

def play_wave(wave, ms):
    """Play given samples, as a sound, for ms milliseconds.

    Arguments:
    wave -- wave to play
    ms -- length in milliseconds to play
    """
    # In pygame 1.9.1, we can pass sample_wave directly,
    # but in 1.9.2 they changed the mixer to only accept ints.
    sound = pygame.sndarray.make_sound(wave.astype(numpy.int16))
    sound.play(-1)
    pygame.time.delay(ms)
    sound.stop()

def play_piece(notes_f, ms):
    """Play an array of notes ms milliseconds each

    Arguments:
    notes_f -- array of frequencies
    ms -- length in milliseconds for notes to play
    """

    for n in notes_f:
        play_note_by_frequency(n, ms)

def play_note_by_frequency(note_f, ms):
    """Play one note for ms milliseconds by directly passing its frequency in Hz

    Arguments:
    note_f -- frequency of note in Hz
    ms -- length in milliseconds for note to play
    """
    play_wave(sine_wave(note_f, sampling), ms)

def print_chord(name, root_name, signature, notation):
    """Prints the chord information in a nicely formatted string

    Arguments:
    name -- chord name
    root_name -- name of the root note
    signature -- chord signature (list of indexes on a major scale)
    notation -- chord notation in note names (list of note names)
    """
    positions = '|'.join(f'{str(i):^7}' for i in signature)
    note_names = '|'.join(f'{note_alt_name_appender(n):^7}' for n in notation)
    lines = '+'.join(f'{"-------":7}' for n in notation)
    print(f'|\n|_{name} {note_alt_name_appender(root_name)} chord..:',
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
    octave_multiplier = octave_converter(octave)
    note_names = '|'.join(f'{n+"|"+basic_notes[n]["alt_name"] if basic_notes[n]["alt_name"] else n:^9}' for n in basic_notes.keys())
    frequencies = '|'.join(f'{octave_multiplier*note_info["frequency"]:^9}' for note_info in basic_notes.values())
    lines = '+'.join(f'{"---------":9}' for i in basic_notes.keys())
    print(
    f'\nOctave : {octave}',
    f'\n{"":15}+{lines}+\n{"Note names":15}|{note_names}|\n{"":15}+{lines}+',
    f'\n{"Frequencies(Hz)":15}|{frequencies}|\n{"":15}+{lines}+\n')

def construct_and_play_chord(root_name, chord_name, octave, one_root=False):
    """Constructs a chord and Plays it

    Arguments:
    chord_name -- name of the chord as defined in all_chord_info dict
    root_name -- root note name of the chord
    octave -- octave at which to play the chord
    one_root -- True if running this function for one single root and therefore only needing to print the reference scale once
    """
    scale_frequencies, scale_notation = construct_scale(root_name, all_scale_info['Major']['signature'], octave, 9)
    chord_wave, chord_notation = construct_chord(all_chord_info[chord_name]['signature'], scale_frequencies, scale_notation)
    if not one_root:
        print_ref_scale(scale_notation)
    print_chord(chord_name, root_name, all_chord_info[chord_name]['signature'], chord_notation)
    play_chord(chord_wave, all_chord_info[chord_name]['signature'], scale_frequencies)

def construct_and_play_scale(root_note, scale_name, mode_name, ms = 300):
    """Constructs a scale and Plays it

    Arguments:
    root_name -- name of the root note (C, D ..etc)
    scale_name -- name of the scale to play.
    octave -- octave at which to play the scale
    mode_name -- name of the musical mode mode as defined in the mode_info dict, in which to play the chord (Ionian, Dorian..etc)
    ms -- length in milliseconds for each note
    """
    scale_length = len(all_scale_info[scale_name]['signature']) + mode_info[mode_name] - 1
    scale_notes = construct_scale(root_note, all_scale_info[scale_name]['signature'], scale_length)
    if scale_name == 'Major' and mode_name != 'Ionian':
        scale_notes = get_modal_scale(scale_notes, mode_info[mode_name])
    print_scale(root_note, scale_name, scale_notes, all_scale_info[scale_name]['signature'], mode_name)
    play_scale(scale_notes, ms)

def get_modal_scale(scale_notes, mode):
    """Return the scale after applying a musical mode to it

    Arguments:
    scale_frequencies -- the scale (in terms of note frequencies) to transform
    scale_notation -- the scale (in terms of note names) to transform
    mode -- int representing mode value as in mode_info dict
    """
    return scale_notes[mode-1:]

def play_scale(scale_notes, ms, with_reverse=True):
    """Plays a scale

    Arguments:
    scale_frequencies -- array of notes
    ms -- length in milliseconds for each note
    with_reverse -- Plays scale both forward and backwards
    """
    print('Scale is now being played forward..')
    scale_frequencies = [n.frequency for n in scale_notes]
    play_piece(scale_frequencies, ms)
    if with_reverse:
        # Extend scale by the reverse scale
        reverse_scale = scale_frequencies[::-1]
        scale_frequencies.extend(reverse_scale[1:]) # drop the first element to nicely play the reverse part
        pygame.time.delay(200)
        print('Scale is now being played forward and then backwards..')
        play_piece(scale_frequencies, ms)

def play_note_by_name(note_name, ms, octave):
    """Play one note for ms milliseconds by passing note name

    Arguments:
    note_name -- note name as in C, C#, D..etc
    ms -- length in milliseconds for note to play
    octave -- octave at which to play the note
    """
    octave_multiplier = octave_converter(octave)
    note_name = note_alt_name_converter(note_name)
    note_f = basic_notes[note_name]['frequency'] * octave_multiplier
    print(f'\n|_Playing {note_alt_name_appender(note_name)} note in octave {octave} | Frequency: {note_f} Hz\n')
    play_wave(sine_wave(note_f, sampling), ms)

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
        construct_and_play_chord(root_name, chord_name, octave)
    elif root_name == 'all' and chord_name !='all':
        # Play specific chord at all roots
        for root_name in basic_notes.keys():
            construct_and_play_chord(root_name, chord_name, octave)
            pygame.time.delay(200)
    elif root_name != 'all' and chord_name =='all':
        # Play all chords for a specific root
        _, scale_notation = construct_scale(root_name, all_scale_info['Major']['signature'], 2, 9)
        print_ref_scale(scale_notation)
        for chord_name in all_chord_info.keys():
            construct_and_play_chord(root_name, chord_name, octave, one_root=True)
            pygame.time.delay(200)
    else:
        # Play all chords at all roots -- very long
        for chord_name in all_chord_info.keys():
            print(f'\n** {chord_name} chords **')
            for note_name in basic_notes.keys():
                construct_and_play_chord(note_name, chord_name, octave)
                pygame.time.delay(200)

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

def octave_converter(octave):
    """Converts an octave to a frequency multiplier.
    Octave 4 translates to x1 multiplier since our basic_notes list is based on the 4th octave.

    Arguments:
    octave -- octave at which to play the scale
    """
    return 2 ** (octave - 4)
def init():
    """Code to initialize pygame"""
    ##pygame 1.9.6
    pygame.mixer.init(sample_rate, -16, 1) # 44.1kHz, 16-bit signed, mono

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
else:
    init()
