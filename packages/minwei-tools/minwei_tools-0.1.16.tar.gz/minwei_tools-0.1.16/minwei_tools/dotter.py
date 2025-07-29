# A dotter while I'm thinking
from typing import Optional, Iterable
import colorama as cm
import itertools
import threading 
import time
import sys

from minwei_tools.dotter_style import DotStyle

piano = DotStyle.piano
cycle = DotStyle.dot_cycle
slash = DotStyle.slash

class Dotter:
    # A dotter while I'm thinking
    def __init__(self, message: str = "Thinking", delay: float = 0.5, 
                 cycle: list[str] = DotStyle.dot_cycle, 
                 show_timer: bool = False) -> None:
        
        self.lock                                           = threading.Lock()
        
        self.spinner           : Iterable                   = cycle
        self.spinner_index     : int                        = 0
        self.show_timer        : bool                       = show_timer
        self.message           : str                        = message
        self.delay             : float                      = delay
        self.dotter_thread     : Optional[threading.Thread] = None
        self.start_time        : Optional[float]            = None
        self.running           : bool                       = False
        self.condition         : threading.Condition        = threading.Condition(self.lock)
        self.inserted_messages : list[str]                  = []  # Store inserted messages
        self.max_inserted_line : int                        = 0
        
        self.last_draw_time  = 0

    def format_elapsed(self, elapsed: float) -> str:
        if elapsed < 300:
            return f"{elapsed:.1f}s"
        else:
            mins = int(elapsed // 60)
            secs = int(elapsed % 60)
            return f"{mins}m{secs:02d}s"
        
    def dot(self):
        self.start_time = time.time()
        self.last_draw_time = time.time()
        self.last_spinner_update = self.last_draw_time
        while self.running:
            with self.condition:
                now = time.time()
                elapsed = now - self.last_spinner_update

                advance_spinner = False
                wait_time = self.delay - elapsed
                if wait_time > 0:
                    self.condition.wait(timeout=wait_time)
                else:
                    advance_spinner = True

                if not self.running:
                    break

                self._draw(advance_spinner=advance_spinner)
                if advance_spinner:
                    self.last_spinner_update = time.time()
            
    def _draw(self, advance_spinner = False):
        lines_to_clear = 1 + self.max_inserted_line
        for _ in range(lines_to_clear):
            sys.stdout.write("\033[F")  # Move cursor up
            sys.stdout.write("\033[K")  # Clear line
        sys.stdout.flush()
        
        
        elapsed = time.time() - self.start_time
        if advance_spinner:
            self.spinner_index = (self.spinner_index + 1) % len(self.spinner)

        spinner_char = self.spinner[self.spinner_index]
        text = f"{self.message} {spinner_char}"
        if self.show_timer:
            timer_str = f"[{self.format_elapsed(elapsed)}]"
            text = timer_str + ' ' + text

        sys.stdout.write(f"\r{text}\n")
        for msg in self.inserted_messages:
            sys.stdout.write(f"    {cm.Style.DIM}{msg}{cm.Style.RESET_ALL}\n")
        sys.stdout.flush()

        self.max_inserted_line = max(self.max_inserted_line, len(self.inserted_messages))
        
        
    def update_message(self, new_message, delay=0.1):
        with self.condition:
            self.message = new_message
            self.condition.notify()  # 立即刷新
            self.delay = delay
        
    def insert_message(self, new_message: str, max_str : int = 5, prefix = "=>"):
        with self.condition:
            self.inserted_messages.append(prefix + " " + new_message)
            while len(self.inserted_messages) > max_str:
                self.inserted_messages.pop(0)
            self.condition.notify()  # 立即刷新
        
    def __enter__(self):
        self.running = True
        self.dotter_thread = threading.Thread(target=self.dot)
        self.dotter_thread.start()
        return self

    def __exit__(self, *args) -> None:
        with self.condition:
            self.running = False
            self.condition.notify_all()
        self.dotter_thread.join()
        
        
if __name__ == "__main__":
    from time import sleep
    import colorama as cm
    from minwei_tools import DotStyle
    import asyncio

    with Dotter(message="[*] Normal speed", cycle=DotStyle.loading_cycle , delay=0.25, show_timer=0) as d:
        d.insert_message("This is a test message 1")
        sleep(1)
        d.insert_message("This is a test message 2")
        sleep(1)
        d.insert_message("This is a test message 3")
        sleep(1)
        d.update_message("[*] Fast spin", delay=0.05)
        sleep(1)
        d.insert_message("This is a test message 4")
        sleep(1)
        d.insert_message("This is a test message 5")
        sleep(1)        
        d.insert_message("This is a test message 6")
        d.update_message("[*] Slow spin", delay=1)
        for i in range(7, 80):
            d.insert_message(f"This is another message {i}", max_str = 10, prefix = "*")
            sleep(0.05)
        
        d.update_message("[*] Longer msg", delay=0.5)
        while True:
            for i in range(80, 250):
                d.insert_message(f"This is another message {i}", max_str = 20, prefix = f"🚀{cm.Style.RESET_ALL}{cm.Style.BRIGHT}")
                sleep(0.01)       
        d.update_message("[*] Short msg", delay=0.5)
            
        for i in range(250, 500):
            d.insert_message(f"This is another message {i}", max_str = 3, prefix = f"{cm.Style.RESET_ALL}{cm.Style.BRIGHT}🚀{cm.Style.RESET_ALL}{cm.Style.DIM}")
            sleep(0.01)            
            