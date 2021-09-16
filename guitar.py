import mt_toolbox as mt
FRET_COUNT = 24
GUITAR_STRING_NAMES = ['E', 'B', 'G', 'D', 'A', 'E'] # Ordered from 1st to 6th
import argparse

def generate_fret_note_names(open_string_name):
    fret_names = [open_string_name]
    note_names = list(mt.basic_notes.keys())
    note_index = note_names.index(open_string_name)
    for i in range(1,FRET_COUNT+1):
        note_index += 1
        fret_names.append(note_names[note_index%len(note_names)])
    return fret_names

def construct_fret_board(notes = 'all'):
    fret_nums = '_'.join(f'__{str(i):^2}__' for i in range(0,FRET_COUNT+1))
    note_names = ''
    lower_edge = ''
    for index, open_string in enumerate(GUITAR_STRING_NAMES):
        note_names += f'{str(index + 1):<2}  {open_string:<2} ||' if open_string in notes or notes == 'all' else f'{str(index + 1):<2}  {"  ":<2} ||'
        note_names += '|'.join(f'_ {n:^2} _' if n in notes or notes == 'all' else f'__{"__":^2}__' for n in generate_fret_note_names(open_string)[1:])
        note_names += '\n'
    for j in range(0,FRET_COUNT+1):
        lower_edge += '='.join(f'={"O=":^2}=' if j in (3,5,7,9,15,17,19,21) else f'={"OO":^2}=' if j in (12,24) else f'={"==":^2}=')

    fret_board =f'__{fret_nums}\n{note_names}=={lower_edge}'
    return fret_board

def main():
    parser = argparse.ArgumentParser(description='guitar.py: A script to show chord/note positions on the guitar fret board')
    root_choices = list(mt.basic_notes.keys())
    chord_choices = list(mt.all_chord_info.keys())
    scale_choices = list(mt.all_scale_info.keys())

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-c','--chord', choices=chord_choices, help=f'Specify the chord type to show', metavar = '')
    group.add_argument('-s','--scale', choices=scale_choices, help='Specify the scale to show', metavar = '')
    group.add_argument('-n','--note', choices=root_choices, help='Specify the note to show', metavar = '')
    group.add_argument('-a','--all', help='Show all notes', action ='store_true')

    parser.add_argument('-r','--root', choices=root_choices ,help='Root note name', metavar = '')

    args = vars(parser.parse_args())

    if args['scale']:
        #TODO: Implement
        pass
    elif args['chord']:
        base_scale, base_scale_notation = mt.construct_scale(args['root'], mt.all_scale_info['Major']['signature'], octave=4)
        _, chord = mt.construct_chord(mt.all_chord_info[args['chord']]['signature'], base_scale, base_scale_notation)
        chord_fret_board = construct_fret_board(chord)
        print(chord_fret_board)
    elif args['note']:
        note_fret_board = construct_fret_board(args['note'])
        print(note_fret_board)
    elif args['all']:
        # Full fretboard
        fret_board = construct_fret_board()
        print(fret_board)

if __name__ == '__main__':
    main()
