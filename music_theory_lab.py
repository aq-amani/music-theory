import mt_toolbox as mt
import argparse
import playback as pb

def command_processor(args):
    """Main command processor

    Arguments:
    args -- flags and input passed to the script
    """
    print(mt.header)
    if(args['keyboard']):
        print(mt.piano_keys)
    if(args['midi']):
        pb.MIDI = True
    if args['scale']:
        pb.REVERSE_SCALE = True
        mt.scale_command_processor(args['root'], args['scale'], args['octave'], args['mode'])
    elif args['chord']:
        if args['mode'] != list(mt.mode_info)[0]:
            parser.error("**Modes other than the default Ionian are not supported for chords**")
        pb.ARPEGGIATE = True
        mt.chord_command_processor(args['root'], args['chord'], args['octave'])
    elif args['note']:
        if args['mode'] != list(mt.mode_info)[0]:
            parser.error("**Modes other than the default Ionian are not supported for notes**")
        print_note_info(args['octave'])
        mt.note_processor(args['note'], args['octave'])
    elif args['list']:
        list_supported_values()
    elif args['progression']:
        key = args['key']
        progression = args['progression']
        chord_list, type_list = mt.get_chord_list_from_progression(key, progression)
        for r, t in zip(chord_list, type_list):
            print(r,t)
            mt.chord_command_processor(r, t, 4)
    elif args['tutorial']:
        import sensei_mode

def list_supported_values():
    """Lists available values for the different options"""
    print('## Supported notes (-n options)')
    for n in mt.basic_notes.keys():
        print('|_',n, f'({mt.basic_notes[n]["alt_name"]})' if mt.basic_notes[n]["alt_name"] else '')
    print('\n## Supported scales (-s options)')
    for s in list(mt.all_scale_info.keys()):
        print('|_',s)
    print('\n## Supported chords (-c options)')
    for c in list(mt.all_chord_info.keys()):
        print('|_',c)
    print('\n## Supported musical modes (-m options)')
    for m in list(mt.mode_info.keys()):
        print('|_',m)

    parser = argparse.ArgumentParser(description='music_theory_lab.py: A script to interactively play with music theory concepts')
    root_choices = list(mt.basic_notes.keys())
    root_choices.extend(note_info['alt_name'] for note_info in mt.basic_notes.values() if note_info['alt_name'])
    root_choices.extend(['all'])
    chord_choices = list(mt.all_chord_info.keys())
    chord_choices.extend(['all'])
    scale_choices = list(mt.all_scale_info.keys())
    scale_choices.extend(['all'])
    key_choices = list(mt.basic_notes.keys()) + [n+'m' for n in mt.basic_notes.keys()]

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-c','--chord', choices=chord_choices, help=f'Specify the chord type', metavar = '')
    group.add_argument('-s','--scale', choices=scale_choices, help='Specify the scale type', metavar = '')
    group.add_argument('-n','--note', choices=root_choices, help='Specify the note to play', metavar = '')
    group.add_argument('-l','--list', help='List available scales, chords and notes', action ='store_true')
    group.add_argument('-t','--tutorial', help='Run the tutorial (sensei) mode!', action ='store_true')
    group.add_argument('-p','--progression', nargs='+', help='Chord progression in terms of degrees separated by space. Ex.: 1 4 1 5', metavar = '')

    parser.add_argument('-o','--octave', choices=[i for i in range(0, 9)], help='Octave settings. Octave 4 is where A = 440Hz', default = 4, type = int, metavar = '')
    parser.add_argument('-r','--root', choices=root_choices ,help='Root note name', default = 'C', metavar = '')
    parser.add_argument('-m','--mode', choices=mt.mode_info ,help='Mode to play scale in', default = 'Ionian', metavar = '')
    parser.add_argument('-b','--keyboard', help='Show a reference piano keyboard', action ='store_true')
    parser.add_argument('-d','--midi', help='Use the midiutil instead to play notes', action ='store_true')
    parser.add_argument('-k','--key', choices=key_choices ,help='Key name. Example C(C major) or Am(A minor)', default = 'C', metavar = '')

    args = vars(parser.parse_args())
    mt.command_processor(args)

if __name__ == '__main__':
    main()
