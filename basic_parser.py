import argparse
import mt_toolbox as mt

def basic_parser(script_description):
    """Parser for common arguments used in all scripts
    Arguments:
    script_description -- Description of the script to use in the help message
    """
    parser = argparse.ArgumentParser(description=script_description)
    root_choices = list(mt.basic_notes.keys())
    root_choices.extend(note_info['alt_name'] for note_info in mt.basic_notes.values() if note_info['alt_name'])
    root_choices.extend(['all'])
    chord_choices = list(mt.all_chord_info.keys())
    chord_choices.extend(['all'])
    scale_choices = list(mt.all_scale_info.keys())
    scale_choices.extend(['all'])
    key_choices = list(mt.basic_notes.keys()) + [n+'m' for n in mt.basic_notes.keys()]
    mode_choices= list(mt.mode_info).extend(['all'])

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-c','--chord', choices=chord_choices, help=f'Specify the chord type', metavar = '')
    group.add_argument('-s','--scale', choices=scale_choices, help='Specify the scale type', metavar = '')
    group.add_argument('-n','--note', choices=root_choices, help='Specify the note to play', metavar = '')
    group.add_argument('-l','--list', help='List available scales, chords and notes', action ='store_true')

    parser.add_argument('-r','--root', choices=root_choices ,help='Root note name', default = 'C', metavar = '')
    parser.add_argument('-m','--mode', choices=mode_choices ,help='Mode to play scale in', default = 'Ionian', metavar = '')

    return parser, group
