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

# length and radius values
tick_circle_radius = 1.4
tick_length = 0.05
offset_from_circle_center = 0.3 # for interval labels
circle_radius = 0.2 # note circles radius

# Function to update the plot for each frame of the animation
def update(frame):
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
        # Interval labels at a nice distance outside the circle
        n_pos_x = np.cos(angle_rad)+np.cos(angle_rad)*(circle_radius+offset_from_circle_center)
        n_pos_y = np.sin(angle_rad)+np.sin(angle_rad)*(circle_radius+offset_from_circle_center)
        external_reference_label = chromatic_note_names[i] # labels outside the circle that are grayed out unless active
        ax.text(n_pos_x, n_pos_y, external_reference_label, ha='center', va='center', color='dimgray', fontsize=12, weight='bold')

        ax.plot([x_tick_start, x_tick_end], [y_tick_start, y_tick_end], color='dimgray', linewidth=4)
    tick_circle = plt.Circle((0,0), tick_circle_radius, zorder=0, edgecolor='dimgray', lw=4)
    tick_circle.set_facecolor('grey')
    ax.add_patch(tick_circle)

    prev_pos = positions_to_plot[0]
    octave_flag = False
    for idx, pos in enumerate(positions_to_plot[:frame+1]):
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

def process(mode, root, name, playback=True):
    """Returns num_lines necessary to create the plot

    Arguments:
    mode -- 's' or 'c' for scale or chord
    root -- root note (if specified)
    name -- scale or chord name
    playback -- whether to play the chord/scale or not
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

    if mode == 's':
        positions_to_plot = mt.tone_to_chrom_positions(mt.all_scale_info[name]['signature'])
        object_name_label = name+'\nscale'
        if root:
            notes_to_plot= mt.construct_scale(mt.Note(root,4), mt.all_scale_info[name]['signature'], len(mt.all_scale_info[name]['signature'])+1)
            if playback:
                pb.create_midi(notes_to_plot, 'scale', t = 2.05)
                thread = threading.Thread(target=pb.play_midi_file, args=(pb.midi_filename,))
                thread.start()
    elif mode == 'c':
        positions_to_plot = mt.intervals_to_chrom_positions(mt.all_chord_info[name]['signature'])
        object_name_label = name+'\nchord'
        if root:
            scale = mt.construct_scale(mt.Note(root,4), mt.all_scale_info['Major']['signature'], 9)
            notes_to_plot= mt.construct_chord(mt.all_chord_info[name]['signature'], scale)
            if playback:
                pb.create_arp_chord_midi(notes_to_plot, t = 2.05)
                thread = threading.Thread(target=pb.play_midi_file, args=(pb.midi_filename,))
                thread.start()
    num_lines = len(positions_to_plot)
    return num_lines

def main():

    parser = argparse.ArgumentParser(description='A script to visualize scales and chords in a group-theoric way')
    root_choices = list(mt.basic_notes.keys())
    root_choices.extend(note_info['alt_name'] for note_info in mt.basic_notes.values() if note_info['alt_name'])
    chord_choices = list(mt.all_chord_info.keys())
    chord_choices.extend(['all'])
    scale_choices = list(mt.all_scale_info.keys())
    scale_choices.extend(['all'])

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-c','--chord', choices=chord_choices, help=f'Specify the chord type', metavar = '')
    group.add_argument('-s','--scale', choices=scale_choices, help='Specify the scale type', metavar = '')

    parser.add_argument('-r','--root', choices=root_choices ,help='Root note name', metavar = '')
    parser.add_argument('-o','--output', help='Save as png image', action ='store_true')

    args = vars(parser.parse_args())
    if args['scale'] != 'all' and args['chord'] != 'all':
        if args['output']:
            num_lines = process('s' if args['scale'] else 'c', args['root'], args['scale'] if args['scale'] else args['chord'], playback=False)
            update(num_lines - 1)
            img_name = args['root']+'_'+args['scale']+'_scale.png' if args['scale'] else args['root']+'_'+args['chord']+'_chord.png'
            plt.savefig(img_name)
        else:
            num_lines = process('s' if args['scale'] else 'c', args['root'], args['scale'] if args['scale'] else args['chord'])
            animation = FuncAnimation(fig, update, frames=num_lines, interval=300, blit=False, repeat=False)
            plt.show()

    if args['scale'] == 'all' or args['chord'] == 'all':
        loop_list = mt.all_scale_info.keys() if args['scale'] else mt.all_chord_info.keys()
        for s in loop_list:
            # Remove axes
            ax.axis('off')
            if args['output']:
                num_lines = process('s' if args['scale'] else 'c', args['root'], s, playback=False)
                update(num_lines - 1)
                img_name = args['root']+'_'+s+'_scale.png' if args['scale'] else args['root']+'_'+s+'_chord.png'
                plt.savefig(img_name)
            else:
                num_lines = process('s' if args['scale'] else 'c', args['root'], s)
                animation = FuncAnimation(fig, update, frames=num_lines, interval=300, blit=False, repeat=False)
                plt.show(block=False)
                plt.pause(4)

if __name__ == '__main__':
    main()
