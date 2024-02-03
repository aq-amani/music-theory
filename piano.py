import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
import mt_toolbox as mt
import math
from basic_parser import basic_parser
## Reference lists
# colors of small circles representing notes
NOTE_COLORS = ['firebrick', 'saddlebrown', 'orange', 'darkkhaki', 'yellow', 'limegreen', 'darkolivegreen', 'dodgerblue', 'slategrey', 'slateblue', 'darkviolet', 'indigo']
# list of chromatic intervals
INTERVAL_LIST = mt.INTERVAL_LIST
# list of rectangles representing piano keys
KEYS = []
# Positions in the middle of each key to draw dots representing notes
CHROMATIC_NOTE_POSITIONS = []
# piano keyboard settings
octave_count = 2 # how many octaves to show
keyboard_size = 7*octave_count #in white keys count
keyboard_height = 2
# list of chromatic note names
CHROMATIC_NOTE_NAMES = list(mt.basic_notes.keys()) * octave_count
# for note dot positions
white_note_y = 0.3
black_note_y = 1
# key width settings
black_key_width = 0.6
white_key_width = 1
# Height of the black keys from the origin
black_key_y = 0.67

# Create a figure and axis
fig, ax = plt.subplots()
fig.patch.set_facecolor('#001F3F')

# Set ticks on X/Y axis
ax.set_xticks(np.linspace(0, keyboard_size, keyboard_size+1))
ax.set_yticks(np.linspace(0, keyboard_height, 3))
# Hide both axes
ax.set_axis_off()

def build_keyboard():
    global KEYS, CHROMATIC_NOTE_POSITIONS
    for n in range(0,keyboard_size):
        # white keys
        white_rectangle = Rectangle((n, 0), white_key_width, keyboard_height, edgecolor='black', facecolor='darkgrey', zorder=-1)
        ax.add_patch(white_rectangle)
        KEYS.append(white_rectangle)
        CHROMATIC_NOTE_POSITIONS.append(((n+1)-white_key_width/2, white_note_y))
        # black keys
        if n%7 not in [2,6]:
            bg_rectangle = Rectangle((n+1-black_key_width/2, black_key_y), black_key_width, keyboard_height-black_key_y, edgecolor=None, facecolor='white', zorder=0)
            black_rectangle = Rectangle((n+1-black_key_width/2, black_key_y), black_key_width, keyboard_height-black_key_y, edgecolor='black', facecolor='black', zorder=1)
            ax.add_patch(bg_rectangle)
            ax.add_patch(black_rectangle)
            KEYS.append(black_rectangle)
            CHROMATIC_NOTE_POSITIONS.append((n+1, black_note_y))

def show_notes(notes, highlight_key=False):
    for n in notes:
        pos = [i for i, name in enumerate(CHROMATIC_NOTE_NAMES) if name == n]
        for p in pos:
            kb_position = CHROMATIC_NOTE_POSITIONS[p]
            if highlight_key:
                KEYS[p].set_facecolor((1, 0, 0, 0.2))
            ax.scatter(kb_position[0],kb_position[1],s=0.5**2 * 1000, facecolor=NOTE_COLORS[p%12], edgecolor=NOTE_COLORS[p%12], zorder=2, clip_on=False)
            ax.text(kb_position[0],kb_position[1], n, color='black', fontsize=10, va='center', ha='center', weight='bold')



def parse_arguments(parser, group):
    # Add arguments unique to this script
    group.add_argument('-a','--all', help='Show all notes', action ='store_true')

    args = vars(parser.parse_args())
    return args, parser

def command_processor(args, parser):
    global NOTE_COLORS
    global minor_flag

    if args['mode'] != list(mt.mode_info)[0] and not args['scale']:
        parser.error("**Modes other than the default Ionian are only supported for scale commands**")

    root_pos = CHROMATIC_NOTE_NAMES.index(args['root'])
    # rotate color list to the right to match the specified root
    NOTE_COLORS = NOTE_COLORS[-root_pos:] + NOTE_COLORS[:-root_pos]

    if args['scale']:
        scale_notes = mt.construct_scale(args['root'], args['scale'], args['mode'], 4)
        notes = [n.name for n in scale_notes]
        title = f"{args['root']} {args['mode']} of the {args['scale']} scale" if args['mode'] != 'Ionian' else f"{args['root']} {args['scale']} scale"
        if args['scale'] == 'Minor':
            minor_flag = True
    elif args['chord']:
        chord_notes = mt.construct_chord(args['root'], args['chord'], 4)
        notes = [n.name for n in chord_notes]
        title = f"{args['root']} {args['chord']} chord"
    elif args['note']:
        notes = args['note']
        title = f"{args['note']} note positions"
    elif args['all']:
        # Full keyboard
        notes = CHROMATIC_NOTE_NAMES
        title = "All note positions"

    return notes, title

def main():
    build_keyboard()
    parser, group = basic_parser('piano.py: A script to show positions of notes, chords and scales on a graphical piano keyboard')
    args, parser = parse_arguments(parser, group)
    notes, title = command_processor(args, parser)
    show_notes(notes)
    # Display the plot
    plt.title(title, color='white')
    plt.show()


if __name__ == '__main__':
    main()
