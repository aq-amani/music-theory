import mt_toolbox as mt
import argparse
import playback as pb
import pygame.time
import threading
VIEW = None
GRAPHICAL = False
SAVE_PNG = False
def scale_command_processor(root_name, scale_name, octave, mode_name, ms = 200):
    """Plays single or multiple scales depending on the input

    Arguments:
    root_name -- name of the root note (C, D ..etc or 'all')
    scale_name -- name of the scale to play. 'all' to play all scales
    octave -- octave at which to play the scale
    mode_name -- name of the musical mode mode as defined in the mode_info dict, in which to play the chord (Ionian, Dorian..etc)
    ms -- length in milliseconds for each note
    """
    print(f'\nPlaying [{scale_name}] scale(s) with [{root_name}] as root note(s) in the [{mode_name}] mode')
    pb.REVERSE_SCALE = True
    if 'all' not in (root_name, scale_name, mode_name):
        # Play specific scale at specific root
        if GRAPHICAL:
            graphical_construct_and_play_scale(root_name, scale_name, mode_name, octave)
        else:
            construct_and_play_scale(root_name, scale_name, mode_name, octave)
    if root_name == 'all':
        # Play specific scale at all roots
        if GRAPHICAL:
            for root_name in mt.basic_notes.keys():
                graphical_construct_and_play_scale(root_name, scale_name, mode_name, octave, single_run=False)
        else:
            for root_name in mt.basic_notes.keys():
                construct_and_play_scale(root_name, scale_name, mode_name, octave, single_run=False)
    if scale_name =='all':
        # Play all scales for a specific root
        if GRAPHICAL:
            for scale_name in mt.all_scale_info.keys():
                graphical_construct_and_play_scale(root_name, scale_name, mode_name, octave, single_run=False)
        else:
            for scale_name in mt.all_scale_info.keys():
                construct_and_play_scale(root_name, scale_name, mode_name, octave, single_run=False)
    if mode_name =='all':
        # Play all modes for a specific scale
        base_scale_notes = mt.construct_scale(root_name, scale_name, 'Ionian', octave)
        if len(base_scale_notes)-1 != 7: #-1 for minus the last octave note
            raise ValueError("Error: Modes not supported for non-heptatonic scales")
        if GRAPHICAL:
            for m, n in zip(mt.mode_info, base_scale_notes):
                graphical_construct_and_play_scale(n.name, scale_name, m, octave, single_run=False)
        else:
            for m, n in zip(mt.mode_info, base_scale_notes):
                construct_and_play_scale(n.name, scale_name, m, octave, single_run=False)
    ## Deprecate this case
    #else:
    #    # Play all scales at all roots -- very long
    #    for scale_name in all_scale_info.keys():
    #        print(f'\n** {scale_name} scales **')
    #        for root_name in basic_notes.keys():
    #            construct_and_play_scale(root_name, scale_name, mode_name, octave, single_run=False)

def construct_and_play_chord(root_name, chord_name, octave, single_run=True):
    chord_notes = mt.construct_chord(root_name, chord_name, octave)
    mt.print_chord(root_name, chord_name, chord_notes)
    pb.play_chord(chord_notes)
    if not single_run:
        pygame.time.delay(200)
def construct_and_play_scale(root_name, scale_name, mode_name, octave, single_run=True):
        # logic
        scale_notes = mt.construct_scale(root_name, scale_name, mode_name, octave)
        # view
        mt.print_scale(root_name, scale_name, scale_notes, mode_name)
        # playback
        pb.play_scale(scale_notes, ms=300)
        if not single_run:
            pygame.time.delay(200)

def graphical_construct_and_play_scale(root_name, scale_name, mode_name, octave, single_run=True):
        # logic
        scale_notes = mt.construct_scale(root_name, scale_name, mode_name, octave)
        animation_frame_interval = (VIEW.animation_frame_interval)/1000 # to seconds from milliseconds
        # playback
        ## Play notes only if non save png mode
        if not SAVE_PNG:
            pb.create_midi(scale_notes, 'scale', t = animation_frame_interval)
            thread = threading.Thread(target=pb.play_midi_file, args=(pb.midi_filename,))
            thread.start()
        # view
        if mode_name != 'Ionian':
            object_name_label = f'{root_name} {mode_name} of\n{scale_name}\nscale'
        else:
            object_name_label = f'{root_name}\n{scale_name}\nscale'
        VIEW.setup_parameters(scale_notes, root_name, object_name_label)
        if SAVE_PNG:
            img_name = f'{root_name}_{mode_name}_{scale_name}_scale.png'
            VIEW.save_plot_image(img_name)
        else:
            VIEW.animate_plot(pause_length=animation_frame_interval*len(scale_notes)+1, single_run=single_run)

def graphical_construct_and_play_chord(root_name, chord_name, octave, arp=True, single_run=True):
        # logic
        chord_notes = mt.construct_chord(root_name, chord_name, octave)
        animation_frame_interval = (VIEW.animation_frame_interval)/1000 # to seconds from milliseconds
        # playback
        ## play notes only if non save png mode
        if not SAVE_PNG:
            if arp:
                pb.create_arp_chord_midi(chord_notes, t = animation_frame_interval)
            else:
                pb.create_midi(chord_notes, 'c')
            thread = threading.Thread(target=pb.play_midi_file, args=(pb.midi_filename,))
            thread.start()
        # view
        object_name_label = f'{root_name}\n{chord_name}\nchord'
        VIEW.setup_parameters(chord_notes, root_name, object_name_label)
        if SAVE_PNG:
            img_name = f'{root_name}_{chord_name}_chord.png'
            VIEW.save_plot_image(img_name)
        else:
            VIEW.animate_plot(pause_length=animation_frame_interval+1 if not arp else (animation_frame_interval*len(chord_notes)+1)+1, single_run=single_run)

def progression_command_processor(key, progression, octave):
    """Plays a chord progression

    Arguments:
    key -- Key in which to play the progression (C, Dm ..etc)
    progression -- list of integers(1~7) representing the degree of each chord within the key
    octave -- octave
    """
    chord_list, type_list, octave_list = mt.get_chord_list_from_progression(key, progression, octave)
    if GRAPHICAL:
        for r, t, o in zip(chord_list, type_list, octave_list):
            graphical_construct_and_play_chord(root_name=r, chord_name=t, octave=o, arp=False, single_run=False)
    else:
        for r, t, o in zip(chord_list, type_list, octave_list):
            chord_command_processor(root_name=r, chord_name=t, octave=o, arp=False)

def chord_command_processor(root_name, chord_name, octave, arp=True):
    """Plays a single or multiple chords depending on input

    Arguments:
    root_name -- name of the root note (C, D ..etc or 'all')
    chord_name -- name of the chord to play. 'all' to play all chords
    octave -- octave at which to play the chord
    """
    print(f'\nPlaying [{chord_name}] chord(s) with [{root_name}] as root note(s)')
    pb.ARPEGGIATE = arp
    if 'all' not in (root_name, chord_name):
        if GRAPHICAL:
            graphical_construct_and_play_chord(root_name, chord_name, octave, arp=True, single_run=True)
        else:
            construct_and_play_chord(root_name, chord_name, octave)
    if root_name == 'all':
        # Play specific chord at all roots
        if GRAPHICAL:
            for root_name in mt.basic_notes.keys():
                graphical_construct_and_play_chord(root_name, chord_name, octave, arp=True, single_run=False)
        else:
            for root_name in mt.basic_notes.keys():
                construct_and_play_chord(root_name, chord_name, octave, single_run=False)
    if chord_name == 'all':
        # Play all chords for a specific root
        if GRAPHICAL:
            for chord_name in mt.all_chord_info.keys():
                graphical_construct_and_play_chord(root_name, chord_name, octave, arp=True, single_run=False)
        else:
            for chord_name in mt.all_chord_info.keys():
                construct_and_play_chord(root_name, chord_name, octave, single_run=False)
    ## Deprecate this case
    #else:
    #    # Play all chords at all roots -- very long
    #    for chord_name in all_chord_info.keys():
    #        print(f'\n** {chord_name} chords **')
    #        for root_name in basic_notes.keys():
    #            construct_and_play_chord(root_name, chord_name, octave, single_run=False)

def note_processor(note_name, octave):
    """Plays a single note

    Arguments:
    note_name -- name of the note (C, D, F# ..etc )
    octave -- octave at which to play the note
    """
    note = mt.Note(note_name, octave)
    print(f'\n|_Playing {mt.note_alt_name_appender(note.name)} note in octave {note.octave} | Frequency: {note.frequency} Hz\n')
    pb.play_note(note, 700)

def command_processor(args, parser):
    """Main command processor

    Arguments:
    args -- flags and input passed to the script
    """
    global VIEW, GRAPHICAL, SAVE_PNG
    print(mt.header)
    if(args['keyboard']):
        print(mt.piano_keys)
    all_count = sum(1 for var in (args['scale'], args['chord'], args['root'], args['mode']) if var == 'all')
    if all_count > 1:
        parser.error("Error: Can't specify 'all' for more than one option")
    if args['graphics']:
        import chord_visualizer
        VIEW = chord_visualizer
        GRAPHICAL = True
        VIEW.ANIMATE =args['animate']
        SAVE_PNG = args['output']
        pb.MIDI = True
    if(args['midi']):
        pb.MIDI = True
    if args['mode'] != list(mt.mode_info)[0] and not args['scale']:
        parser.error("**Modes other than the default Ionian are only supported for scale commands**")
    if args['scale']:
        scale_command_processor(args['root'], args['scale'], args['octave'], args['mode'])
    elif args['chord']:
        chord_command_processor(args['root'], args['chord'], args['octave'])
    elif args['note']:
        mt.print_note_info(args['octave'])
        note_processor(args['note'], args['octave'])
    elif args['list']:
        list_supported_values()
    elif args['progression']:
        progression_command_processor(args['key'], args['progression'], args['octave'])
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

def parse_arguments():
    parser = argparse.ArgumentParser(description='music_theory_lab.py: A script to interactively play with music theory concepts')
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
    group.add_argument('-t','--tutorial', help='Run the tutorial (sensei) mode!', action ='store_true')
    group.add_argument('-p','--progression', nargs='+', help='Chord progression in terms of degrees separated by space. Ex.: 1 4 1 5', metavar = '')

    parser.add_argument('-o','--octave', choices=[i for i in range(0, 9)], help='Octave settings. Octave 4 is where A = 440Hz', default = 4, type = int, metavar = '')
    parser.add_argument('-r','--root', choices=root_choices ,help='Root note name', default = 'C', metavar = '')
    parser.add_argument('-m','--mode', choices=mode_choices ,help='Mode to play scale in', default = 'Ionian', metavar = '')
    parser.add_argument('-b','--keyboard', help='Show a reference piano keyboard', action ='store_true')
    parser.add_argument('-d','--midi', help='Use the midiutil instead to play notes', action ='store_true')
    parser.add_argument('-k','--key', choices=key_choices ,help='Key name. Example C(C major) or Am(A minor)', default = 'C', metavar = '')
    # options unique to the graphical backend
    parser.add_argument('-g','--graphics', help='To use the matplotlib as the graphics backend instead of console print out', action ='store_true')
    parser.add_argument('-v','--output', help='Save as png image', action ='store_true')
    parser.add_argument('-a','--animate', help='animate notes to show them one by one', action ='store_true')

    args = vars(parser.parse_args())
    return args, parser

def main():
    args, parser = parse_arguments()
    command_processor(args, parser)


if __name__ == '__main__':
    main()
