import pygame, pygame.sndarray
import numpy
import scipy.signal
import re

sample_rate = 44100
sampling = 4096    # or 16384

S = 2**(1/12) # Semi-tone frequency multiplier
T = S ** 2 # Full-tone frequency multiplier

major_scale_signature = [T,T,S,T,T,T,S]
minor_scale_signature = [T,S,T,T,S,T,T]
diminished_scale_signature = [T,S,T,S,T,S,T]
augmented_scale_signature = [T*S,S,T*S,S,T*S,S,T*S]
maj_pentatonic_scale_signature = [T,T,T*S,T,T*S]
min_pentatonic_scale_signature = [T*S,T,T,T*S,T]
blues_scale_signature = [T*S,T,S,S,T*S,T]
## Major, minor, dim, aug Triads are all 1,3,5 respective to their own scale.
##And are 1,3,5 / 1,b3,5 / 1,b3,b5 / 1,3,#5 respective to the major scale.

major_chord_signature = [1,3,5] # Happy
basic_triad_signature = [1,3,5]
minor_chord_signature = [1,'b3',5] # Sad / (b) for flat
diminished_chord_signature = [1,'b3','b5'] # Sad with drama
augmented_chord_signature = [1,3,'5#'] # Strange as if moving to another dimension / (#) for sharp
sus2_chord_signature = [1,2,5] # Suspended 2
sus4_chord_signature = [1,4,5] # Suspended 4
# 7ths chords (4 note chords)
maj7_chord_signature = [1,3,5,7] # Major 7th
min7_chord_signature = [1,'b3',5,'b7'] # minor 7th
dom7_chord_signature = [1,3,5,'b7'] # Dominant 7th
# Diminished chords / Kind of Jazzy feeling
half_dim_chord_signature = [1,'b3','b5','b7'] # AKA minor 7th flat 5 (m7b5)
whole_dim_chord_signature = [1,'b3','b5',6] # AKA diminished 7th.
#Last index of diminished 7th usually expressed as 'bb7' but this script doesn't support double flats yet. 'bb7' is 6 on a major scale.

# 9ths chords (5 note chords) / 5 can be ommited without much sound difference
maj9_chord_signature = [1,3,5,7,9] # Major 9th
min9_chord_signature = [1,'b3',5,'b7',9] # minor 9th
dom9_chord_signature = [1,3,5,'b7',9] # Dominant 9th

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

def construct_chord(root, chord_signature, base_scale):
    """Construct a wave from a combination of simultaneous notes(chord)

    Arguments:
    root -- root note of the chord
    chord_signature -- indexes of notes within the base scale
    base_scale -- reference scale from where notes are picked up to form chords
    """
    chord = 0
    for index in chord_signature:
        note = note_modifier(index, base_scale)
        chord = sum([chord, sine_wave(note, sampling)])
    return chord

def note_modifier(note_index, base_scale):
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
        play_note(n, ms)

def play_note(note, ms):
    """Play one note for ms milliseconds. A note is a frequency in Hz

    Arguments:
    note -- frequency of note in Hz
    ms -- length in milliseconds for note to play
    """
    play_wave(sine_wave(note, sampling), ms)

def play_all_scales(name, scale_signature):
    print(f'Playing all {name} scales')
    for note_name, note_freq in basic_notes.items():
        print(f'{note_name} {name} scale..')
        scale = construct_scale(note_freq, scale_signature, 2)
        play_scale(scale, 300)
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

def play_all_chords(name, chord_signature):
    print(f'Playing all {name} triad chords')
    for note_name, note_freq in basic_notes.items():
        scale = construct_scale(note_freq, major_scale_signature, 2, 9)
        chord = construct_chord(note_freq, chord_signature, scale)
        print(f'{name} {note_name} chord..')
        play_chord(chord, chord_signature, scale)
        pygame.time.delay(200)

def init():
    """Code to initialize pygame"""
    ##pygame 1.9.4
    #pygame.mixer.pre_init(sample_rate, -16, 1) # 44.1kHz, 16-bit signed, mono
    #pygame.init()

    ##pygame 1.9.6/win7
    pygame.mixer.init(sample_rate, -16, 1) # 44.1kHz, 16-bit signed, mono

def main():
    init()

    #scale = construct_scale(basic_notes["G"], major_scale_signature, 2)
    #play_piece(scale, 500)

    #chord = construct_chord(basic_notes["G"], sus4_chord_signature, scale)
    #play_chord(chord, sus4_chord_signature, scale)

    test_run()

def test_run():
    """Plays all defined scales and chords with all basic_note roots"""

    print('Playing all scales..')
    play_all_scales('Major', major_scale_signature)
    play_all_scales('minor', minor_scale_signature)
    play_all_scales('Diminished', diminished_scale_signature)
    play_all_scales('Augmented', augmented_scale_signature)
    play_all_scales('Maj Pentatonic', maj_pentatonic_scale_signature)
    play_all_scales('Min Pentatonic', min_pentatonic_scale_signature)
    play_all_scales('Blues', blues_scale_signature)

    print('Playing all chords..')
    play_all_chords('Major', major_chord_signature)
    play_all_chords('minor', minor_chord_signature)
    play_all_chords('Diminished', diminished_chord_signature)
    play_all_chords('Augmented', augmented_chord_signature)
    play_all_chords('Sus2', sus2_chord_signature)
    play_all_chords('Sus4', sus4_chord_signature)
    play_all_chords('Maj 7th', maj7_chord_signature)
    play_all_chords('min 7th', min7_chord_signature)
    play_all_chords('Dominant 7th', dom7_chord_signature)
    play_all_chords('Half diminished', half_dim_chord_signature)
    play_all_chords('Whole diminished', whole_dim_chord_signature)
    play_all_chords('Maj 9th', maj9_chord_signature)
    play_all_chords('min 9th', min9_chord_signature)
    play_all_chords('Dominant 9th', dom9_chord_signature)

if __name__ == '__main__':
    main()
