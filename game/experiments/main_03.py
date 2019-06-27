import curses
from Queue import Queue, Empty as QueueEmptyError
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


class Glopnet:
    def __init__(self):
        self.stdscr = None

        self.should_close = False

        self.i_thread = None
        self.d_thread = None
        self.u_thread = None

        self.lookup = {
            'resize': False,
            'info': "TEST",
        }

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
        self.i_thread = Thread(target=self.input_thread, name="input_thread", kwargs=i_args)
        d_args = {
            "glopnet": self,
            "curses_lock": curses_lock,
            "stop_lock": d_stop_lock,
        }
        self.d_thread = Thread(target=self.draw_thread, name="draw_thread", kwargs=d_args)
        u_args = {
            "glopnet": self,
            "input_thread": self.i_thread,
            "draw_thread": self.d_thread,
            "input_queue": input_queue,
            "curses_lock": curses_lock,
            "i_stop_lock": i_stop_lock,
            "d_stop_lock": d_stop_lock,
        }
        self.u_thread = Thread(target=self.update_thread, name="update_thread", kwargs=u_args)

    def screen_setup(self):
        # Start colors in curses
        curses.start_color()
        curses.init_pair(WHITE_ON_RED, curses.COLOR_WHITE, curses.COLOR_RED)
        curses.init_pair(WHITE_ON_BLUE, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(BLACK_ON_WHITE, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(BLACK_ON_BLUE, curses.COLOR_BLACK, curses.COLOR_BLUE)

        # Set which mouse buttons are allowed (Rightclick and Leftclick)
        curses.mousemask(
            0
            | curses.BUTTON1_PRESSED
            | curses.BUTTON1_RELEASED
            | curses.BUTTON1_CLICKED
            | curses.BUTTON3_PRESSED
            | curses.BUTTON3_RELEASED
            | curses.BUTTON3_CLICKED
        )
        curses.curs_set(0)

        # Don't wait for getch()
        self.stdscr.nodelay(1)
        self.stdscr.leaveok(1)

        # Clear and refresh the screen for a blank canvas
        self.stdscr.clear()
        self.stdscr.refresh()

    def resize_screen(self):
        self.lookup['info'] = "{}{}".format(str(self.stdscr.getmaxyx()))
        h, w = self.stdscr.getmaxyx()
        curses.resize_term(h, w)

    def run(self):

        try:
            # Initialize curses
            self.stdscr = curses.initscr()
            curses.noecho()
            curses.cbreak()
            self.stdscr.keypad(1)

            # Do setup
            self.setup()
            self.screen_setup()

            # Start update thread
            self.u_thread.start()
            self.u_thread.join()

        finally:
            # Set everything back to normal
            if self.stdscr is not None:
                self.stdscr.keypad(0)
                curses.echo()
                curses.nocbreak()
                curses.endwin()

    def process_input(self, input_list):
        for ch in input_list:
            if ch is None or ch == -1:
                return

            elif ch == ord('q'):
                self.should_close = True
            elif ch == curses.KEY_MOUSE:
                pass
            elif ch == curses.KEY_RESIZE:
                self.lookup['resize'] = True
                self.lookup['info'] = "RESIZING!"

    def update(self):
        pass

    def render(self):
        self.stdscr.clear()
        
        max_h, max_w = self.stdscr.getmaxyx()

        # Draw frame
        self.stdscr.attron(curses.color_pair(BLACK_ON_WHITE))
        # first line
        self.stdscr.hline(0, 1, " ", max_w - 2)
        # edges
        self.stdscr.vline(1, 0, " ", max_h - 3)
        self.stdscr.vline(1, max_w - 1, " ", max_h - 3)
        # last line
        self.stdscr.hline(max_h - 2, 1, " ", max_w - 2)
        self.stdscr.attroff(curses.color_pair(BLACK_ON_WHITE))

        safe_addstr(self.stdscr, 1, 1, str(self.lookup['info']))

    @staticmethod
    def update_thread(**kwargs):
        glopnet = kwargs.get('glopnet')
        i_thread = kwargs.get('input_thread')
        d_thread = kwargs.get('draw_thread')
        input_queue = kwargs.get('input_queue')
        curses_lock = kwargs.get('curses_lock')
        i_stop_lock = kwargs.get('i_stop_lock')
        d_stop_lock = kwargs.get('d_stop_lock')

        i_stop_lock.acquire()
        d_stop_lock.acquire()

        i_thread.start()
        d_thread.start()

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

            curses_lock.acquire()  # =============================================================== CURSES LOCK ACQUIRE

            if glopnet.lookup['resize']:
                glopnet.lookup['resize'] = False
                glopnet.resize_screen()
            glopnet.process_input(input_to_process)
            glopnet.update()

            curses_lock.release()  # =============================================================== CURSES LOCK RELEASE

            if glopnet.should_close:
                i_stop_lock.release()
                d_stop_lock.release()
                i_thread.join()
                d_thread.join()
                break
            sleep(SPT)

    @staticmethod
    def draw_thread(**kwargs):
        glopnet = kwargs.get('glopnet')
        stop_lock = kwargs.get('stop_lock')
        curses_lock = kwargs.get('curses_lock')

        while True:
            if stop_lock.acquire(blocking=False):
                break

            curses_lock.acquire()  # =============================================================== CURSES LOCK ACQUIRE
            glopnet.render()
            curses_lock.release()  # =============================================================== CURSES LOCK RELEASE

            sleep(SPF)

    @staticmethod
    def input_thread(**kwargs):
        glopnet = kwargs.get('glopnet')
        stop_lock = kwargs.get('stop_lock')
        input_queue = kwargs.get('input_queue')
        curses_lock = kwargs.get('curses_lock')

        while True:
            if stop_lock.acquire(blocking=False):
                break

            curses_lock.acquire()  # =============================================================== CURSES LOCK ACQUIRE
            while True:
                ch = glopnet.stdscr.getch()
                if ch == -1:
                    break
                else:
                    input_queue.put(ch)
            curses_lock.release()  # =============================================================== CURSES LOCK RELEASE

            sleep(SPF/4.0)


def safe_addstr(scr, y, x, string):
    if x + len(string) >= scr.getmaxyx()[1]:
        try:
            scr.addstr(y, x, string)
        except curses.error:
            pass
    else:
        scr.addstr(y, x, string)


def run_experiment():
    run()
