import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
import mt_toolbox as mt
import argparse
import threading
import playback as pb
pb.MIDI = True

# Set up the figure and axis
fig, ax = plt.subplots(figsize=(8, 8), facecolor='gray')
ax.set_xlim(-1.5, 1.5)
ax.set_ylim(-1.5, 1.5)
fig.canvas.manager.set_window_title('Chord visualizer')
# Remove axes
ax.axis('off')

structure_color = 'black'

colors = ['firebrick', 'saddlebrown', 'orange', 'darkkhaki', 'yellow', 'limegreen', 'darkolivegreen', 'dodgerblue', 'slategrey', 'slateblue', 'darkviolet', 'indigo']
interval_list = ['1', 'm2', '2', 'm3', '3', 'P4', 'A4', 'P5', 'm6', '6', 'm7', '7']
chromatic_note_names = [note.name for note in mt.construct_scale(mt.Note('C',4), mt.all_scale_info['Chromatic']['signature'], len(mt.all_scale_info['Chromatic']['signature']))]
rotated_chromatic_note_names = [] # chromatic_note_names but rotated left to start from specified root note
# colors of small circles representing notes
circle_colors = colors
# positions of notes to plot (list indexes) with reference to a chromatic scale(0~11)
positions_to_plot = []
# list of note objects representing notes that construct the required scale or chord
notes_to_plot = []
# degrees on the chromatic "clock"
chromatic_angle_degrees = -1 * np.arange(0, (12+1) * 30, 30) + 450 # get all 12 chromatic angle degrees
rotated_angle_degrees = [] # chromatic_angle_degrees but rotated left to start at the degree of the specfied root note
# text representing the chord/scale name to place on center circle
object_name_label = ''
# ANIMATE flag
ANIMATE = False
# Flag to play resulting notes or not
PLAYNOTES = True
# length and radius values
tick_circle_radius = 1.4
tick_length = 0.05
offset_from_circle_center = 0.3 # for interval labels
circle_radius = 0.2 # note circles radius

# Function to update the plot for each frame of the animation
def update(frame):
    """Function to update the plot for each frame of the animation

    Arguments:
    frame -- current frame number as passed by FuncAnimation
    """

    ax.clear()

    # Set the same figure and axis size for every frame
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)

    # Plot the center circle
    center_circle = plt.Circle((0, 0), 0.3, color=structure_color, zorder=2)
    ax.add_patch(center_circle)

    # Ticks circle at 30-degree intervals
    for i, angle in enumerate(chromatic_angle_degrees[:-1]):
        angle_rad = np.deg2rad(angle)
        x_tick_start = np.cos(angle_rad) * tick_circle_radius
        y_tick_start = np.sin(angle_rad) * tick_circle_radius
        x_tick_end = np.cos(angle_rad) * (tick_circle_radius - tick_length)
        y_tick_end = np.sin(angle_rad) * (tick_circle_radius - tick_length)
        # Labels around the chromatic reference circle (grayed out unless active)
        n_pos_x = np.cos(angle_rad)+np.cos(angle_rad)*(circle_radius+offset_from_circle_center)
        n_pos_y = np.sin(angle_rad)+np.sin(angle_rad)*(circle_radius+offset_from_circle_center)
        external_reference_label = chromatic_note_names[i]
        ax.text(n_pos_x, n_pos_y, external_reference_label, ha='center', va='center', color='dimgray', fontsize=12, weight='bold')

        ax.plot([x_tick_start, x_tick_end], [y_tick_start, y_tick_end], color='dimgray', linewidth=4)
    tick_circle = plt.Circle((0,0), tick_circle_radius, zorder=0, edgecolor='dimgray', lw=4)
    tick_circle.set_facecolor('grey')
    ax.add_patch(tick_circle)

    prev_pos = positions_to_plot[0]
    octave_flag = False
    # Depending on ANIMATE flag, animate notes one by one or just draw them at once in one frame
    positions_loop_list = positions_to_plot[:frame+1] if ANIMATE else positions_to_plot
    for idx, pos in enumerate(positions_loop_list):
        reversed_index = len(positions_to_plot) - pos
        #If the new index is lower, this means we proceeded to the next octave
        # flag is used to add text to the label of notes on next octaves(ex.: 9th is 2+octave)
        if not octave_flag:
            if pos < prev_pos:
                octave_flag = True
            prev_pos = pos
        current_angle = rotated_angle_degrees[pos] % 360
        active_external_label = rotated_chromatic_note_names[pos]

        # Convert angle from degrees to radians
        angle_rad = np.deg2rad(current_angle)

        # Define line coordinates
        x_line = [0, np.cos(angle_rad)]
        y_line = [0, np.sin(angle_rad)]

        # Plot a circle at the end of the line with a fixed color
        circle = plt.Circle((np.cos(angle_rad), np.sin(angle_rad)), circle_radius, zorder=2, edgecolor=structure_color, lw=1)
        circle.set_facecolor(circle_colors[pos])
        ax.add_patch(circle)

        # Plot the line
        ax.plot(x_line, y_line, color=structure_color, lw=10, zorder=1)
        n_pos_x = np.cos(angle_rad)+np.cos(angle_rad)*(circle_radius+offset_from_circle_center)
        n_pos_y = np.sin(angle_rad)+np.sin(angle_rad)*(circle_radius+offset_from_circle_center)
        ax.text(n_pos_x, n_pos_y, active_external_label, ha='center', va='center', color='black', fontsize=12, weight='bold')

        # Labels at circle centers
        note_circle_label = interval_list[pos]+'\n+Octave' if octave_flag else interval_list[pos]
        pos_x = np.cos(angle_rad)
        pos_y = np.sin(angle_rad)
        ax.text(pos_x, pos_y, note_circle_label, ha='center', va='center', color='black', fontsize=10, weight='bold')

    # Text for object name
    ax.text(0, 0, object_name_label, ha='center', va='center', color='white', fontsize=10, weight='bold')
    # Set aspect ratio to equal
    ax.set_aspect('equal')

    # Remove axes
    ax.axis('off')
    return ax

def calculate_parameters(type, root, name, mode, arp):
    """Returns num_lines necessary to create the plot and populates the necessary global lists

    Arguments:
    type -- 's' or 'c' for scale or chord
    root -- root note (if specified)
    name -- scale or chord name
    mode -- the mode of the scale
    arp  -- whether to arpeggiate a chord or not
    """
    global positions_to_plot
    global notes_to_plot
    global object_name_label
    global rotated_chromatic_note_names, rotated_angle_degrees
    root_pos = chromatic_note_names.index(root) if root else 0
    rotated_chromatic_note_names = chromatic_note_names[root_pos:]+chromatic_note_names[:root_pos]
    #rotate excluding the last wrap back angle
    rotated_angle_degrees = np.concatenate((chromatic_angle_degrees[root_pos:-1], chromatic_angle_degrees[:root_pos]))
    # include the first angle to wrap back to the first note
    rotated_angle_degrees = np.append(rotated_angle_degrees, rotated_angle_degrees[0])

    if type == 's':
        if mode != 'Ionian':
            signature = mt.get_modal_scale_signature(mt.all_scale_info[name]['signature'], mt.mode_info[mode])
            object_name_label = name+f'\n{mode} scale'
        else:
            signature = mt.all_scale_info[name]['signature']
            object_name_label = name+'\nscale'
        positions_to_plot = mt.tone_to_chrom_positions(signature)
        if root:
            notes_to_plot= mt.construct_scale(mt.Note(root,4), signature, len(signature)+1)
            root_pos = chromatic_note_names.index(notes_to_plot[0].name)
            rotated_chromatic_note_names = chromatic_note_names[root_pos:]+chromatic_note_names[:root_pos]
            if PLAYNOTES:
                pb.create_midi(notes_to_plot, 'scale', t = 2.05)
                thread = threading.Thread(target=pb.play_midi_file, args=(pb.midi_filename,))
                thread.start()
    elif type == 'c':
        positions_to_plot = mt.intervals_to_chrom_positions(mt.all_chord_info[name]['signature'])
        object_name_label = name+'\nchord'
        if root:
            scale = mt.construct_scale(mt.Note(root,4), mt.all_scale_info['Major']['signature'], 9)
            notes_to_plot= mt.construct_chord(mt.all_chord_info[name]['signature'], scale)
            if PLAYNOTES:
                if arp:
                    pb.create_arp_chord_midi(notes_to_plot, t = 2.05)
                else:
                    pb.create_midi(notes_to_plot, 'c', t = 1)
                thread = threading.Thread(target=pb.play_midi_file, args=(pb.midi_filename,))
                thread.start()
    num_lines = len(positions_to_plot)
    return num_lines

def animate_or_save_image(scale, chord, root, mode, save_png, arp=True, single=True):
    """Animate the chord/scale or save an image of the plot

    Arguments:
    scale -- scale name
    chord -- chord name
    root -- root note name
    mode -- the mode of the scale
    save_png -- boolean. Saves an image if True, displayes the plot if False
    arp  -- bool. whether to arpeggiate a chord or not
    """
    num_lines = calculate_parameters('s' if scale else 'c', root, scale if scale else chord, mode, arp)
    if save_png:
        update(num_lines - 1)
        img_name = f'{root}_{mode}_{scale}_scale.png' if scale else f'{root}_{chord}_chord.png'
        plt.savefig(img_name)
    else:
        animation = FuncAnimation(fig, update, frames=num_lines if ANIMATE else 1, interval=300, blit=False, repeat=False)
        if single:
            plt.show()
        else:
            # Remove axes
            ax.axis('off')
            plt.show(block=False)
            # Adjust delay between consecutive plots/playbacks
            # non arpeggiated chords finish faster
            pause_length = 1.2 if chord and not arp else 4
            plt.pause(pause_length)

def process_command(args):
    """Main switch for the script arguments

    Arguments:
    args -- arguments as returned by parse_arguments()
    """

    global PLAYNOTES
    global ANIMATE
    # Ensure no more than one variable has the 'all' value, if any
    all_count = sum(1 for var in (args['scale'], args['chord'], args['root'], args['mode']) if var == 'all')
    if all_count > 1:
        raise ValueError("Error: Can't specify 'all' for more than one option")
    ANIMATE = args['animate']
    PLAYNOTES= not args['output']
    # Chord progression
    if args['progression']:
        key = args['key']
        chord_root_list, type_list = mt.get_chord_list_from_progression(key, args['progression'])
        for r, t in zip(chord_root_list, type_list):
            animate_or_save_image(scale=args['scale'], chord=t, root=r, mode=args['mode'], save_png=args['output'], arp=False, single=False)
    # Specific scale or chord and a specific root note
    elif 'all' not in (args['scale'], args['chord'], args['root'], args['mode']):
        animate_or_save_image(args['scale'], args['chord'], args['root'], args['mode'], args['output'])
    # All chords, all scales or all notes
    elif args['mode'] != 'all':
        loop_list = mt.all_scale_info.keys() if args['scale'] else (mt.all_chord_info.keys() if args['chord'] else chromatic_note_names)
        if args['scale'] == 'all':
            for s in mt.all_scale_info.keys():
                animate_or_save_image(scale=s, chord=args['chord'], root=args['root'], mode=args['mode'], save_png=args['output'], single=False)
        if args['chord'] == 'all':
            for c in mt.all_chord_info.keys():
                animate_or_save_image(scale=args['scale'], chord=c, root=args['root'], mode=args['mode'], save_png=args['output'], single=False)
        if args['root'] == 'all':
            for n in chromatic_note_names:
                animate_or_save_image(scale=args['scale'], chord=args['chord'], root=n, mode=args['mode'], save_png=args['output'], single=False)
    # all modes case
    else:
        base_scale_notes = mt.construct_scale(mt.Note(args['root'],4), mt.all_scale_info[args['scale']]['signature'], len(mt.all_scale_info[args['scale']]['signature']))
        if len(base_scale_notes) != 7:
            raise ValueError("Error: Modes not supported for non-heptatonic scales")
        for m, n in zip(mt.mode_info, base_scale_notes):
            animate_or_save_image(scale=args['scale'], chord=args['chord'], root=n.name, mode=m, save_png=args['output'], single=False)


def main():
    from music_theory_lab import parse_arguments
    args = parse_arguments()
    process_command(args)

if __name__ == '__main__':
    main()
