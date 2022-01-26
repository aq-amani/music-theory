from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame, pygame.sndarray
import numpy
import scipy.signal
from note import Note

##MIDI stuff
from midiutil import MIDIFile
track    = 0
channel  = 0
duration = 8   # In beats
tempo    = 400  # In BPM
volume   = 100 # 0-127, as per the MIDI standard
instrument = 0 #27 guitar

midi_filename = "out.mid"
MIDI = False # Plays as wave if false and using midiutil if True
##

sample_rate = 44100
sampling = 4096    # or 16384
##
ARPEGGIATE = False # Whether to arpeggiate chords or not
REVERSE_SCALE = False # Whether to play scales in reverse as well
## Waves
#########
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
    """Play an array of note frequencies ms milliseconds each

    Arguments:
    notes -- array of Note objects
    ms -- length in milliseconds for notes to play
    """

    for n in notes:
        play_note(n, ms)

## Notes
#########
def play_note(note, ms):
    """Play one note for ms milliseconds by passing note name

    Arguments:
    note -- Note object
    ms -- length in milliseconds for note to play
    """
    if MIDI:
        create_midi([note], 'note')
        play_midi_file(midi_filename)
    else:
        play_wave(sine_wave(note.frequency, sampling), ms)

## Chords
#########
def play_chord(chord_notes):
    """Play a combination of notes simultaneously (chord)

    Arguments:
    chord_notes -- List of Note objects respresenting the chord
    arpegiate -- whether to also play the chord note by note
    """
    chord_wave = 0
    for note in chord_notes:
        chord_wave = sum([chord_wave, sine_wave(note.frequency, sampling)])

    print('Chord is now being played..')
    if MIDI:
        create_midi(chord_notes, 'chord')
        play_midi_file(midi_filename)
    else:
        play_wave(chord_wave, 700)
    pygame.time.delay(100)

    if ARPEGGIATE:
        print('Single notes of the chord are now being played separately..')
        if MIDI:
            create_midi(chord_notes, 'scale', ms = 3)
            play_midi_file(midi_filename)
        else:
            for note in chord_notes:
                play_wave(sine_wave(note.frequency, sampling), 500)
        pygame.time.delay(100)
        print('Chord is now being played again..')
        if MIDI:
            create_midi(chord_notes, 'chord')
            play_midi_file(midi_filename)
        else:
            play_wave(chord_wave, 700)

## Scales
#########
def play_scale(scale_notes, ms):
    """Plays a scale

    Arguments:
    scale_notes -- A list of Note objects of which the scale to play is made
    ms -- length in milliseconds for each note
    with_reverse -- Plays scale both forward and backwards
    """
    print('Scale is now being played forward..')
    if MIDI:
        create_midi(scale_notes, 'scale')
        play_midi_file(midi_filename)
    else:
        play_piece(scale_notes, ms)

    if REVERSE_SCALE:
        # Extend scale by the reverse scale
        reverse_scale = scale_notes[::-1]
        scale_notes.extend(reverse_scale[1:]) # drop the first element to nicely play the reverse part
        pygame.time.delay(200)
        print('Scale is now being played forward and then backwards..')
        if MIDI:
            create_midi(scale_notes, 'scale')
            play_midi_file(midi_filename)
        else:
            play_piece(scale_notes, ms)

## MIDI files
#############
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

def init():
    """Code to initialize pygame"""
    ##pygame 1.9.6
    pygame.mixer.init(sample_rate, -16, 1) # 44.1kHz, 16-bit signed, mono
    # optional volume 0 to 1.0
    #pygame.mixer.music.set_volume(0.8)

if __name__ == '__main__':
    print('module for music playback functions')
else:
    init()
