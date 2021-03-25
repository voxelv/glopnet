import curses
import os
from queue import Queue, Empty as QueueEmptyError
from threading import Thread, RLock

from time import sleep

FPS = 60  # Frames per second (renders)
TPS = 60  # Ticks per second (updates)
SPF = 1.0 / FPS
SPT = 1.0 / TPS


def run():
    app = Glopnet()
    app.run()


# Enumerate colors
WHITE_ON_RED = 1
WHITE_ON_BLUE = 2
BLACK_ON_WHITE = 3
BLACK_ON_BLUE = 4
WHITE_ON_BLACK = 5


class Key:
    def __init__(self, ch, mod=False, s=""):
        self.ch = ch
        self.mod = mod
        self.s = s

    def __repr__(self):
        return f"K: {self.ch}, {self.s}"


class Mouse:
    def __init__(self, info=None):
        self._info = info

    def description(self):
        return "" if self._info is None else str(self._info)

    def __repr__(self):
        return f"M: {self.description()}"


class Glopnet:
    def __init__(self):
        self.stdscr = None
        self.scr_size = (0, 0)
        self.full_redraw = True
        self.notify = ""

        self.should_close = False

        self.i_thread = None
        self.d_thread = None
        self.u_thread = None

    def setup(self):

        input_queue = Queue(maxsize=FPS)
        curses_lock = RLock()
        i_stop_lock = RLock()
        d_stop_lock = RLock()

        i_args = {
            "glopnet": self,
            "curses_lock": curses_lock,
            "input_queue": input_queue,
            "stop_lock": i_stop_lock,
        }
        self.i_thread = Thread(target=input_thread, name="input_thread", kwargs=i_args)
        d_args = {
            "glopnet": self,
            "curses_lock": curses_lock,
            "stop_lock": d_stop_lock,
        }
        self.d_thread = Thread(target=draw_thread, name="draw_thread", kwargs=d_args)
        u_args = {
            "glopnet": self,
            "input_thread": self.i_thread,
            "draw_thread": self.d_thread,
            "input_queue": input_queue,
            "curses_lock": curses_lock,
            "i_stop_lock": i_stop_lock,
            "d_stop_lock": d_stop_lock,
        }
        self.u_thread = Thread(target=update_thread, name="update_thread", kwargs=u_args)

    def screen_setup(self):
        # Start colors in curses
        curses.start_color()
        curses.init_pair(WHITE_ON_RED, curses.COLOR_WHITE, curses.COLOR_RED)
        curses.init_pair(WHITE_ON_BLUE, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(BLACK_ON_WHITE, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(BLACK_ON_BLUE, curses.COLOR_BLACK, curses.COLOR_BLUE)
        curses.init_pair(WHITE_ON_BLACK, curses.COLOR_WHITE, curses.COLOR_BLACK)

        # Set which mouse buttons are allowed (Rightclick and Leftclick)
        mm_info = curses.mousemask(
            0
            | curses.ALL_MOUSE_EVENTS
            | curses.REPORT_MOUSE_POSITION
        )
        self.notify += str(mm_info)
        curses.curs_set(0)

        # Don't wait for getch()
        self.stdscr.nodelay(True)
        self.stdscr.leaveok(True)

        # Clear and refresh the screen for a blank canvas
        self.stdscr.clear()
        self.stdscr.refresh()
        self.scr_size = self.stdscr.getmaxyx()

    def resize_screen(self):
        if curses.is_term_resized(*self.scr_size):
            self.full_redraw = True
            self.scr_size = self.stdscr.getmaxyx()
            curses.resize_term(*self.scr_size)
            curses.curs_set(0)

    def run(self):
        try:
            # Initialize curses
            self.stdscr = curses.initscr()
            curses.noecho()
            curses.cbreak()
            self.stdscr.keypad(True)

            # Do setup
            self.setup()
            self.screen_setup()

            # Start update thread
            self.u_thread.start()
            self.u_thread.join()

        finally:
            # Set everything back to normal
            if self.stdscr is not None:
                self.stdscr.keypad(False)
                curses.echo()
                curses.nocbreak()
                curses.endwin()

    def process_input(self, input_list):
        if len(input_list) > 0:
            self.full_redraw = True
            self.notify += str(input_list)
        for inp in input_list:
            if isinstance(inp, Key):
                key = inp
                if key.ch == -1:
                    continue
                elif key.ch == ord('q'):
                    self.should_close = True
                elif key.ch == ord('w'):
                    self.notify += "w"
                elif key.ch == ord(' '):
                    self.notify = ""
                else:
                    self.notify += key.s

            elif isinstance(inp, Mouse):
                self.notify += " M " + inp.description() + " "
            else:
                self.notify += " ? "

    def update(self):
        pass

    def draw(self):
        if self.full_redraw:
            self.full_redraw = False
            self.stdscr.clear()
            self.scr_size = self.stdscr.getmaxyx()
            h, w = self.scr_size

            # Draw frame
            self.stdscr.attron(curses.color_pair(WHITE_ON_BLUE))
            # first line
            self.stdscr.hline(0, 1, " ", w - 2)
            # edges
            self.stdscr.vline(1, 0, " ", h - 2)
            self.stdscr.vline(1, w - 1, " ", h - 2)
            # last line
            self.stdscr.hline(h - 1, 1, " ", w - 2)
            self.stdscr.attroff(curses.color_pair(WHITE_ON_BLUE))

            self.stdscr.attron(curses.color_pair(WHITE_ON_BLACK))
            safe_addstr(self.stdscr, 2, 1, self.notify)
            self.stdscr.attroff(curses.color_pair(WHITE_ON_BLACK))


def update_thread(**kwargs):
    glopnet = kwargs.get('glopnet')
    i_thread = kwargs.get('input_thread')
    d_thread = kwargs.get('draw_thread')
    input_queue = kwargs.get('input_queue')
    curses_lock = kwargs.get('curses_lock')
    i_stop_lock = kwargs.get('i_stop_lock')
    d_stop_lock = kwargs.get('d_stop_lock')

    assert isinstance(glopnet, Glopnet)

    i_stop_lock.acquire()
    d_stop_lock.acquire()

    i_thread.start()
    d_thread.start()

    sleep(1)

    try:
        while True:
            input_to_process = []
            while not input_queue.empty():
                inp = None
                try:
                    inp = input_queue.get(block=False)
                except QueueEmptyError:
                    pass
                if inp is not None:
                    input_to_process.append(inp)

            glopnet.process_input(input_to_process)
            glopnet.update()

            if glopnet.should_close:
                i_stop_lock.release()
                d_stop_lock.release()
                i_thread.join()
                d_thread.join()
                break
            sleep(SPT)
    except Exception:
        i_stop_lock.release()
        d_stop_lock.release()
        i_thread.join()
        d_thread.join()


def draw_thread(**kwargs):
    glopnet = kwargs.get('glopnet')
    stop_lock = kwargs.get('stop_lock')
    curses_lock = kwargs.get('curses_lock')

    assert isinstance(glopnet, Glopnet)

    while True:
        if stop_lock.acquire(blocking=False):
            break

        curses_lock.acquire()  # =============================================================== CURSES LOCK ACQUIRE
        glopnet.draw()
        curses_lock.release()  # =============================================================== CURSES LOCK RELEASE

        sleep(SPF)


def input_thread(**kwargs):
    glopnet = kwargs.get('glopnet')
    stop_lock = kwargs.get('stop_lock')
    input_queue = kwargs.get('input_queue')
    curses_lock = kwargs.get('curses_lock')

    assert isinstance(glopnet, Glopnet)

    while True:
        if stop_lock.acquire(blocking=False):
            break

        curses_lock.acquire()  # =============================================================== CURSES LOCK ACQUIRE
        while True:
            ch = glopnet.stdscr.getch()
            if ch == -1:
                break
            elif ch == curses.KEY_MOUSE:
                mouseinfo = (-1, -1, -1, -1, -1)
                try:
                    mouseinfo = curses.getmouse()
                except curses.error:
                    pass
                input_queue.put(Mouse(info=mouseinfo))
            elif ch == curses.KEY_RESIZE:
                glopnet.resize_screen()
            else:
                s = str(curses.keyname(ch))
                input_queue.put(Key(ch, mod=False, s=s))
        curses_lock.release()  # =============================================================== CURSES LOCK RELEASE

        sleep(SPF/16.0)


def safe_addstr(scr, y, x, string):
    if x + len(string) >= scr.getmaxyx()[1]:
        try:
            scr.addstr(y, x, string)
        except curses.error:
            pass
    else:
        scr.addstr(y, x, string)


def run_experiment():
    os.environ['TERM'] = "xterm-1003"
    run()
