
import curses
from curses import wrapper

import time


def main(stdscr):
    # Frame the interface area at fixed VT100 size
    global screen
    sz = stdscr.getmaxyx()
    screen = stdscr.subwin(sz[0], sz[1], 0, 0)
    screen.box()
    screen.hline(2, 1, curses.ACS_HLINE, sz[1] - 2)
    screen.refresh()

    for _ in range(20):
        sz = stdscr.getmaxyx()
        screen = stdscr.subwin(sz[0], sz[1], 0, 0)
        screen.box()
        screen.hline(2, 1, curses.ACS_HLINE, sz[1] - 2)
        screen.refresh()
        time.sleep(1)

    # Define the topbar menus
    file_menu = ("File", "file_func()")
    proxy_menu = ("Proxy Mode", "proxy_func()")
    doit_menu = ("Do It!", "doit_func()")
    help_menu = ("Help", "help_func()")
    exit_menu = ("Exit", "EXIT")
    # Add the topbar menus to screen object
    # topbar_menu((file_menu, proxy_menu, doit_menu,
    #              help_menu, exit_menu))
    #
    # # Enter the topbar menu loop
    # while topbar_key_handler():
    #     draw_dict()


def run_experiment():
    wrapper(main)
