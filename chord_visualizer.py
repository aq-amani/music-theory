import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from mt_toolbox import basic_notes

# Set up the figure and axis
fig, ax = plt.subplots(figsize=(8, 8), facecolor='gray')
fig.canvas.manager.set_window_title('Chord visualizer')
# Remove axes
ax.axis('off')
# color of center circle and note lines
structure_color = 'black'

## Reference lists
# colors of small circles representing notes
circle_colors = ['firebrick', 'saddlebrown', 'orange', 'darkkhaki', 'yellow', 'limegreen', 'darkolivegreen', 'dodgerblue', 'slategrey', 'slateblue', 'darkviolet', 'indigo']
# list of chromatic intervals
interval_list = ['1', 'm2', '2', 'm3', '3', 'P4', 'A4', 'P5', 'm6', '6', 'm7', '7']
# list of chromatic note names
chromatic_note_names = list(basic_notes.keys())
# degrees on the chromatic "clock" for all 12 chromatic angle degrees
chromatic_angle_degrees = -1 * np.arange(0, (12+1) * 30, 30) + 450
# ---------------------------------
## Global parameters that are assigned using setup_parameters
# chromatic_note_names but rotated left to start from a specific root note
rotated_chromatic_note_names = []
# positions of notes to plot (list indexes) with reference to a chromatic scale(0~11)
positions_to_plot = []
# text representing the chord/scale name to place on center circle
object_name_label = ''
# chromatic_angle_degrees but rotated left to start at the degree of the specfied root note
rotated_angle_degrees = []
# ---------------------------------
# ANIMATE flag: show notes one by one or all at once in one frame
ANIMATE = False
# length and radius values
tick_circle_radius = 1.4
tick_length = 0.05
offset_from_circle_center = 0.3 # for interval labels
circle_radius = 0.2 # note circles radius

def plot_base_circles():
    """Function to plot the center circle and the ticks (chromatic clock) circle
    """
    # Plot the center circle
    center_circle = plt.Circle((0, 0), 0.3, color=structure_color, zorder=2)
    ax.add_patch(center_circle)

    # Plot ticks circle with ticks at 30-degree intervals
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

    # plot ticks circle and center circle
    plot_base_circles()

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
        # Plot the line
        ax.plot(x_line, y_line, color=structure_color, lw=10, zorder=1)
        # Plot a circle at the end of the line with a fixed color
        circle = plt.Circle((np.cos(angle_rad), np.sin(angle_rad)), circle_radius, zorder=2, edgecolor=structure_color, lw=1)
        circle.set_facecolor(circle_colors[pos])
        ax.add_patch(circle)

        # Active labels on ticks circle
        n_pos_x = np.cos(angle_rad)+np.cos(angle_rad)*(circle_radius+offset_from_circle_center)
        n_pos_y = np.sin(angle_rad)+np.sin(angle_rad)*(circle_radius+offset_from_circle_center)
        ax.text(n_pos_x, n_pos_y, active_external_label, ha='center', va='center', color='black', fontsize=12, weight='bold')

        # Labels at circle centers
        if positions_to_plot.count(pos) > 1 and octave_flag:
            note_circle_label = '\n\n+Octave'
        elif octave_flag:
            note_circle_label = interval_list[pos]+'\n+Octave'
        else:
            note_circle_label = interval_list[pos]
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

def apply_rotations(root_name, modal_root):
    """Applies necessary rotations to the reference note and angle lists for non C roots
    Arguments:
    root_name -- name of the root note
    modal_root -- name of the new root in case of a modal scale
    """
    global rotated_chromatic_note_names
    global rotated_angle_degrees
    # Rotations necessary to start at notes other than C
    root_pos = chromatic_note_names.index(root_name)
    modal_root_pos = chromatic_note_names.index(modal_root) # Only affects label list. Angels stay the same
    #rotate chromatic note list
    rotated_chromatic_note_names = chromatic_note_names[modal_root_pos:]+chromatic_note_names[:modal_root_pos]
    #rotate excluding the last wrap back angle
    rotated_angle_degrees = np.concatenate((chromatic_angle_degrees[root_pos:-1], chromatic_angle_degrees[:root_pos]))
    # include the first angle to wrap back to the first note
    rotated_angle_degrees = np.append(rotated_angle_degrees, rotated_angle_degrees[0])
    # Rotations necessary for scale modes other than Ionian

def setup_parameters(notes, root, name_label):
    """Sets up the necessary parameters for the plots

    Arguments:
    notes -- List of note objects represeting chords or scales to plot
    root -- root name of the chord or scale object
    name_label -- label to show on the plotted object
    """
    global positions_to_plot
    global object_name_label
    # Apply necessary rotations
    apply_rotations(root, notes[0].name)
    # Set positions to plot
    positions_to_plot = []
    for n in notes:
      positions_to_plot.append(rotated_chromatic_note_names.index(n.name))
    # Set object labels
    object_name_label = name_label

def save_plot_image(img_name):
    """Animate the chord/scale or save an image of the plot

    Arguments:
    img_name -- name to use for the image to save
    """
    num_lines = len(positions_to_plot)
    update(num_lines - 1)
    plt.savefig(img_name)

def animate_plot(pause_length=4, single_run=True):
    """Animate the chord/scale or save an image of the plot

    Arguments:
    pause_length -- time to pause before clearing a plot and drawing the next, in case of looped runs
    single_run -- single run or part of a looped run. To control plot closing and delay in case of looped runs
    """
    num_lines = len(positions_to_plot)
    animation = FuncAnimation(fig, update, frames=num_lines if ANIMATE else 1, interval=300, blit=False, repeat=False)
    if single_run:
        plt.show()
    else:
        # Remove axes
        ax.axis('off')
        plt.show(block=False)
        # Adjust delay between consecutive plots/playbacks
        # non arpeggiated chords finish faster
        #pause_length = 1.2 if chord and not arp else 4
        plt.pause(pause_length)

if __name__ == '__main__':
    print('Not intended for stand alone use')
