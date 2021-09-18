# About this repository
This repository currently has two main scripts:

#### 1. guitar.py
A script to print a guitar fretboard showing notes, chords and scales on the strings.

#### 2. music_theory_lab.py
A script to experiment around with music theory concepts while playing actual sounds.

If you have no idea what notes, octaves, chords or scales mean, I highly recommend you run the tutorial mode (sensei mode) as explained in the usage examples below.

## :warning: Caution

If you want to play with the underlying wave frequency settings by manually editing the script, please **be careful not to damage your ears (or your speakers)** by extreme frequencies and high volumes.

As a general rule, please make sure the volume is low when experimenting around.

## :hammer_and_wrench: Setup/ Preparation
```bash
pipenv install --ignore-pipfile --python 3.7
pipenv shell
```

## :rocket: Usage examples: music_theory_lab.py
#### :mortar_board: Tutorial mode (sensei mode)
If you want to grasp music theory concepts in less than 5 minutes, then this command is for you.
```bash
python -u music_theory_lab.py --tutorial
```
#### :musical_note: Play a simple note
Example: C at 4th octave
```bash
python -u music_theory_lab.py --note C --octave 4
```
#### :musical_keyboard: Play a specific scale with a specific root note
Example: C Major scale at 4th octave
```bash
python -u music_theory_lab.py --root C --scale Major -octave 4
```
Example: C Major scale in the Lydian mode
```bash
python -u music_theory_lab.py --root C --scale Major --mode Lydian
```
#### :notes: Play a specific chord with a specific root note
Example: C Major chord at 4th octave
```bash
python -u music_theory_lab.py --root C --chord Major_triad --octave 4
```
:information_source: Check the help output (-h option) for a full list of options, flags and setting values.
```bash
python -u music_theory_lab.py --help
```
## :rocket: Usage examples: guitar.py
Make sure your CLI screen is zoomed out enough to print a 24 fret guitar fretboard.

#### :musical_score: Print all the note names on the fret board
```bash
python guitar.py --all
```
#### :musical_keyboard: Print all the note positions for the C Major scale on the fret board
```bash
python guitar.py --scale Major --root C
```
#### :notes: Print all the note positions for the C Major chord on the fret board
```bash
python guitar.py --chord Major_triad --root C
```

## :white_heart: Acknowledgements
Self teaching myself music theory (still learning though) would not have been possible without the excellent content on https://yourguitaracademy.com/courses

I'd like to thank the "your guitaracademy" team for making such high quality content available for free.
