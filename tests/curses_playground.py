import curses
from curses import wrapper
from time import sleep


def main(stdscr):
    k = 0
    cursor_x = 0
    cursor_y = 0

    # Clear and refresh the screen for a blank canvas
    stdscr.clear()
    stdscr.refresh()

    # Start colors in curses
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_RED)

    curses.mousemask(
        0
        | curses.ALL_MOUSE_EVENTS
        | curses.REPORT_MOUSE_POSITION
    )

    stdscr.nodelay(1)

    # Loop where k is the last character pressed
    while k != ord('q'):
        # curses.curs_set(0)

        # Initialization
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        # Single-point mouseinfo read
        try:
            mouseinfo = curses.getmouse()
        except curses.error:
            mouseinfo = (-1, -1, -1, -1, -1)

        if k == curses.KEY_DOWN:
            cursor_y = cursor_y + 1
        elif k == curses.KEY_UP:
            cursor_y = cursor_y - 1
        elif k == curses.KEY_RIGHT:
            cursor_x = cursor_x + 1
        elif k == curses.KEY_LEFT:
            cursor_x = cursor_x - 1

        cursor_x = max(0, cursor_x)
        cursor_x = min(width-1, cursor_x)

        cursor_y = max(0, cursor_y)
        cursor_y = min(height-1, cursor_y)

        # Declaration of strings
        title = "Curses example"[:width-1]
        subtitle = "Written by Clay McLeod"[:width-1]
        keystr = "Last key pressed: {}".format(k)[:width-1]
        statusbarstr = "Press 'q' to exit | STATUS BAR | Pos: {}, {} | M: {}, {}".format(cursor_x, cursor_y, mouseinfo[2], mouseinfo[3])
        if k == 0:
            keystr = "No key press detected..."[:width-1]
        elif k == curses.KEY_MOUSE:
            try:
                keystr = "Mouse key pressed: {}".format(mouseinfo)[:width-1]
            except curses.error:
                pass

        # Centering calculations
        start_x_title = int((width // 2) - (len(title) // 2) - len(title) % 2)
        start_x_subtitle = int((width // 2) - (len(subtitle) // 2) - len(subtitle) % 2)
        start_x_keystr = int((width // 2) - (len(keystr) // 2) - len(keystr) % 2)
        start_y = int((height // 2) - 2)

        # Rendering some text
        whstr = "Width: {}, Height: {}".format(width, height)
        stdscr.addstr(0, 0, whstr, curses.color_pair(1))

        # Render status bar
        stdscr.attron(curses.color_pair(3))
        stdscr.addstr(height-1, 0, statusbarstr)
        try:
            stdscr.addstr(height-1, len(statusbarstr), " " * (width - len(statusbarstr)))
        except curses.error:
            pass
        stdscr.attroff(curses.color_pair(3))

        # Turning on attributes for title
        stdscr.attron(curses.color_pair(2))
        stdscr.attron(curses.A_BOLD)

        # Rendering title
        stdscr.addstr(start_y, start_x_title, title)

        # Turning off attributes for title
        stdscr.attroff(curses.color_pair(2))
        stdscr.attroff(curses.A_BOLD)

        # Print rest of text
        stdscr.addstr(start_y + 1, start_x_subtitle, subtitle)
        stdscr.addstr(start_y + 3, (width // 2) - 2, '-' * 4)
        stdscr.addstr(start_y + 5, start_x_keystr, keystr)

        # Render mouse click pos
        mousestr = "!"
        stdscr.attron(curses.color_pair(4))
        stdscr.attron(curses.A_BOLD)
        try:
            mousepos = mouseinfo
            stdscr.addstr(mousepos[2], mousepos[1], mousestr)
        except curses.error:
            pass
        stdscr.attroff(curses.color_pair(4))
        stdscr.attroff(curses.A_BOLD)

        # Move the cursor to position
        stdscr.move(cursor_y, cursor_x)

        # Refresh the screen
        stdscr.refresh()

        # Wait for next input
        k = stdscr.getch()

        sleep(1.0/60.0)


def run():
    wrapper(main)


if __name__ == '__main__':
    import os
    os.environ['TERM'] = "xterm-1003"
    run()
