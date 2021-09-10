import mt_toolbox as mt
import argparse

def main():

    parser = argparse.ArgumentParser(description='music_theory_lab.py: A script to interactively play with music theory concepts')
    root_choices = list(mt.basic_notes.keys())
    root_choices.extend(note_info['alt_name'] for note_info in mt.basic_notes.values() if note_info['alt_name'])
    root_choices.extend(['all'])
    chord_choices = list(mt.all_chord_info.keys())
    chord_choices.extend(['all'])
    scale_choices = list(mt.all_scale_info.keys())
    scale_choices.extend(['all'])

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-c','--chord', choices=chord_choices, help=f'Specify the chord type', metavar = '')
    group.add_argument('-s','--scale', choices=scale_choices, help='Specify the scale type', metavar = '')
    group.add_argument('-n','--note', choices=root_choices, help='Specify the note to play', metavar = '')
    group.add_argument('-l','--list', help='List available scales, chords and notes', action ='store_true')
    group.add_argument('-t','--tutorial', help='Run the tutorial (sensei) mode!', action ='store_true')

    parser.add_argument('-o','--octave', choices=[i for i in range(3, 7)], help='Octave settings. Octave 4 is where A = 440Hz', default = 4, type = int, metavar = '')
    parser.add_argument('-r','--root', choices=root_choices ,help='Root note name', default = 'C', metavar = '')
    parser.add_argument('-m','--mode', choices=mt.mode_info ,help='Mode to play scale in', default = 'Ionian', metavar = '')
    parser.add_argument('-k','--keyboard', help='Show a reference piano keyboard', action ='store_true')

    print(mt.header)
    args = vars(parser.parse_args())

    if(args['keyboard']):
        print(mt.piano_keys)
    if args['scale']:
        if args['scale'] != scale_choices[0] and args['mode'] != list(mt.mode_info)[0]:
            parser.error("**Scales other than the Major scale do not support modes other than Ionian (default scale as is)**")
        mt.scale_command_processor(args['root'], args['scale'], args['octave'], args['mode'])
    elif args['chord']:
        if args['mode'] != list(mt.mode_info)[0]:
            parser.error("**Modes other than the default Ionian are not supported for chords**")
        mt.chord_command_processor(args['root'], args['chord'], args['octave'])
    elif args['note']:
        if args['mode'] != list(mt.mode_info)[0]:
            parser.error("**Modes other than the default Ionian are not supported for notes**")
        mt.print_note_info(args['octave'])
        mt.play_note_by_name(args['note'], 700, args['octave'])
    elif args['list']:
        mt.list_supported_values()
    elif args['tutorial']:
        import sensei_mode


if __name__ == '__main__':
    main()
