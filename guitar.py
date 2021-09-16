import mt_toolbox as mt
FRET_COUNT = 24
GUITAR_STRING_NAMES = ['E', 'B', 'G', 'D', 'A', 'E'] # Ordered from 1st to 6th

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

# Empty fretboard
fret_board = construct_fret_board([])
print(fret_board)

# Full fretboard
fret_board = construct_fret_board()
print(fret_board)
# G major chord positions only
base_scale, base_scale_notation = mt.construct_scale('G', mt.all_scale_info['Major']['signature'], octave=4)
_, chord = mt.construct_chord(mt.all_chord_info['Major_triad']['signature'], base_scale, base_scale_notation)
chord_fret_board = construct_fret_board(chord)
print(chord_fret_board)
