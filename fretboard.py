import mt_toolbox as mt
import matplotlib.pyplot as plt
from note import Note, basic_notes
import numpy as np
FRET_COUNT = 24
GUITAR_STRING_NAMES = [Note('E', 4), Note('B', 3), Note('G', 3), Note('D', 3), Note('A', 2), Note('E', 2)] # Ordered from 1st to 6th
# Create a 6 x 24 NumPy array with string data type
fretboard_np = np.empty((6, FRET_COUNT+1), dtype='U10')

def generate_fret_notes(open_string_note):
    fret_notes = open_string_note.get_consecutive_notes(FRET_COUNT+1)
    return [n.name for n in fret_notes]

def generate_all_notes():
    global fretboard_np
    # Populate the array with strings (example: 'Row_x_Col')
    for i, n in enumerate(GUITAR_STRING_NAMES):
        fretboard_np[i, :] = generate_fret_notes(n)

def show_notes(notenames):
    for n in notenames:
        pos_y, pos_x = np.where(fretboard_np == n)
        pos_y += 1 # string count starts from 1
        for x, y in zip(pos_x, pos_y):
            ax.scatter(x, y, s=0.5**2 * 1000, facecolor='red', edgecolor='red', zorder=2, clip_on=False)
            ax.text(x, y, n, color='white', fontsize=10, va='center', ha='center', weight='bold')




# Define the number of frets and strings
num_frets = 24
num_strings = 6

# Create a figure and axis with a dark background color
fig, ax = plt.subplots(figsize=(8, 6))
fig.patch.set_facecolor('#1e1e1e')  # Dark background color

# Set the limits for the plot
ax.set_xlim(0, num_frets + 1)
ax.set_ylim(num_strings + 0.5, 0.5)  # Reverse the Y-axis limits

# Draw the frets as horizontal lines with a color close to the fretboard color
for fret in range(1, num_frets + 1):
    ax.axvline(fret, color='#4d4d4d', linestyle='-', linewidth=2)  # Dark gray color

# Draw the strings as vertical lines with different thicknesses
string_color = '#808080'  # Gray color
string_thicknesses = [1, 1.5, 1.5, 2, 2, 3]  # Example thicknesses for each string
for string, thickness in zip(range(1, num_strings + 1), string_thicknesses):
    ax.axhline(string, color=string_color, linestyle='-', linewidth=thickness)

# Label the axes
ax.set_xlabel('Frets', color='white')  # White text color
ax.set_ylabel('Strings', color='white')  # White text color

# Set the aspect ratio to be equal
ax.set_aspect('equal')

# Set the ticks to represent the fret numbers
ax.set_xticks(range(1, num_frets + 1))
ax.set_yticks(range(num_strings, 0, -1))  # Reverse the Y-axis ticks

# Set the color of the axes ticks
ax.tick_params(axis='x', colors='white')
ax.tick_params(axis='y', colors='white')

# Remove ticks on the top and right sides of the plot
ax.tick_params(right=False, top=False)

# Set the background color of the plot
ax.set_facecolor('#8B4513')  # Dark background color

# Draw filled circles (inlays) at specific fret positions
inlay_frets = [3, 5, 7, 9, 15, 17, 19, 21]
inlay_positions = [(fret-0.5, 3.5) for fret in inlay_frets]  # Example positions for inlays
inlay_positions = inlay_positions + [(12,2),(12,5),(24,2),(24,5)]
inlay_radius = 0.25  # Radius of the inlay circles
inlay_color = 'grey'  # Color of the inlay circles
ax.scatter(*zip(*inlay_positions), color=inlay_color, s=inlay_radius**2 * 1000, edgecolor='black', linewidth=1)
generate_all_notes()
scale_notes = mt.construct_scale(Note('A', 4), mt.all_scale_info['Minor']['signature'])
#show_notes(basic_notes.keys())
show_notes([n.name for n in scale_notes])

# Display the plot
plt.title('Guitar Fretboard (Y-axis reversed)', color='white')  # White text color for the title
plt.show()
