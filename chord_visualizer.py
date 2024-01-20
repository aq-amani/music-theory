import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
import mt_toolbox as mt
import argparse

# Set up the figure and axis
fig, ax = plt.subplots(figsize=(8, 8), facecolor='gray')
ax.set_xlim(-1.5, 1.5)
ax.set_ylim(-1.5, 1.5)
# Remove axes
ax.axis('off')

structure_color = 'black'

colors = ['firebrick', 'saddlebrown', 'orange', 'darkkhaki', 'yellow', 'limegreen', 'darkolivegreen', 'dodgerblue', 'slategrey', 'slateblue', 'darkviolet', 'indigo']
interval_list = ['1', 'm2', '2', 'm3', '3', 'P4', 'A4', 'P5', 'm6', '6', 'm7', '7']

circle_colors = colors

positions = []
notes = []
angle_degrees = []
name_label = ''
# Function to update the plot for each frame of the animation
def update(frame):
    ax.clear()

    # Set the same figure and axis size for every frame
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)

    # Plot a white circle at the center
    center_circle = plt.Circle((0, 0), 0.3, color=structure_color, zorder=2)
    ax.add_patch(center_circle)

    # Ticks circle at 30-degree intervals
    tick_circle_radius = 1.4
    tick_length = 0.05  # Adjust the length of the ticks

    for angle in range(0, 360, 30):
        angle_rad = np.deg2rad(angle)
        x_tick_start = np.cos(angle_rad) * tick_circle_radius
        y_tick_start = np.sin(angle_rad) * tick_circle_radius
        x_tick_end = np.cos(angle_rad) * (tick_circle_radius - tick_length)
        y_tick_end = np.sin(angle_rad) * (tick_circle_radius - tick_length)

        ax.plot([x_tick_start, x_tick_end], [y_tick_start, y_tick_end], color='dimgray', linewidth=4)
    tick_circle = plt.Circle((0,0), tick_circle_radius, zorder=0, edgecolor='dimgray', lw=4)
    tick_circle.set_facecolor('grey')
    ax.add_patch(tick_circle)

    prev_i = positions[0]
    octave_flag = False
    for idx, i in enumerate(positions[:frame+1]):
        reversed_index = len(positions) - i
        #If the new index is lower, this means we proceeded to the next octave
        # flag is used to add text to the label of notes on next octaves(ex.: 9th is 2+octave)
        if not octave_flag:
            if i < prev_i:
                octave_flag = True
            prev_i = i
        current_angle = angle_degrees[i] % 360
        interval_label = interval_list[i]+'\n+Octave' if octave_flag else interval_list[i]

        # Convert angle from degrees to radians
        angle_rad = np.deg2rad(current_angle)

        # Define line coordinates
        x_line = [0, np.cos(angle_rad)]
        y_line = [0, np.sin(angle_rad)]

        # Plot a circle at the end of the line with a fixed color
        circle_radius = 0.2
        circle = plt.Circle((np.cos(angle_rad), np.sin(angle_rad)), circle_radius, zorder=2, edgecolor=structure_color, lw=1)
        circle.set_facecolor(circle_colors[i])
        ax.add_patch(circle)

        # Plot the line
        ax.plot(x_line, y_line, color=structure_color, lw=10, zorder=1)
        # Labels at a nice distance outside the circle
        offset_from_circle_center = 0.3
        n_pos_x = np.cos(angle_rad)+np.cos(angle_rad)*(circle_radius+offset_from_circle_center)
        n_pos_y = np.sin(angle_rad)+np.sin(angle_rad)*(circle_radius+offset_from_circle_center)
        ax.text(n_pos_x, n_pos_y, interval_label, ha='center', va='center', color='black', fontsize=12, weight='bold')
        # Text for object name
        ax.text(0, 0, name_label, ha='center', va='center', color='white', fontsize=10)

        # Labels at circle centers
        if notes:
            note_label = notes[idx].name
            pos_x = np.cos(angle_rad)
            pos_y = np.sin(angle_rad)
            ax.text(pos_x, pos_y, note_label, ha='center', va='center', color='black', fontsize=10, weight='bold')

    # Set aspect ratio to equal
    ax.set_aspect('equal')

    # Remove axes
    ax.axis('off')

    return ax

def main():
    global positions
    global notes
    global angle_degrees
    global name_label
    parser = argparse.ArgumentParser(description='A script to visualize scales and chords in a group-theoric way')
    root_choices = list(mt.basic_notes.keys())
    root_choices.extend(note_info['alt_name'] for note_info in mt.basic_notes.values() if note_info['alt_name'])
    chord_choices = list(mt.all_chord_info.keys())
    scale_choices = list(mt.all_scale_info.keys())

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-c','--chord', choices=chord_choices, help=f'Specify the chord type', metavar = '')
    group.add_argument('-s','--scale', choices=scale_choices, help='Specify the scale type', metavar = '')

    parser.add_argument('-r','--root', choices=root_choices ,help='Root note name', metavar = '')

    args = vars(parser.parse_args())
    if args['scale']:
        positions = mt.tone_to_chrom_positions(mt.all_scale_info[args['scale']]['signature'])
        name_label = args['scale']+'\nscale'
        if args['root']:
            notes= mt.construct_scale(mt.Note(args['root'],4), mt.all_scale_info[args['scale']]['signature'])
    elif args['chord']:
        positions = mt.intervals_to_chrom_positions(mt.all_chord_info[args['chord']]['signature'])
        name_label = args['chord']+'\nchord'
        if args['root']:
            scale = mt.construct_scale(mt.Note(args['root'],4), mt.all_scale_info['Major']['signature'], 9)
            notes= mt.construct_chord(mt.all_chord_info[args['chord']]['signature'], scale)

    num_lines = len(positions)
    angle_degrees = -1 * np.arange(0, (12+1) * 30, 30) + 450 # get all 12 chromatic angle degrees

    # Create an animation
    animation = FuncAnimation(fig, update, frames=num_lines, interval=300, blit=False, repeat=False)
    plt.show()

if __name__ == '__main__':
    main()
