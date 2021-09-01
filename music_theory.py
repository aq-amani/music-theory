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
## TODO: Consider a better way to express scale signatures(something like 0.5, 1 ,1.5 ?)
## TODO: Use classes for scales, chords and notes?(ex.: scales.major, chord.type..etc)
## TODO: Make the script interactive. Create scale? chord?, type? root? octave?..etc

# Scale signatures
scale_signatures = {
    "Major"  : [T,T,S,T,T,T,S],
    "Minor" : [T,S,T,T,S,T,T],
    "Diminished"  : [T,S,T,S,T,S,T],
    "Augmented" : [T*S,S,T*S,S,T*S,S,T*S],
    "Major_pentatonic"  : [T,T,T*S,T,T*S],
    "Minor_pentatonic"  : [T*S,T,T,T*S,T],
    "Blues" : [T*S,T,S,S,T*S,T],
}

# Chord signatures
chord_signatures = {
    "Major_triad" : [1,3,5], # Happy
    "Minor_triad" : [1,'b3',5], # Sad / (b) for flat
    "Diminished" : [1,'b3','b5'], # Sad with drama
    "Augmented" : [1,3,'5#'], # Strange as if moving to another dimension / (#) for sharp
    ## Major, minor, dim, aug Triads are all 1,3,5 respective to their own scale.
    ##And are 1,3,5 / 1,b3,5 / 1,b3,b5 / 1,3,#5 respective to the major scale.
    "Suspended_2" : [1,2,5], # Suspended 2
    "Suspended_4" : [1,4,5], # Suspended 4
    # 7ths chords (4 note chords)
    "Major_7th" : [1,3,5,7], # Major 7th
    "Minor_7th" : [1,'b3',5,'b7'], # minor 7th
    "Dominant_7th" : [1,3,5,'b7'], # Dominant 7th
    # Diminished chords / Kind of Jazzy feeling
    "Half_diminished" : [1,'b3','b5','b7'], # AKA minor 7th flat 5 (m7b5)
    "Whole_diminished" : [1,'b3','b5',6], # AKA diminished 7th.
    #Last index of diminished 7th usually expressed as 'bb7' but this script doesn't support double flats yet. 'bb7' is 6 on a major scale.
    # 9ths chords (5 note chords) / 5 can be ommited without much sound difference
    "Major_9th" : [1,3,5,7,9], # Major 9th
    "Minor_9th" : [1,'b3',5,'b7',9], # minor 9th
    "Dominant_9th" : [1,3,5,'b7',9], # Dominant 9th
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
    root -- root note of the scale
    scale_signature -- array of frequency ratios between consecutive notes on the scale
    octave -- octave with which to construct the scale with. 1 is for frequencies in basic_notes
    scale_length -- Defaults to standard scale length. Specify when needing non-standard scale length (ex.: span multiple octaves)
    """
    note = root * octave
    if not scale_length:
        # If not specified, default to standard scale length
        scale_length = len(scale_signature)
    scale = []
    scale.append(note)
    for i in range(scale_length):
        note *= scale_signature[i % len(scale_signature)]
        note = round(note,2)
        scale.append(note)
    return scale

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
    sound = pygame.sndarray.make_sound(wave.astype(int))
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
    for name, signature in scale_signatures.items():
        print(f'\n** {name} scales **')
        for note_name, note_freq in basic_notes.items():
            print(f'{note_name} {name} scale..')
            scale = construct_scale(note_freq, signature, 2)
            play_scale(scale, 300)
        pygame.time.delay(200)

def play_all_scales_for_one_root(root):
    """Plays scales of the type specified by scale_signature based on one root note

    Arguments:
    root -- name of root note
    """
    for name, signature in scale_signatures.items():
        print(f'{root} {name} scale..')
        scale = construct_scale(basic_notes[root], signature, 2)
        play_scale(scale, 300)
        pygame.time.delay(200)

def play_one_scale_for_all_roots(scale_name):
    """Plays a specific scale type for all root notes

    Arguments:
    scale_name -- name of scale type to play
    """
    for root, note_freq in basic_notes.items():
        print(f'Playing {root} {scale_name} scale..')
        scale = construct_scale(basic_notes[root], scale_signatures[scale_name], 2)
        play_scale(scale, 300)
        pygame.time.delay(200)

def play_one_chord_for_all_roots(chord_name):
    """Plays a specific chord type for all root notes

    Arguments:
    chord_name -- name of chord type to play
    """
    for root, note_freq in basic_notes.items():
        print(f'Playing {root} {chord_name} chord..')
        scale = construct_scale(note_freq, scale_signatures['Major'], 2, 9)
        chord = construct_chord(chord_signatures[chord_name], scale)
        play_chord(chord, chord_signatures[chord_name], scale)
        pygame.time.delay(200)

def play_scale(scale, ms):
    """Play a scale forward and backward

    Arguments:
    scale -- array of notes
    ms -- length in milliseconds for each note
    """
    play_piece(scale, ms)
    reverse_scale = scale[::-1]
    play_piece(reverse_scale[1:], ms) # drop the first element to nicely play the reverse part

def play_all_chords_for_all_roots():
    """Plays chords of the type specified by chord_signature based on all root notes

    Arguments: none
    """
    for name, signature in chord_signatures.items():
        print(f'\n** {name} chords **')
        for note_name, note_freq in basic_notes.items():
            scale = construct_scale(note_freq, scale_signatures['Major'], 2, 9)
            chord = construct_chord(signature, scale)
            print(f'{name} {note_name} chord..')
            play_chord(chord, signature, scale)
            pygame.time.delay(200)

def play_all_chords_for_one_root(root):
    """Plays chords of the type specified by chord_signature based on one root note

    Arguments:
    root -- root note name
    """
    for name, signature in chord_signatures.items():
        scale = construct_scale(basic_notes[root], scale_signatures['Major'], 2, 9)
        chord = construct_chord(signature, scale)
        print(f'{name} {root} chord..')
        play_chord(chord, signature, scale)
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

def construct_and_play_scale(root, octave, scale_name, ms = 200):
    """Constructs a scale and Plays it forward and backward

    Arguments:
    root -- name of the root note (C, D ..etc or 'all')
    scale_name -- name of the scale to play. 'all' to play all scales
    octave -- octave at which to play the scale
    ms -- length in milliseconds for each note
    """
    print(f'\nPlaying [{scale_name}] scale(s) with [{root}] as root note(s)')
    if 'all' not in (root, scale_name):
        # Play specific scale at specific root
        scale = construct_scale(basic_notes[root], scale_signatures[scale_name], octave)
        play_scale(scale, ms)
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
        base_scale = construct_scale(basic_notes[root], scale_signatures['Major'], octave, 9)
        chord = construct_chord(chord_signatures[chord_name], base_scale)
        play_chord(chord, chord_signatures[chord_name], base_scale)
    elif root == 'all' and chord_name !='all':
        # Play specific chord at all roots
        play_one_chord_for_all_roots(chord_name)
    elif root != 'all' and chord_name =='all':
        # Play all chords for a specific root
        play_all_chords_for_one_root(root)
    else:
        # Play all chords at all roots -- very long
        play_all_chords_for_all_roots()

def play_major_with_octave(octave):
    """Constructs and plays C root major scale with the specified octave, for octave preview purposes

    Arguments:
    octave -- octave at which to play the scale
    """
    scale = construct_scale(basic_notes["C"], scale_signatures['Major'], octave)
    play_piece(scale, 200)

def init():
    """Code to initialize pygame"""
    ##pygame 1.9.4
    #pygame.mixer.pre_init(sample_rate, -16, 1) # 44.1kHz, 16-bit signed, mono
    #pygame.init()

    ##pygame 1.9.6/win7
    pygame.mixer.init(sample_rate, -16, 1) # 44.1kHz, 16-bit signed, mono

def main():
    init()

    parser = argparse.ArgumentParser(description='music-theory.py: A script to interactively play scales and chords')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-c','--chord', choices=list(chord_signatures.keys()), help='Specify the chord type')
    group.add_argument('-s','--scale', choices=list(scale_signatures.keys()), help='Specify the scale type')
    parser.add_argument('-o','--octave', choices=[0,1,2,3,4], help='Octave settings', default = 2, type = int)
    parser.add_argument('-r','--root', choices=list(basic_notes.keys()) ,help='Root note name', default = 'C')

    args = vars(parser.parse_args())
    if args['scale']:
        construct_and_play_scale(args['root'], args['octave'], args['scale'])
    else:
        construct_and_play_chord(args['root'], args['octave'], args['chord'])
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
