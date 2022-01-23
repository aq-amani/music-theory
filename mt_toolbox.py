from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame, pygame.sndarray
import numpy
import scipy.signal
import re
from note import Note
from note import basic_notes

##MIDI stuff
from midiutil import MIDIFile
track    = 0
channel  = 0
duration = 8   # In beats
tempo    = 400  # In BPM
volume   = 100 # 0-127, as per the MIDI standard
instrument = 0 #27 guitar

midi_filename = "out.mid"
##

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

def create_midi(note_list, type, ms = 1.5):
    """writes a midi file

    Arguments:
    note_list -- list of note objects in chord or scale
    type -- 'harmonic' or 'melodic': harmonic for chords and single notes / melodic for scales
    """
    time = 0
    MyMIDI = MIDIFile(1) # One track, defaults to format 1 (tempo track
                     # automatically created)
    MyMIDI.addProgramChange(track, channel, time, instrument)
    MyMIDI.addTempo(track,time, tempo)

    for note in note_list:
        MyMIDI.addNote(track, channel, note.midi_id, time, duration, volume)
        if type == 'scale':
            time += ms
    with open(midi_filename, "wb") as output_file:
        MyMIDI.writeFile(output_file)


def play_chord_midi(chord_notes):
    """Play a combination of notes simultaneously (chord)

    Arguments:
    chord_notes -- List of Note objects respresenting the chord
    """
    #global track, channel, time, duration, tempo, volume, instrument
    #MyMIDI = MIDIFile(1) # One track, defaults to format 1 (tempo track
                     # automatically created)
    #MyMIDI.addProgramChange(track, channel, time, instrument)
    #MyMIDI.addTempo(track,time, tempo)
    print('Chord is now being played..')
    create_midi(chord_notes, 'chord')
    play_midi_file(midi_filename)
    pygame.time.delay(100)

    print('Single notes of the chord are now being played separately..')
    create_midi(chord_notes, 'scale', ms = 3)
    play_midi_file(midi_filename)
    pygame.time.delay(100)

    print('Chord is now being played again..')
    create_midi(chord_notes, 'chord')
    play_midi_file(midi_filename)

def play_chord(chord_notes):
    """Play a combination of notes simultaneously (chord)

    Arguments:
    chord_notes -- List of Note objects respresenting the chord
    """
    chord_wave = 0
    for note in chord_notes:
        chord_wave = sum([chord_wave, sine_wave(note.frequency, sampling)])

    print('Chord is now being played..')
    play_wave(chord_wave, 700)
    pygame.time.delay(100)

    print('Single notes of the chord are now being played separately..')
    for note in chord_notes:
        play_wave(sine_wave(note.frequency, sampling), 500)
    pygame.time.delay(100)

    print('Chord is now being played again..')
    play_wave(chord_wave, 700)

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
    """Play an array of note frequencies ms milliseconds each

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

def construct_and_play_chord(root_note, chord_name, midi, one_root=False):
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
    if midi:
        play_chord_midi(chord_notes)
    else:
        play_chord(chord_notes)

def construct_and_play_scale(root_note, scale_name, mode_name, midi, ms = 300):
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
    if midi:
        play_scale_midi(scale_notes, ms)
    else:
        play_scale(scale_notes, ms)

def get_modal_scale(scale_notes, mode):
    """Return the scale after applying a musical mode to it

    Arguments:
    scale_notes -- A list of Note objects of which the scale to transform is made
    mode -- int representing mode value as in mode_info dict
    """
    return scale_notes[mode-1:]

def play_scale(scale_notes, ms, with_reverse=True):
    """Plays a scale

    Arguments:
    scale_notes -- A list of Note objects of which the scale to play is made
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

def play_scale_midi(scale_notes, ms, with_reverse=True):
    """Plays a scale

    Arguments:
    scale_notes -- A list of Note objects of which the scale to play is made
    ms -- length in milliseconds for each note
    with_reverse -- Plays scale both forward and backwards
    """
    print('Scale is now being played forward ..')
    create_midi(scale_notes, 'scale')
    play_midi_file(midi_filename)

    if with_reverse:
        # Extend scale by the reverse scale
        reverse_scale = scale_notes[::-1]
        scale_notes.extend(reverse_scale[1:]) # drop the first element to nicely play the reverse part

        print('Scale is now being played forward and then backwards..')
        create_midi(scale_notes, 'scale')
        play_midi_file(midi_filename)

def play_note_midi(note, ms):
    """Play a midi note for ms milliseconds

    Arguments:
    note -- note object
    ms -- length in milliseconds for note to play
    """
    create_midi([note], 'note')
    play_midi_file(midi_filename)

def play_midi_file(midi_filename):
    '''Stream music_file in a blocking manner'''
    try:
        clock = pygame.time.Clock()
        pygame.mixer.music.load(midi_filename)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            clock.tick(30) # check if playback has finished
    except KeyboardInterrupt:
        # if user hits Ctrl/C then exit
        # (works only in console mode)
        pygame.mixer.music.fadeout(1000)
        pygame.mixer.music.stop()
        raise SystemExit

def play_note_by_name(note_name, ms, octave, midi):
    """Play one note for ms milliseconds by passing note name

    Arguments:
    note_name -- note name as in C, C#, D..etc
    ms -- length in milliseconds for note to play
    octave -- octave at which to play the note
    midi -- flag whether to play note as midi or as a wave
    """
    note = Note(note_name, octave)
    print(f'\n|_Playing {note_alt_name_appender(note.name)} note in octave {note.octave} | Frequency: {note.frequency} Hz\n')
    if midi:
        play_note_midi(note, ms)
    else:
        play_wave(sine_wave(note.frequency, sampling), ms)

def scale_command_processor(root_name, scale_name, octave, mode_name, midi, ms = 200):
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
        construct_and_play_scale(Note(root_name, octave), scale_name, mode_name, midi)
    elif root_name == 'all' and scale_name !='all':
        # Play specific scale at all roots
        for root_name in basic_notes.keys():
            construct_and_play_scale(Note(root_name, octave), scale_name, mode_name, midi)
            pygame.time.delay(200)
    elif root_name != 'all' and scale_name =='all':
        # Play all scales for a specific root
        for scale_name in all_scale_info.keys():
            construct_and_play_scale(Note(root_name, octave), scale_name, mode_name, midi)
            pygame.time.delay(200)
    else:
        # Play all scales at all roots -- very long
        for scale_name in all_scale_info.keys():
            print(f'\n** {scale_name} scales **')
            for note_name in basic_notes.keys():
                construct_and_play_scale(Note(note_name, octave), scale_name, mode_name, midi)
                pygame.time.delay(200)

def chord_command_processor(root_name, chord_name, octave, midi):
    """Plays a single or multiple chords depending on input

    Arguments:
    root_name -- name of the root note (C, D ..etc or 'all')
    chord_name -- name of the chord to play. 'all' to play all chords
    octave -- octave at which to play the chord
    """
    print(f'\nPlaying [{chord_name}] chord(s) with [{root_name}] as root note(s)')
    if 'all' not in (root_name, chord_name):
        construct_and_play_chord(Note(root_name, octave), chord_name, midi)
    elif root_name == 'all' and chord_name !='all':
        # Play specific chord at all roots
        for root_name in basic_notes.keys():
            construct_and_play_chord(Note(root_name, octave), chord_name, midi)
            pygame.time.delay(200)
    elif root_name != 'all' and chord_name =='all':
        # Play all chords for a specific root
        scale_notes = construct_scale(Note(root_name, octave), all_scale_info['Major']['signature'], 9)
        print_ref_scale(scale_notes)
        for chord_name in all_chord_info.keys():
            construct_and_play_chord(Note(root_name, octave), chord_name, midi, one_root=True)
            pygame.time.delay(200)
    else:
        # Play all chords at all roots -- very long
        for chord_name in all_chord_info.keys():
            print(f'\n** {chord_name} chords **')
            for note_name in basic_notes.keys():
                construct_and_play_chord(Note(note_name, octave), chord_name, midi)
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

def init():
    """Code to initialize pygame"""
    ##pygame 1.9.6
    pygame.mixer.init(sample_rate, -16, 1) # 44.1kHz, 16-bit signed, mono
    # optional volume 0 to 1.0
    #pygame.mixer.music.set_volume(0.8)

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
