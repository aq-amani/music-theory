from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame, pygame.sndarray
import numpy
import scipy.signal
import re
import argparse

sample_rate = 44100
sampling = 4096    # or 16384

S = 2**(1/12) # Semi-tone frequency multiplier
T = S ** 2 # Full-tone frequency multiplier
## TODO: Review requirements on another environment
## TODO: Sensei mode: Note list, note sound, frequency relation, octave, scales (familiar major), chord, signatures, # and b
## TODO: Add logging

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
scale_info = {
    "Major"  		: {"signature" : [T,T,S,T,T,T,S], 		"info" : "The Do Re Me sequence that everyone knows"},
    "Minor" 		: {"signature" : [T,S,T,T,S,T,T], 		"info" : ""},
    "Diminished"  	: {"signature" : [T,S,T,S,T,S,T],		"info" : ""},
    "Augmented" 	: {"signature" : [T*S,S,T*S,S,T*S,S,T*S],	"info" : ""},
    "Major_pentatonic"  : {"signature" : [T,T,T*S,T,T*S],		"info" : ""},
    "Minor_pentatonic"  : {"signature" : [T*S,T,T,T*S,T],		"info" : ""},
    "Blues" 		: {"signature" : [T*S,T,S,S,T*S,T],		"info" : ""},
}

# Chord signatures
chord_info = {
    ##Signatures are respective to the major scale.
    ## Major, minor, dim, aug Triads are all 1,3,5 respective to their own scale.
    "Major_triad" 	: {"signature" : [1,3,5],		"info" : "Happy feel."},
    "Minor_triad" 	: {"signature" : [1,'b3',5], 		"info" : "Sad feel."},
    "Power" 		: {"signature" : [1,5,8], 		"info" : "Powerful feel. Used a lot in rock/metal"},
    "Diminished" 	: {"signature" : [1,'b3','b5'], 	"info" : "Unpleasant dramatic sad feel."},
    "Augmented" 	: {"signature" : [1,3,'5#'], 		"info" : "Mysterious uneasy reality-altering-like feel."},
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

#Octave 4
basic_notes = {
    "C"  : 261.63,
    "C#" : 277.18,
    "D"  : 293.66,
    "D#" : 311.13,
    "E"  : 329.63,
    "F"  : 349.23,
    "F#" : 369.99,
    "G"  : 392.00,
    "G#" : 415.30,
    "A"  : 440.00,
    "A#" : 466.16,
    "B"  : 493.88,
}

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

def construct_scale(root, scale_signature, octave, scale_length=None):
    """Construct a musical scale from a root note

    Arguments:
    root -- root note name of the scale
    scale_signature -- array of frequency ratios between consecutive notes on the scale
    octave -- octave with which to construct the scale with. 1 is for frequencies in basic_notes
    scale_length -- Defaults to standard scale length. Specify when needing non-standard scale length (ex.: span multiple octaves)
    """
    note = basic_notes[root] * octave
    if not scale_length:
        # If not specified, default to standard scale length
        scale_length = len(scale_signature)
    scale = []
    note_names = list(basic_notes.keys())
    name_index = note_names.index(root)
    scale_notation = []
    scale.append(note)
    scale_notation.append(root)
    for i in range(scale_length):
        note *= scale_signature[i % len(scale_signature)]
        note = round(note,2)
        scale.append(note)
        name_index += 1 if scale_signature[i % len(scale_signature)] == S else 2 if scale_signature[i % len(scale_signature)] == T else 3
        scale_notation.append(note_names[name_index%len(note_names)])

    return scale, scale_notation

def construct_chord(chord_signature, base_scale):
    """Construct a wave from a combination of simultaneous notes(chord)

    Arguments:
    chord_signature -- indexes of notes within the base scale
    base_scale -- reference scale from where notes are picked up to form chords
    """
    chord = 0
    for index in chord_signature:
        note = note_modifier(index, base_scale)
        chord = sum([chord, sine_wave(note, sampling)])
    return chord

def note_modifier(note_index, base_scale):
    """Returns the frequecy of after sharpening or flattening the note based on # or b modifiers

    Arguments:
    note_index -- Note position index on the major scale
    base_scale -- reference scale from where notes are picked up to form chords
    """
    if type(note_index) is str:
        i = int(re.findall(r'\d+', note_index)[0])
        if 'b' in note_index:
           note = flatten(base_scale[i-1])
           #print (f'{n} is flat {i}')
        elif '#' in note_index:
           note = sharpen(base_scale[i-1])
           #print (f'{n} is sharp {i}')
    else:
        note = base_scale[note_index-1]
    return note

def play_chord(chord, chord_signature, base_scale):
    """Play a combination of notes simultaneously (chord)

    Arguments:
    chord -- wave object constructed from summing multiple waves representing single notes
    chord_signature -- indexes of notes within the base scale
    base_scale -- reference scale from where notes are picked up to form chords
    """
    play_wave(chord, 700)
    pygame.time.delay(100)
    for index in chord_signature:
        note = note_modifier(index, base_scale)
        play_wave(sine_wave(note, sampling), 500)
    pygame.time.delay(100)
    play_wave(chord, 700)

def sharpen(note):
    """Increase the note frequency by a half step. Ex.: C becomes C# (C sharp)

    Arguments:
    note -- frequency of note in Hz
    """
    return note * S

def flatten(note):
    """Drop the note frequency by a half step. Ex.: C becomes Cb (C flat)

    Arguments:
    note -- frequency of note in Hz
    """

    return note / S

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

def play_piece(notes, ms):
    """Play an array of notes ms milliseconds each

    Arguments:
    notes -- array of frequencies
    ms -- length in milliseconds for notes to play
    """

    for n in notes:
        play_note_by_frequency(n, ms)

def play_note_by_frequency(note_f, ms):
    """Play one note for ms milliseconds by directly passing its frequency in Hz

    Arguments:
    note_f -- frequency of note in Hz
    ms -- length in milliseconds for note to play
    """
    play_wave(sine_wave(note_f, sampling), ms)

def play_all_scales_for_all_roots():
    """Plays scales of the type specified by scale_signature based on all root notes

    Arguments: none
    """
    for name, info in scale_info.items():
        print(f'\n** {name} scales **')
        for note_name, note_freq in basic_notes.items():
            print(f'|_{note_name} {name} scale..')
            scale, scale_notation = construct_scale(note_name, info['signature'], 2)
            play_scale(scale, 300)
        pygame.time.delay(200)

def play_all_scales_for_one_root(root):
    """Plays scales of the type specified by scale_signature based on one root note

    Arguments:
    root -- name of root note
    """
    for name, info in scale_info.items():
        print(f'|_{root} {name} scale..')
        scale, scale_notation = construct_scale(root, info['signature'], 2)
        play_scale(scale, 300)
        pygame.time.delay(200)

def play_one_scale_for_all_roots(scale_name):
    """Plays a specific scale type for all root notes

    Arguments:
    scale_name -- name of scale type to play
    """
    for root, note_freq in basic_notes.items():
        print(f'|_Playing {root} {scale_name} scale..')
        scale, scale_notation = construct_scale(root, scale_info[scale_name]['signature'], 2)
        play_scale(scale, 300)
        pygame.time.delay(200)

def play_one_chord_for_all_roots(chord_name):
    """Plays a specific chord type for all root notes

    Arguments:
    chord_name -- name of chord type to play
    """
    for root, note_freq in basic_notes.items():
        print(f'|_Playing {root} {chord_name} chord..')
        scale, scale_notation = construct_scale(root, scale_info['Major']['signature'], 2, 9)
        chord = construct_chord(chord_info[chord_name]['signature'], scale)
        play_chord(chord, chord_info[chord_name]['signature'], scale)
        pygame.time.delay(200)

def get_modal_scale(scale, scale_notation, mode):
    """Return the scale after applying a musical mode to it

    Arguments:
    scale -- scale(list of notes) to transform
    mode -- int representing mode value as in mode_info dict
    """
    return scale[mode-1:], scale_notation[mode-1:]

def play_scale(scale, ms, with_reverse=True):
    """Plays a scale

    Arguments:
    scale -- array of notes
    ms -- length in milliseconds for each note
    with_reverse -- Plays scale both forward and backwards
    """

    if with_reverse:
        # Extend scale by the reverse scale
        reverse_scale = scale[::-1]
        scale.extend(reverse_scale[1:]) # drop the first element to nicely play the reverse part
    play_piece(scale, ms)

def play_all_chords_for_all_roots():
    """Plays chords of the type specified by chord_signature based on all root notes

    Arguments: none
    """
    for name, info in chord_info.items():
        print(f'\n** {name} chords **')
        for note_name, note_freq in basic_notes.items():
            scale, scale_notation = construct_scale(note_name, scale_info['Major']['signature'], 2, 9)
            chord = construct_chord(info['signature'], scale)
            print(f'|_{name} {note_name} chord..')
            play_chord(chord, info['signature'], scale)
            pygame.time.delay(200)

def play_all_chords_for_one_root(root):
    """Plays chords of the type specified by chord_signature based on one root note

    Arguments:
    root -- root note name
    """
    for name, info in chord_info.items():
        scale, scale_notation = construct_scale(root, scale_info['Major']['signature'], 2, 9)
        chord = construct_chord(info['signature'], scale)
        print(f'|_{name} {root} chord..')
        play_chord(chord, info['signature'], scale)
        pygame.time.delay(200)

def play_note_by_name(note_name, ms, octave):
    """Play one note for ms milliseconds by passing note name

    Arguments:
    note_name -- note name as in C, C#, D..etc
    ms -- length in milliseconds for note to play
    octave -- octave at which to play the note
    """
    f = basic_notes[note_name]
    play_wave(sine_wave(octave*f, sampling), ms)

def construct_and_play_scale(root, octave, scale_name, mode_name, ms = 200):
    """Constructs a scale and Plays it forward and backward

    Arguments:
    root -- name of the root note (C, D ..etc or 'all')
    scale_name -- name of the scale to play. 'all' to play all scales
    octave -- octave at which to play the scale
    ms -- length in milliseconds for each note
    mode_name -- name of the musical mode mode as defined in the mode_info dict, in which to play the chord (Ionian, Dorian..etc)
    """
    print(f'\nPlaying [{scale_name}] scale(s) with [{root}] as root note(s) in the [{mode_name}] mode')
    if 'all' not in (root, scale_name):
        # Play specific scale at specific root
        scale, scale_notation = construct_scale(root, scale_info[scale_name]['signature'], octave, len(scale_info[scale_name]['signature']) + mode_info[mode_name] - 1)
        modal_scale, modal_notation = get_modal_scale(scale, scale_notation, mode_info[mode_name])
        print(modal_notation)
        play_scale(modal_scale, ms)
    elif root == 'all' and scale_name !='all':
        # Play specific scale at all roots
        play_one_scale_for_all_roots(scale_name)
    elif root != 'all' and scale_name =='all':
        # Play all scales for a specific root
        play_all_scales_for_one_root(root)
    else:
        # Play all scales at all roots -- very long
        play_all_scales_for_all_roots()

def construct_and_play_chord(root, octave, chord_name):
    """Constructs a chord and Plays it

    Arguments:
    root -- name of the root note (C, D ..etc or 'all')
    chord_name -- name of the chord to play. 'all' to play all chords
    octave -- octave at which to play the chord
    """
    print(f'\nPlaying [{chord_name}] chord(s) with [{root}] as root note(s)')
    if 'all' not in (root, chord_name):
        base_scale, scale_notation = construct_scale(root, scale_info['Major']['signature'], octave, 9)
        chord = construct_chord(chord_info[chord_name]['signature'], base_scale)
        play_chord(chord, chord_info[chord_name]['signature'], base_scale)
    elif root == 'all' and chord_name !='all':
        # Play specific chord at all roots
        play_one_chord_for_all_roots(chord_name)
    elif root != 'all' and chord_name =='all':
        # Play all chords for a specific root
        play_all_chords_for_one_root(root)
    else:
        # Play all chords at all roots -- very long
        play_all_chords_for_all_roots()

def octave_coverter(octave):
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

def list_values():
    print('## Supported notes (-n options)')
    for n in basic_notes.keys():
        print('|_',n)
    print('\n## Supported scales (-s options)')
    for s in list(scale_info.keys()):
        print('|_',s)
    print('\n## Supported chords (-c options)')
    for c in list(chord_info.keys()):
        print('|_',c)
    print('\n## Supported modes (-m options)')
    for m in list(mode_info.keys()):
        print('|_',m)

def main():
    init()

    parser = argparse.ArgumentParser(description='music-theory.py: A script to interactively play scales and chords')
    root_choices = list(basic_notes.keys())
    root_choices.extend(['all'])
    chord_choices = list(chord_info.keys())
    chord_choices.extend(['all'])
    scale_choices = list(scale_info.keys())
    scale_choices.extend(['all'])

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-c','--chord', choices=chord_choices, help=f'Specify the chord type', metavar = '')
    group.add_argument('-s','--scale', choices=scale_choices, help='Specify the scale type', metavar = '')
    group.add_argument('-n','--note', choices=root_choices, help='Specify the note to play', metavar = '')
    group.add_argument('-l','--list', help='List available scales, chords and notes', action ='store_true')

    parser.add_argument('-o','--octave', choices=[i for i in range(3, 7)], help='Octave settings. Octave 4 is where A = 440Hz', default = 4, type = int, metavar = '')
    parser.add_argument('-r','--root', choices=root_choices ,help='Root note name', default = 'C', metavar = '')
    parser.add_argument('-m','--mode', choices=mode_info ,help='Mode to play scale in', default = 'Ionian', metavar = '')

    args = vars(parser.parse_args())
    octave_multiplier = octave_coverter(args['octave'])
    if args['scale']:
        construct_and_play_scale(args['root'], octave_multiplier, args['scale'], args['mode'])
    elif args['chord']:
        construct_and_play_chord(args['root'], octave_multiplier, args['chord'])
    elif args['note']:
        play_note_by_name(args['note'], 200, octave_multiplier)
    elif args['list']:
        list_values()
    #test_run()

def test_run():
    """Plays all defined scales and chords with all basic_note roots"""

    print('Playing all C scales..')
    play_all_scales_for_one_root('C')
    print('Playing all C chords..')
    play_all_chords_for_one_root('C')
    #play_all_scales_for_all_roots()
    #play_all_chords_for_all_roots()


if __name__ == '__main__':
    main()
else:
    init()
