import curses
from Queue import Queue, Empty as QueueEmptyError
from threading import Thread, RLock

from time import sleep, clock

FPS = 60
SPF = 1.0 / FPS
FRAME_AVG_NUM = 30


def run():
    # curses_wrapper(_wrap_with_curses)
    _wrap_with_curses(None)


def _wrap_with_curses(stdscr):
    app = Glopnet(threading=False)
    app.run()


WHITE_ON_RED = 1
WHITE_ON_BLUE = 2
BLACK_ON_WHITE = 3
BLACK_ON_BLUE = 4


class Glopnet:
    def __init__(self, threading=True):
        self.threading = threading

        self.stdscr = None

        self.should_close = False

        bm = GlopnetButtonMngr(self)
        bm.add_button(5, 5, 1, 10, 'one', "TEST1")
        bm.add_button(7, 5, 1, 10, 'two', "STUFFYNLONGTEXT")
        bm.add_button(9, 5, 3, 10, 'three', "THINGS")

        sm = GlopnetStatusMngr(self)
        sm.set_status("X")

        self.i_thread = None
        self.d_thread = None
        self.u_thread = None

        self.lookup = {
            'frame': 0,
            'frame_times': [0.0] * FRAME_AVG_NUM,
            'last_frame_time': 0.0,
            'mouse_info': (-1, -1, -1, -1, -1),
            'bm': bm,
            'sm': sm,
            'mdata': {"string": "-|-", "data": ["-", "-"]},
            'full_redraw': True,
        }

    def setup(self):

        input_queue = Queue(maxsize=FPS)
        draw_lock = RLock()
        i_stop_lock = RLock()
        d_stop_lock = RLock()

        i_args = {
            "glopnet": self,
            "input_queue": input_queue,
            "stop_lock": i_stop_lock,
        }
        d_args = {
            "glopnet": self,
            "draw_lock": draw_lock,
            "stop_lock": d_stop_lock,
        }
        self.i_thread = Thread(target=self.input_thread, name="input_thread", kwargs=i_args)
        self.d_thread = Thread(target=self.draw_thread, name="draw_thread", kwargs=d_args)
        u_args = {
            "glopnet": self,
            "input_thread": self.i_thread,
            "draw_thread": self.d_thread,
            "input_queue": input_queue,
            "draw_lock": draw_lock,
            "i_stop_lock": i_stop_lock,
            "d_stop_lock": d_stop_lock,
        }
        self.u_thread = Thread(target=self.update_thread, name="update_thread", kwargs=u_args)

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
            # | curses.BUTTON3_PRESSED
            # | curses.BUTTON3_RELEASED
            # | curses.BUTTON3_CLICKED
        )
        curses.curs_set(0)

    def screen_setup(self):

        # Don't wait for getch()
        self.stdscr.nodelay(1)
        self.stdscr.leaveok(1)

        # Clear and refresh the screen for a blank canvas
        self.stdscr.clear()
        self.stdscr.refresh()

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

            if self.threading:
                self.u_thread.start()
                self.u_thread.join()
            else:
                while not self.should_close:
                    self._process_input(self._input())
                    self._update()
                    self._draw()
                    sleep(SPF)

        finally:
            # Set everything back to normal
            if self.stdscr is not None:
                self.stdscr.keypad(0)
                curses.echo()
                curses.nocbreak()
                curses.endwin()

    def _input(self):
        ch = self.stdscr.getch()
        if ch != -1:
            return ch
        else:
            return None

    def _process_input(self, ch):
        if ch is None:
            return

        if ch == ord('q'):
            self.should_close = True
        if ch == curses.KEY_MOUSE:
            minfo = self.lookup['mouse_info']
            try:
                minfo = curses.getmouse()
                self.lookup['mouse_info'] = minfo
            except curses.error:
                pass
            mdata = self.lookup['mdata']['data']
            send_click = False
            if minfo[4] & curses.BUTTON1_PRESSED:
                mdata[0] = "_"
            elif minfo[4] & curses.BUTTON1_RELEASED:
                mdata[0] = "-"
                send_click = True
            elif minfo[4] & curses.BUTTON1_CLICKED:
                mdata[0] = "."
                send_click = True
            elif minfo[4] & curses.BUTTON3_PRESSED:
                mdata[1] = "_"
            elif minfo[4] & curses.BUTTON3_RELEASED:
                mdata[1] = "-"
                send_click = True
            elif minfo[4] & curses.BUTTON3_CLICKED:
                mdata[1] = "."
                send_click = True
            ms = "{}|{}".format(*mdata)
            self.lookup['mdata']['string'] = ms
            if send_click:
                self.lookup['bm'].click(minfo[2], minfo[1])
        if ch == curses.KEY_RESIZE:
            self.lookup['full_redraw'] = True

    def _update(self):
        frame_begin_time = clock()

        # Create status line
        frame_times = self.lookup['frame_times']
        max_frame = max(frame_times)
        mxstr = "{:.6}".format(float(max_frame*1000.0))
        mxstr = "{:0<8}e-3".format(mxstr[:8])
        self.lookup['sm'].set_status("{} | {} {}".format(mxstr, self.lookup['mdata']['string'], self.lookup['mouse_info']))

        # Update button manager
        self.lookup['bm'].update()

        # Frame stuff
        self.lookup['frame'] = self.lookup.get('frame', 0) + 1
        frame_end_time = clock()
        self.lookup['last_frame_time'] = frame_end_time - frame_begin_time
        self.lookup['frame_times'].append(self.lookup['last_frame_time'])
        self.lookup['frame_times'].pop(0)

    def _draw(self):
        if self.lookup['full_redraw']:
            self.lookup['full_redraw'] = False
            self.stdscr.clear()

            # Draw frame
            self.stdscr.attron(curses.color_pair(BLACK_ON_WHITE))
            max_h, max_w = self.stdscr.getmaxyx()
            # first line
            line_fmt = "{: <" + str(max_w) + "}"
            safe_addstr(self.stdscr, 0, 0, line_fmt.format(" "))
            # edges
            for i in range(max_h - 2):
                safe_addstr(self.stdscr, i, 0, " ")
                safe_addstr(self.stdscr, i, max_w - 1, " ")
            # last line
            safe_addstr(self.stdscr, max_h - 2, 0, line_fmt.format(" "))
            self.stdscr.attroff(curses.color_pair(BLACK_ON_WHITE))

        # Draw status line
        self.stdscr.attron(curses.color_pair(BLACK_ON_WHITE))
        self.lookup['sm'].draw(self.stdscr)
        self.stdscr.attroff(curses.color_pair(BLACK_ON_WHITE))

        # Buttons
        self.stdscr.attron(curses.color_pair(WHITE_ON_BLUE))
        self.lookup['bm'].draw(self.stdscr)
        self.stdscr.attroff(curses.color_pair(WHITE_ON_BLUE))

    @staticmethod
    def update_thread(**kwargs):
        glopnet = kwargs.get('glopnet')
        i_thread = kwargs.get('input_thread')
        d_thread = kwargs.get('draw_thread')
        input_queue = kwargs.get('input_queue')
        draw_lock = kwargs.get('draw_lock')
        i_stop_lock = kwargs.get('i_stop_lock')
        d_stop_lock = kwargs.get('d_stop_lock')

        assert isinstance(glopnet, Glopnet)
        assert isinstance(i_thread, Thread)
        assert isinstance(d_thread, Thread)
        assert isinstance(input_queue, Queue)

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

            # Don't draw while updating
            draw_lock.acquire()

            for _ in input_to_process:
                glopnet._process_input(input_to_process.pop(0))
                glopnet.lookup['sm'].i_count()

            glopnet._update()

            # Resume drawing
            draw_lock.release()

            if glopnet.should_close:
                i_stop_lock.release()
                d_stop_lock.release()
                i_thread.join()
                d_thread.join()
                break
            sleep(SPF)

    @staticmethod
    def draw_thread(**kwargs):
        glopnet = kwargs.get('glopnet')
        stop_lock = kwargs.get('stop_lock')
        draw_lock = kwargs.get('draw_lock')

        assert isinstance(glopnet, Glopnet)

        while True:
            if stop_lock.acquire(blocking=False):
                break

            draw_lock.acquire()

            glopnet._draw()

            draw_lock.release()
            sleep(SPF)

    @staticmethod
    def input_thread(**kwargs):
        glopnet = kwargs.get('glopnet')
        stop_lock = kwargs.get('stop_lock')
        input_queue = kwargs.get('input_queue')

        assert isinstance(glopnet, Glopnet)
        assert isinstance(input_queue, Queue)

        while True:
            if stop_lock.acquire(blocking=False):
                break
            inp_list = []
            inp = glopnet._input()
            while inp is not None:
                inp_list.append(inp)
                inp = glopnet._input()

            for i in inp_list:
                input_queue.put(i)

            sleep(SPF)


class GlopnetClickable:
    def __init__(self, y, x, h, w):
        self.y = y
        self.x = x
        self.h = h
        self.w = w

    def click(self, y, x):
        pass

    def action(self):
        pass


class GlopnetButton(GlopnetClickable):
    def __init__(self, y, x, h, w, name, display_text):
        GlopnetClickable.__init__(self, y, x, h, w)
        self.name = name
        self.original_display_text = display_text
        self.display_text = self.original_display_text
        self.updates_since_click = 0

    def click(self, y, x):
        y_test = (self.y <= y < (self.y + self.h))
        x_test = (self.x <= x < (self.x + self.w))
        if y_test and x_test:
            self.action()

    def action(self):
        self.display_text = "CLICKED!"
        self.updates_since_click = 0

    def draw(self, scr):
        line_format = "{: ^" + str(self.w) + "}"
        text_line = int(self.h / 2)
        for i in range(self.h):
            if i == text_line:
                safe_addstr(scr, self.y + i, self.x, line_format.format(self.display_text[:self.w]))
            else:
                safe_addstr(scr, self.y + i, self.x, line_format.format(" "))

    def update(self):
        if self.updates_since_click >= 2*FPS and self.display_text == "CLICKED!":
            self.display_text = self.original_display_text
        elif self.display_text == "CLICKED!":
            self.updates_since_click += 1


class GlopnetButtonMngr(GlopnetClickable):
    _buttons = {}

    def __init__(self, glopnet):
        GlopnetClickable.__init__(self, 0, 0, 0, 0)
        self.glopnet = glopnet

    def add_button(self, y, x, h, w, name, display_text="X"):
        self._buttons[name] = GlopnetButton(y, x, h, w, name, display_text)

    def rem_button(self, name):
        self._buttons.pop(name)

    def click(self, y, x):
        for b in self._buttons.itervalues():
            b.click(y, x)

    def update(self):
        for b in self._buttons.itervalues():
            b.update()

    def draw(self, scr):
        for b in self._buttons.itervalues():
            b.draw(scr)
            pass


class GlopnetStatusMngr:
    ALIGN_LEFT = 0
    ALIGN_CENTER = 1
    ALIGN_RIGHT = 2

    pulser = {0: '|', 1: '/', 2: '-', 3: '\\'}

    bits = []

    def __init__(self, glopnet, align=ALIGN_LEFT):
        self.glopnet = glopnet
        self.align = align
        self.status_str = "."
        self.input_count = 0
        pass

    def set_status(self, status):
        self.status_str = status

    def add_bit(self, string):
        self.bits.append(string)

    def i_count(self):
        self.input_count += 1

    def draw(self, scr):
        align = {self.ALIGN_LEFT: '<', self.ALIGN_CENTER: '^', self.ALIGN_RIGHT: '>'}

        height, width = scr.getmaxyx()
        status_fmt = "{: " + align[self.align] + str(width-1) + "}"
        self.bits.insert(0, " ")
        self.bits.insert(0, str(self.input_count))
        self.bits.insert(0, " ")
        self.bits.insert(0, self.status_str)
        self.status_str = "".join(self.bits)
        self.bits = []
        self.input_count = 0
        display_string = status_fmt.format(self.status_str)
        display_string += self.pulser[(self.glopnet.lookup['frame'] / (FPS / 4)) % 4]
        safe_addstr(scr, height-1, 0, display_string)


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
