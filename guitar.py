import mt_toolbox as mt
import matplotlib.pyplot as plt
from note import Note, basic_notes
import numpy as np
import argparse

## Reference lists
# colors of small circles representing notes
NOTE_COLORS = ['firebrick', 'saddlebrown', 'orange', 'darkkhaki', 'yellow', 'limegreen', 'darkolivegreen', 'dodgerblue', 'slategrey', 'slateblue', 'darkviolet', 'indigo']
# list of chromatic intervals
INTERVAL_LIST = ['1', 'm2', '2', 'm3', '3', 'P4', 'A4', 'P5', 'm6', '6', 'm7', '7']
# list of chromatic note names
CHROMATIC_NOTE_NAMES = list(mt.basic_notes.keys())

## Guitar parameters
FRET_COUNT = 24
STRING_COUNT = 6
GUITAR_STRING_NAMES = [Note('E', 4), Note('B', 3), Note('G', 3), Note('D', 3), Note('A', 2), Note('E', 2)] # Ordered from 1st to 6th
# Fretboard numPy array to contain note names (or interval names)
FRETBOARD_NP = np.empty((STRING_COUNT, FRET_COUNT+1), dtype='U10')
# label notes with interval names instead of note names
INTERVAL_LABELS = False

def generate_fret_notes(open_string_note):
    """Returns a list of notes existing along a string at all fret positions

    Arguments:
    open_string_notes -- note object representing the note of a string
    """
    fret_notes = open_string_note.get_consecutive_notes(FRET_COUNT+1)
    return [n.name for n in fret_notes]

def generate_all_notes():
    """Populates FRETBOARD_NP with note names
    """
    global FRETBOARD_NP
    # Populate the array with note names
    for i, n in enumerate(GUITAR_STRING_NAMES):
        FRETBOARD_NP[i, :] = generate_fret_notes(n)

def show_notes(notenames):
    """Shows the notes existing in the notenames list on a guitar fretboard

    Arguments:
    notenames -- list of note names to show
    """

    for i, n in enumerate(notenames):
        pos_y, pos_x = np.where(FRETBOARD_NP == n)
        pos_y += 1 # string count starts from 1
        color = NOTE_COLORS[CHROMATIC_NOTE_NAMES.index(n)]
        label = INTERVAL_LIST[CHROMATIC_NOTE_NAMES.index(n)] if INTERVAL_LABELS else n
        for x, y in zip(pos_x, pos_y):
            ax.scatter(x, y, s=0.5**2 * 1000, facecolor=color, edgecolor=color, zorder=2, clip_on=False)
            ax.text(x, y, label, color='black', fontsize=10, va='center', ha='center', weight='bold')




# Create a figure and axis with a dark background color
fig, ax = plt.subplots(figsize=(16, 8))
fig.patch.set_facecolor('#1e1e1e')  # Dark background color
fig.canvas.manager.set_window_title('Guitar fretboard')
# Set the limits for the plot
ax.set_xlim(0, FRET_COUNT + 1)
ax.set_ylim(STRING_COUNT + 0.5, 0.5)  # Reverse the Y-axis limits

# Draw the frets as horizontal lines with a color close to the fretboard color
for fret in range(1, FRET_COUNT + 1):
    ax.axvline(fret, color='#4d4d4d', linestyle='-', linewidth=2)  # Dark gray color

# Draw the strings with different thicknesses
string_color = '#808080'  # Gray color
string_thicknesses = [1, 1.5, 1.5, 2, 2, 3]  # Thicknesses for each string
for string, thickness in zip(range(1, STRING_COUNT + 1), string_thicknesses):
    ax.axhline(string, color=string_color, linestyle='-', linewidth=thickness)

# Label the axes
ax.set_xlabel('Frets', color='white')  # White text color
ax.set_ylabel('Strings', color='white')  # White text color

# Set the aspect ratio to be equal
ax.set_aspect('equal')

# Set the ticks to represent the fret numbers and string numbers
# Reverse the Y-axis ticks to reflect the string order on a guitar
ax.set_xticks(range(1, FRET_COUNT + 1))
ax.set_yticks(range(STRING_COUNT, 0, -1))

# Set the color of the axes ticks
ax.tick_params(axis='x', colors='white')
ax.tick_params(axis='y', colors='white', pad=10)

# Remove ticks on the top and right sides of the plot
ax.tick_params(right=False, top=False)

# Set the background color of the plot
ax.set_facecolor('#8B4513')  # Dark background color

# Draw filled circles (inlays) at specific fret positions
inlay_frets = [3, 5, 7, 9, 15, 17, 19, 21]
inlay_radius = 0.25  # Radius of the inlay circles
inlay_color = 'grey'  # Color of the inlay circles
inlay_positions = [(fret-0.5, 3.5) for fret in inlay_frets]  # Example positions for inlays
inlay_positions = inlay_positions + [(12,2),(12,5),(24,2),(24,5)]
ax.scatter(*zip(*inlay_positions), color=inlay_color, s=inlay_radius**2 * 1000, edgecolor='black', linewidth=1)
generate_all_notes()

def parse_arguments():
    parser = argparse.ArgumentParser(description='guitar.py: A script to show scale/chord/note positions on the guitar fret board')
    root_choices = list(mt.basic_notes.keys())
    root_choices.extend(note_info['alt_name'] for note_info in mt.basic_notes.values() if note_info['alt_name'])
    chord_choices = list(mt.all_chord_info.keys())
    scale_choices = list(mt.all_scale_info.keys())
    mode_choices= list(mt.mode_info)

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-c','--chord', choices=chord_choices, help=f'Specify the chord type to show', metavar = '')
    group.add_argument('-s','--scale', choices=scale_choices, help='Specify the scale to show', metavar = '')
    group.add_argument('-n','--note', choices=root_choices, help='Specify the note to show', metavar = '')
    group.add_argument('-a','--all', help='Show all notes', action ='store_true')

    parser.add_argument('-r','--root', choices=root_choices ,help='Root note name', default='C', metavar = '')
    parser.add_argument('-m','--mode', choices=mode_choices ,help='Mode to play scale in', default = 'Ionian', metavar = '')

    args = vars(parser.parse_args())
    return args, parser

def command_processor(args, parser):
    global CHROMATIC_NOTE_NAMES

    if args['mode'] != list(mt.mode_info)[0] and not args['scale']:
        parser.error("**Modes other than the default Ionian are only supported for scale commands**")

    root_pos = CHROMATIC_NOTE_NAMES.index(args['root'])
    CHROMATIC_NOTE_NAMES = CHROMATIC_NOTE_NAMES[root_pos:]+CHROMATIC_NOTE_NAMES[:root_pos]
    if args['scale']:
        scale_notes = mt.construct_scale(args['root'], args['scale'], args['mode'], 4)
        notes = [n.name for n in scale_notes]
        title = f"{args['root']} {args['mode']} of the {args['scale']} scale" if args['mode'] != 'Ionian' else f"{args['root']} {args['scale']} scale"
    elif args['chord']:
        chord_notes = mt.construct_chord(args['root'], args['chord'], 4)
        notes = [n.name for n in chord_notes]
        title = f"{args['root']} {args['chord']} chord"
    elif args['note']:
        notes = args['note']
        title = f"{args['note']} note positions"
    elif args['all']:
        # Full fretboard
        notes = CHROMATIC_NOTE_NAMES
        title = "All note positions"

    return notes, title

def main():
    args, parser = parse_arguments()
    notes, title = command_processor(args, parser)
    show_notes(notes)
    # Display the plot
    plt.title(title, color='white')  # White text color for the title
    plt.show()


if __name__ == '__main__':
    main()
