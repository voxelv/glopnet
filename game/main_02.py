
import curses
import os


def run():
    ch = -1
    count = 0
    event = None

    os.environ['TERM'] = "xterm-1003"

    screen = curses.initscr()
    curses.raw()
    screen.keypad(True)
    curses.noecho()

    screen.clear()
    curses.cbreak()

    curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)

    while ch != ord('q'):
        count += 1
        # screen.addstr(1, 1, "Has mouse {}".format(curses.has_mouse()))
        screen.addstr(2, 1, "Key code: {}; mouse code:{}".format(ch, curses.KEY_MOUSE))
        if ch == curses.KEY_MOUSE:
            event = curses.getmouse()
            screen.addstr(3, 3, "Mouse Event: x={}, y={}, z={}".format(event[1], event[2], event[3]))
            screen.addstr(4, 3, "Mouse device id: {}".format(event[0]))
            screen.addstr(5, 3, "Mouse button mask: {}".format(event[4]))
        screen.addstr(6, 1, "Event number: {}".format(count))
        screen.refresh()
        ch = screen.getch()
    curses.endwin()
