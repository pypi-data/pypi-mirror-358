from typing import Optional, Iterable
from .dotter_style import DotStyle

import colorama as cm
import asyncio
import time
import sys

from minwei_tools.dotter import piano, slash  # Importing from the dotter module


class AsyncDotter:
    def __init__(self, message: str = "Thinking", delay: float = 0.5, 
                 cycle: list[str] = DotStyle.dot_cycle, 
                 show_timer: bool = False) -> None:

        self.spinner: Iterable = cycle
        self.spinner_index: int = 0
        self.show_timer: bool = show_timer
        self.message: str = message
        self.delay: float = delay
        self.dotter_task: Optional[asyncio.Task] = None
        self.start_time: Optional[float] = None
        self.running: bool = False
        self.condition: asyncio.Condition = asyncio.Condition()
        self.inserted_messages: list[str] = []
        self.max_inserted_line: int = 0

    def format_elapsed(self, elapsed: float) -> str:
        if elapsed < 300:
            return f"{elapsed:.1f}s"
        else:
            mins = int(elapsed // 60)
            secs = int(elapsed % 60)
            return f"{mins}m{secs:02d}s"

    async def dot(self):
        self.start_time = time.time()
        self.last_spinner_update = time.time()
        while self.running:
            async with self.condition:
                now = time.time()
                elapsed = now - self.last_spinner_update
                if elapsed < self.delay:
                    try:
                        await asyncio.wait_for(self.condition.wait(), timeout=self.delay - elapsed)
                    except asyncio.TimeoutError:
                        pass

                if not self.running:
                    break

                await self._draw(advance_spinner=(elapsed >= self.delay))
                if elapsed >= self.delay:
                    self.last_spinner_update = time.time()

    async def _draw(self, advance_spinner=False):
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

    async def update_message(self, new_message: str, delay: float = 0.1):
        async with self.condition:
            self.message = new_message
            self.delay = delay
            self.condition.notify()

    async def insert_message(self, new_message: str, max_str: int = 5, prefix="=>"):
        async with self.condition:
            self.inserted_messages.append(prefix + " " + new_message)
            while len(self.inserted_messages) > max_str:
                self.inserted_messages.pop(0)
            self.condition.notify()

    async def __aenter__(self):
        self.running = True
        self.dotter_task = asyncio.create_task(self.dot())
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self.running = False
        async with self.condition:
            self.condition.notify()
        if self.dotter_task:
            await self.dotter_task

        
        
if __name__ == "__main__":
    import asyncio

    async def main():
        async with AsyncDotter("Loading", show_timer=False, cycle=DotStyle.dot_cycle, delay=0.1) as d:
            await d.insert_message("This is a test message -1")
            await d.insert_message("This is a test message 0")
            await d.insert_message("This is a test message 1")
            await asyncio.sleep(1)
            await d.insert_message("This is a test message 2")
            await asyncio.sleep(1)
            await d.insert_message("This is a test message 3")
            await asyncio.sleep(1)
            await d.update_message("[*] Fast Spin", delay=0.05)
            await d.insert_message("This is a test message 4")
            await asyncio.sleep(1)
            await d.insert_message("This is a test message 5")
            await asyncio.sleep(1)
            await d.insert_message("This is a test message 6")
            await asyncio.sleep(1)
            await d.insert_message("This is a test message 7")
            
            for i in range(7, 80):
                await d.insert_message(f"This is another message {i}", max_str = 10, prefix = "*")
                await asyncio.sleep(0.05)
            await d.update_message("[*] Slow Spin", delay=0.5)
            for i in range(80, 800):
                await d.insert_message(f"This is another message {i}", max_str = 20, prefix = f"🚀{cm.Style.RESET_ALL}{cm.Style.BRIGHT}")
                await asyncio.sleep(0.01)       

    asyncio.run(main())