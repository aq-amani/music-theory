import time
import sys
from mt_toolbox import header, print_note_info, piano_keys
from music_theory_lab import note_processor, scale_command_processor, chord_command_processor

def sensei_print(s, play_flag=False, wait_flag=True):
    for c in s:
        sys.stdout.write(c)
        sys.stdout.flush()
        time.sleep(0.04)
    if wait_flag:
        input("\n[Press any key to play the sample...]" if play_flag else "\n[Press any key to continue...]")

def main():
    sensei_print(
    """
    Hello there! I'll explain to you some music theory concepts in the simplest way.
    You can freely experiment with all the concepts explained here and more
    by using the main music_theory_lab.py script.

    This explanation will cover the following concepts:
    - Notes
    - Octaves
    - Scales
    - Chords
    """
    )

    sensei_print(
    """
    First let us start with the nature of sound.
    As you already know from grade school,
    sound is the way our brains perceive vibrations that travel through air or any other medium.

    These vibrations can be represented as waves of certain frequencies.

    The simplest form of sound can be created using a single sine wave.
    Here is how a single sine wave of 261.6 Hz frequency sounds like..
    """
    , play_flag=True)
    # Play C note
    note_processor('C', 4)
    time.sleep(1)

    sensei_print(
    """
    That single sine wave you just listened to, is also called a [Musical note].
    261.6 Hz coresponds to the *Do* sound in the 'Do Re Mi' sequence we all know.
    It is also called 'C' in musical notation.

    Every different frequency gives a different sound.
    Increasing the frequency of the note (wave) will produce a sharper higher pitched sound,
    while decreasing it will produce a deeper lower pitched sound.

    See how the *Do* sound (261.6 Hz wave) compares to a 329.6 Hz wave (*Mi* sound) and a 440 Hz wave (*La* sound).
    Do is 'C', Mi is 'E' and La is 'A' in musical notation.
    """
    , play_flag=True)
    # play note C -o4 and E-o4 and A -o4
    note_processor('C', 4)
    time.sleep(1)
    note_processor('E', 4)
    time.sleep(1)
    note_processor('A', 4)
    time.sleep(1)
    sensei_print(
    """
    I will replace the word *wave* with [note] instead hereafter.

    Doubling the frequency of a note will produce a sound that our brain perceives as similar but of a higher pitch.
    Such notes have the same name but exist on different [octave]s.

    See how 261.6 Hz (*Do* we listened to before) compares to the doubled frequency note (261.6 x 2 = 523.2 Hz).
    This new note is also a *Do*, but on a different HIGHER [octave].
    """
    , play_flag=True)
    # play note C -o4 and C-o5
    note_processor('C', 4)
    time.sleep(1)
    note_processor('C', 5)
    time.sleep(1)

    sensei_print(
    """
    Similarily, we get the same note but on a different LOWER [octave] if we divide the note frequency by 2.
    """
    , play_flag=True)
    note_processor('C', 4)
    time.sleep(1)
    note_processor('C', 3)
    time.sleep(1)

    sensei_print(
    """
    People historically tried to divide the frequencies
    between notes and their next octave counterpart in many different ways.
    Some division systems assumed equal spacing between notes, while others did not.

    The most common system is one that divides the interval
    between a note and its octave counterpart into [12] logarithmically equal intervals.
    That is, each note frequency is equal to the previous note frequency multiplied by 2^(1/12).
    """
    )
    sensei_print(
    """
    This 2^(1/12) ratio between consecutive frequencies is called a [Half step] or a [Semi-tone].
    Two half steps/ semi-tones make a [Whole step] or a [Full Tone].

    Each note on these intervals is given a human-friendly name, an alphabet between A~F,
    instead of just frequency values to refer to these notes.

    Here are the basic 12 notes that have names, along with their frequencies on the 4th octave.
    """
    )
    print_note_info(octave = 4)
    sensei_print('')

    sensei_print(
    """
    And here is how these notes exist on one [octave] of a piano keyboard
    """
    )
    print(piano_keys)
    sensei_print('')

    sensei_print(
    """
    Notice the '#' marking of some notes.
    This '#' means that the note is increased by a half step, and is called a sharp.
    Similarily, 'b' is also used in naming notes.
    This 'b' means that the note is decreased by a half step and is called a flat.

    Therefore C# is called [C sharp], and means a C with a frequency increase by half a step (C frequency * 2^(1/12)).
    On the other hand Cb is called [C flat], and means a C with a frequency decrease by half a step (C frequency / 2^(1/12)).
    """
    )

    sensei_print(
    """
    Looking at the 12 note list, you will notice that some notes can have two names.
    For example, G# can also be called Ab, because it is half a step lower than A.
    """
    )

    sensei_print(
    """
    Now you know what notes, octaves and steps are, let us move to musical [scales].

    A scale is a sequence of notes, where note frequencies follow a certain relationship (ratios) between each other.
    The Do Re Mi sequence we all know is actually one type of scales. It is called the [Major scale].
    Listen to and examine the notes on the familiar Major scale.
    """
    , play_flag=True)
    scale_command_processor('C', 'Major', 4, 'Ionian')
    time.sleep(1)

    sensei_print(
    """
    Our familiar major scale starts with the C note,
    and its frequencies follow the pattern outlined in the Scale signature field.
    T refers to a Tone (Full step) while S is for Semitone (Half step) as explained before.
    """
    )
    # scale pattern

    sensei_print(
    """
    In fact, any scale that follows this pattern is called a Major scale, regardless of the note where it starts.
    Therefore scales are defined by the [scale type], Major scale in our example, and the note where it starts from.
    The starting note is called a [root].

    A scale type is defined by ratio sequence of its note frequencies and the number of notes in it.
    A major scale has 7 notes.

    Here is an A Major scale as another example.
    The note frequency ratios follow a major scale pattern,
    and its root note is A (starts from A), hence the [A Major scale] naming.
    """
    , play_flag=True)
    # Play A major scale
    scale_command_processor('A', 'Major', 4, 'Ionian')
    time.sleep(1)

    sensei_print(
    """
    There are many other types of scales, each with its own pattern or frequency ratio sequence.
    The Minor scale, the Pentatonic scale and the Blues scale are some examples of other scale types.

    You can use the main script music_theory_lab.py to experiment more with how the different scales sound with different root notes.
    For now, listen to how the different scales sound with a C root note.
    """
    , play_flag=True)
    scale_command_processor('C', 'all', 4, 'Ionian')
    sensei_print('')
    sensei_print(
    """
    Now let us move on to [chords].

    A chord is simply, multiple notes played together simultaneously.
    The first note in a chord is also called a root note.

    As in scales, notes in a [chord] also need to follow
    certain frequency ratio rules to sound good together.

    To ensure notes follow such frequency ratio rules,
    we always pick up notes from a certain scale that we use as the [base scale] for our chord construction.
    """
    )

    sensei_print(
    """
    For example, one type of chords is constructed
    by taking the 1st, the 3rd and the 5th notes **with reference to the major scale of the same root**.
    Such chords that follow this 1,3,5 position rule, are called a [Major chords].

    If we choose the C note as the root note, then we will get a [C Major chord].
    """
    , play_flag=True)
    chord_command_processor('C', 'Major_triad', 4)
    time.sleep(1)

    sensei_print("""
    Major chords give a 'Happy' impression.

    Let's follow another chord rule. Let's use these positions instead: 1,b3,5 ('b' means flattened note in that position).
    If we flatten the 3rd position note, we get a new chord called a [Minor chord].
    Flattening the 3rd position in our C chord example gives an Eb (E flat).
    This is equivalent to a D# if you look back again at the 12 note chart.

    This is how the resulting [C Minor chord] sounds like.
    """
    , play_flag=True)
    chord_command_processor('C', 'Minor_triad', 4)
    time.sleep(1)

    sensei_print(
    """
    As you have noticed, Minor chords give a 'Sad' impression.

    You can use the main script to experiment with how the different chords sound with different root notes.
    For now, listen to how the different chord types sound with a C root note.
    """
    , play_flag=True)
    chord_command_processor('C', 'all', 4)

    sensei_print(
    """
    This is the end of explanation for this version of this script. I hope it was useful for you!
    Thank you for following the explanation :)
    """
    ,wait_flag=False)
    print('\n')

if __name__ == '__main__':
    print(header)
    main()
else:
    main()
