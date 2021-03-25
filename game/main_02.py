
import curses


def run():
    screen = curses.initscr()
    curses.noecho()
    curses.curs_set(0)
    screen.keypad(True)
    curses.mousemask(1)

    screen.addstr("This is a Sample Curses Script\n\n")

    while True:
        event = screen.getch()
        if event == ord("q"): break
        if event == curses.KEY_MOUSE: screen.addstr(str(curses.getmouse()))

    curses.endwin()
