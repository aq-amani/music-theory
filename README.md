# music_theory.py
A script to play around with music theory concepts.

## :warning: Caution

If you want to play with the underlying wave frequency settings by manually editing the script, please **be careful not to damage your ears (or your speakers)** by extreme frequencies and high volumes.

As a general rule, please make sure the volume is low when experimenting around.

## 🛠️ Setup/ Preparation
```bash
pipenv install --ignore-pipfile --python 3.7
pipenv shell
```

## 🚀 Usage examples
#### :musical_note: Play a simple note
Example: C at 4th octave
```bash
python -u music_theory.py --note C --octave 4
```
#### :musical_keyboard: Play a specific scale with a specific root note
Example: C Major scale at 4th octave
```bash
python -u music_theory.py --root C --scale Major -octave 4
```
#### :notes: Play a specific chord with a specific root note
Example: C Major chord at 4th octave
```bash
python -u music_theory.py --root C --chord Major_triad --octave 4
```
️:information_source: Check the help output for a full list of options, flags and setting values.
