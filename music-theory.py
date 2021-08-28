import pygame, pygame.sndarray
import numpy
import scipy.signal
import re

sample_rate = 44100
sampling = 4096    # or 16384

S = 2**(1/12) # Semi-tone frequency multiplier
T = S ** 2 # Full-tone frequency multiplier
SCALE_LENGTH = 7 # standard one octave scale length
#SCALE_LENGTH = 5
major_scale_signature = [T,T,S,T,T,T,S]
minor_scale_signature = [T,S,T,T,S,T,T]
diminished_scale_signature = [T,S,T,S,T,S,T]
augmented_scale_signature = [T*S,S,T*S,S,T*S,S,T*S]
maj_pentatonic_scale_signature = [T,T,T*S,T,T*S]
## Major, minor, dim, aug Triads are all 1,3,5 respective to their own scale.
##And are 1,3,5 / 1,b3,5 / 1,b3,b5 / 1,3,#5 respective to the major scale.

major_chord_signature = [1,3,5]
basic_triad_signature = [1,3,5]
minor_chord_signature = [1,'b3',5] # (b) for flat
diminished_chord_signature = [1,'b3','b5']
augmented_chord_signature = [1,3,'5#'] # (#) for sharp
sus2_chord_signature = [1,2,5]
sus4_chord_signature = [1,4,5]

major_scale = []

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

def construct_scale(root, scale_signature, octave):
    """Construct a musical scale from a root note

    Arguments:
    root -- root note of the scale
    scale_signature -- array of frequency ratios between consecutive notes on the scale
    octave -- octave with which to construct the scale with. 1 is for frequencies in basic_notes
    """
    note = root * octave
    scale = []
    for i in range(SCALE_LENGTH):
        scale.append(note)
        note *= scale_signature[i % SCALE_LENGTH]
        note = round(note,2)
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
        if type(index) is str:
            i = int(re.findall(r'\d+', index)[0])
            if 'b' in index:
               note = flatten(base_scale[i-1])
               #print (f'{n} is flat {i}')
            elif '#' in index:
               note = sharpen(base_scale[i-1])
               #print (f'{n} is sharp {i}')
        else:
            note = base_scale[index-1]
        chord = sum([chord, sine_wave(note, sampling)])
    return chord

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
        if type(index) is str:
            i = int(re.findall(r'\d+', index)[0])
            if 'b' in index:
               note = flatten(base_scale[i-1])
               #print (f'{n} is flat {i}')
            elif '#' in index:
               note = sharpen(base_scale[i-1])
               #print (f'{n} is sharp {i}')
        else:
            note = base_scale[index-1]
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

def init():
    """Code to initialize pygame"""
    ##pygame 1.9.4
    #pygame.mixer.pre_init(sample_rate, -16, 1) # 44.1kHz, 16-bit signed, mono
    #pygame.init()

    ##pygame 1.9.6/win7
    pygame.mixer.init(sample_rate, -16, 1) # 44.1kHz, 16-bit signed, mono

def main():
    init()

    scale = construct_scale(basic_notes["D"], diminished_scale_signature, 1)
    play_piece(scale, 500)

    chord = construct_chord(basic_notes["D"], major_chord_signature, scale)
    play_chord(chord, major_chord_signature, scale)


if __name__ == '__main__':
    main()
