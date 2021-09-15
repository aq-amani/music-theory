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

def print_fret_board():
    fret_nums = '_'.join(f'__{str(i):^2}__' for i in range(0,FRET_COUNT+1))
    note_names = ''
    lower_edge = ''
    for index, open_string in enumerate(GUITAR_STRING_NAMES):
        note_names += f'{str(index + 1):<2}'
        note_names += '|'.join(f'_ {n:^2} _' for n in generate_fret_note_names(open_string))
        note_names += '\n'
    for j in range(0,FRET_COUNT+1):
        lower_edge += '='.join(f'={"O=":^2}=' if j in (3,5,7,9,15,17,19,21) else f'={"OO":^2}=' if j in (12,24) else f'={"==":^2}=')
    print(
    f'__{fret_nums}',
    f'\n{note_names}=={lower_edge}')

print_fret_board()
