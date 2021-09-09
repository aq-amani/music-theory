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

Those vibrations can be represented as waves of certain frequencies.
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

note_exp3 = """
To distinguish notes in a human-friendly way,
notes were given names using english letters from A to F.
Here are the basic notes that have names, along with their frequencies.
The frequency ratio between each of these notes is 2^12. This ratio is called a [Half step] or a [Semi-tone].
Two half steps make a [Whole step] or a [Full Tone].
"""

octave_exp = """
Doubling the frequency of a note will produce a sound that our brain perceives as similar but of a higher pitch.
Such notes have the same name but exist on a higher [octave].
See how XXHz and ZZHz sound like.
"""

sensei_print(intro)
sensei_print(note_exp1)
#play_note()
sensei_print(note_exp2)
#play_note_compare()
sensei_print(note_exp3)
sensei_print(octave_exp)

