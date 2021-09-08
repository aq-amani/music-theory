import time
import sys

def sensei_print(s):
    for c in s:
        sys.stdout.write(c)
        sys.stdout.flush()
        time.sleep(0.050)
    input("[Press any key to continue...]")

intro = """
Hello. I'll explain to you some music theory concepts in the simplest way.
The explanation will cover the following concepts:
- Notes
- Octaves
- Scales
- Chords
"""

note_exp1 = """
First let us start with the nature of sound.
As you already know from grade school,
sound is the way our brains perceive vibrations that travel through air or any other medium.

These vibrations can be represented as waves of certain frequencies.
The simplest form of sound can be created using a single sine wave.
Here is how a single sine wave of XXHz frequency sounds like..
"""
note_exp2 = """
That single sine wave you just listened to, is also called a [Musical note].
Every different frequency gives a different sound.
Increasing the frequency of the note (wave) will produce a sharper higher pitched sound,
while decreasing it will produce a deeper lower pitched sound.
See how XXHz wave/note compares to YYHz and ZZHz waves/notes.

I will replace the word wave with [note] instead hereafter.
"""

octave_exp = """
Doubling the frequency of a note will produce a sound that our brain perceives as similar but of a higher pitch.
Such notes have the same name but exist on different [octave]s.
See how XXHz and ZZHz sound like.
"""

octave_exp2 = """
People historically tried to divide the frequencies between notes and their next octave counterpart in many different ways.
Some division systems assumed equal spacing between notes, while others did not.
The most common system is one that divides the interval between a note and its octave counter part into [12] logarithmically equal intervals.
That is, each note frequency is equal to the previous note frequency multiplied by 2^(1/12).

This 2^(1/12) ratio between consecutive frequencies is called a [Half step] or a [Semi-tone].
Two half steps/ semi-tones make a [Whole step] or a [Full Tone].

Each note on these intervals is given a human-friendly name, an alphabet between A~F, instead of just a frequency values to refer to these notes.
Here are the basic notes that have names, along with their frequencies.
"""




sensei_print(intro)
sensei_print(note_exp1)
#play_note()
sensei_print(note_exp2)
#play_note_compare()
sensei_print(octave_exp)
sensei_print(octave_exp2)
