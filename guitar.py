import mt_toolbox as mt
from note import Note
import argparse

FRET_COUNT = 24
GUITAR_STRING_NAMES = [Note('E', 4), Note('B', 3), Note('G', 3), Note('D', 3), Note('A', 2), Note('E', 2)] # Ordered from 1st to 6th

def generate_fret_notes(open_string_note):
    fret_notes = open_string_note.get_consecutive_notes(FRET_COUNT+1)
    return fret_notes

def construct_fret_board(notes = 'all'):
    fret_nums = '_'.join(f'__{str(i):^3}__' for i in range(0,FRET_COUNT+1))
    note_names = ''
    lower_edge = ''
    chord_note_names = [note.name for note in notes] if notes != 'all' else 'all'
    for index, open_string_note in enumerate(GUITAR_STRING_NAMES):
        note_names += f'{str(index + 1):<2}  {open_string_note.name:<2}{open_string_note.octave:<1} ||' if notes == 'all' or open_string_note.name in chord_note_names else f'{str(index + 1):<2}  {"  ":<3} ||'
        note_names += '|'.join(f'_ {n.name:^2}{n.octave:^1} _' if notes == 'all' or n.name in chord_note_names else f'__{"___":^3}__' for n in generate_fret_notes(open_string_note)[1:])
        note_names += '\n'

    lower_edge += '='.join(f'=={"=●=":^3}==' if j in (3,5,7,9,15,17,19,21) else f'=={"●●=":^3}==' if j in (12,24) else f'=={"===":^3}==' for j in range(0,FRET_COUNT+1))

    fret_board =f'__{fret_nums}\n{note_names}=={lower_edge}'
    return fret_board

def main():
    parser = argparse.ArgumentParser(description='guitar.py: A script to show chord/note positions on the guitar fret board')
    root_choices = list(mt.basic_notes.keys())
    root_choices.extend(note_info['alt_name'] for note_info in mt.basic_notes.values() if note_info['alt_name'])
    chord_choices = list(mt.all_chord_info.keys())
    scale_choices = list(mt.all_scale_info.keys())

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-c','--chord', choices=chord_choices, help=f'Specify the chord type to show', metavar = '')
    group.add_argument('-s','--scale', choices=scale_choices, help='Specify the scale to show', metavar = '')
    group.add_argument('-n','--note', choices=root_choices, help='Specify the note to show', metavar = '')
    group.add_argument('-a','--all', help='Show all notes', action ='store_true')

    parser.add_argument('-r','--root', choices=root_choices ,help='Root note name', metavar = '')
    #parser.add_argument('-o','--octave', choices=[i for i in range(2, 7)], help='Octave settings. Octave 4 is where A = 440Hz', default = 4, type = int, metavar = '')
    octave = 4 # Printing frets is not limited to a specific octave. This value is provided anyway because it is necessary in underlying functions

    args = vars(parser.parse_args())

    if args['scale']:
        scale_notes = mt.construct_scale(Note(args['root'], octave), mt.all_scale_info[args['scale']]['signature'])
        scale_fret_board = construct_fret_board(scale_notes)
        print(scale_fret_board)
    elif args['chord']:
        base_scale_notes = mt.construct_scale(Note(args['root'], octave), mt.all_scale_info['Major']['signature'])
        chord_notes = mt.construct_chord(mt.all_chord_info[args['chord']]['signature'], base_scale_notes)
        chord_fret_board = construct_fret_board(chord_notes)
        print(chord_fret_board)
    elif args['note']:
        note_fret_board = construct_fret_board([Note(args['note'], octave)])
        print(note_fret_board)
    elif args['all']:
        # Full fretboard
        fret_board = construct_fret_board()
        print(fret_board)

if __name__ == '__main__':
    main()
