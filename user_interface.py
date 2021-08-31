import curses
import music_theory as mt

main_menu = ['Scale', 'Chord', 'EXIT']
octave_menu = ['2', '3', '4', '5', '6', 'BACK', 'EXIT']
#root_menu= ['C', 'C#', 'D', 'D#', 'E','F','F#','G', 'G#', 'A', 'A#', 'B', 'BACK', 'EXIT']
root_menu = list((mt.basic_notes).keys())
root_menu.extend(['BACK', 'EXIT'])
scale_menu = list((mt.scale_signatures).keys())
scale_menu.extend(['BACK', 'EXIT'])
chord_menu = list((mt.chord_signatures).keys())
chord_menu.extend(['BACK', 'EXIT'])
#scale_menu = ['Major', 'minor', 'Diminished', 'Augmented', 'Major Pentatonic', 'minor Pentatonic', 'Blues', 'BACK', 'EXIT']
#chord_menu = ['Major','minor','Diminished','Augmented','Suspended2', 'Suspended4','Major 7th', 'minor 7th', 'Dominant 7th',
#                         'Major 9th', 'minor 9th', 'Dominant 9th', 'Half diminished', 'Whole diminished', 'BACK', 'EXIT']
confirm_menu = ['OK', 'BACK']
screen_list = [main_menu, octave_menu, confirm_menu, root_menu, confirm_menu, []]

def print_menu(stdscr, selected_row_idx, menu, menu_title):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    for idx, row in enumerate(menu):
        x = w//2 - len(row)//2
        y = h//2 - len(menu)//2 + idx
        if idx == selected_row_idx:
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(y, x, row)
            stdscr.attroff(curses.color_pair(1))
        else:
            stdscr.addstr(y, x, row)
    stdscr.addstr(int(y/2), x, menu_title)
    stdscr.refresh()


def print_center(stdscr, text):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    x = w//2 - len(text)//2
    y = h//2
    stdscr.addstr(y, x, text)
    stdscr.refresh()


def main(stdscr):
    # turn off cursor blinking
    curses.curs_set(0)

    # color scheme for selected row
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

    # specify the current selected row
    current_row = 0

    # print the menu
    print_menu(stdscr, current_row)

    while 1:
        key = stdscr.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(main_menu)-1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            print_center(stdscr, "You selected '{}'".format(main_menu[current_row]))
            stdscr.getch()
            # if user selected last row, exit the program
            if current_row == len(main_menu)-1:
                break

        print_menu(stdscr, current_row)

#def scale_func(stdscr):
octave = 2
root = 'C'
mode = ''

def mainother(stdscr):
    # turn off cursor blinking
    curses.curs_set(0)

    # color scheme for selected row
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

    # specify the current selected row
    current_row = 0
    current_menu_index = 0

    # print the menu
    print_menu(stdscr, current_row, screen_list[current_menu_index], 'Menu title goes here')

    while 1:
        key = stdscr.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(screen_list[current_menu_index])-1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            selection = screen_list[current_menu_index][current_row]
            #print(selection)
            #print_center(stdscr, "You selected '{}'".format(screen_list[current_menu_index][current_row]))
            #print(current_menu_index, current_row)
            if screen_list[current_menu_index][current_row] == 'EXIT':
                break
            elif screen_list[current_menu_index][current_row] == 'BACK':
                if current_menu_index in (3,5):
                    current_menu_index -= 2
                else:
                    current_menu_index -= 1
            else:
                if screen_list[current_menu_index][current_row] == 'Scale':
                    screen_list[len(screen_list)-1] = scale_menu
                    mode = screen_list[current_menu_index][current_row]

                if screen_list[current_menu_index][current_row] == 'Chord':
                    screen_list[len(screen_list)-1] = chord_menu
                    mode = screen_list[current_menu_index][current_row]
                if current_menu_index == 1:
                    octave = int(screen_list[current_menu_index][current_row])
                    mt.play_major_with_octave(octave)
                elif current_menu_index == 3:
                    root = screen_list[current_menu_index][current_row]
                    mt.play_note_by_name(root, 200, octave)
                elif current_menu_index == 5:
                    if mode == 'Scale':
                        mt.construct_and_play_scale(root, octave, screen_list[current_menu_index][current_row])
                    if mode == 'Chord':
                        mt.construct_and_play_chord(root, octave, screen_list[current_menu_index][current_row])
                if current_menu_index < len(screen_list)-1:
                    current_menu_index += 1
                    #preview_player call here

            #current_row = 0
            print_menu(stdscr, current_row, screen_list[current_menu_index], 'Menu title goes here')
            #print_center(stdscr, "You selected '{}'".format(selection))
            current_row = 0
                # Call chord play/select function here
            #stdscr.getch()
            #if screen_list[current_menu_index][current_row] == 'EXIT':
                #break

        print_menu(stdscr, current_row, screen_list[current_menu_index], 'Menu title goes here')

#curses.wrapper(main)
curses.wrapper(mainother)
