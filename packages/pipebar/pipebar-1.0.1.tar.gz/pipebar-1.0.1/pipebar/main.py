import time
import sys
import os
import re

# ANSI colors
green = '\033[38;2;115;230;100m'
cyan = '\033[38;2;128;255;234m'
gray = '\033[38;2;95;105;110m'
red = '\033[38;2;235;64;52m'
white = '\033[97m'
end = '\033[0m'

_ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

def get_terminal_width():
    try:
        return os.get_terminal_size().columns
    except OSError:
        return 70

class ProgressBar:
    def __init__(self, iterable=None, total=None, unit='it', scale=1, bar_length=None):
        """
        Initialize the progress bar.

        :param iterable: Iterable to wrap (optional).
        :param total: Total number of units (optional).
        :param unit: Unit label for display (e.g. 'it' for items, 'MB' for megabytes).
        :param scale: Scaling factor to convert raw units (e.g. 1024*1024 to convert bytes to MB).
        :param bar_length: Length of the bar in characters (auto-calculated if None).
        """

        self.iterable = iterable
        if total is not None:
            self.total = total
        elif iterable is not None and hasattr(iterable, '__len__'):
            self.total = len(iterable)
        else:
            self.total = None

        self._finished = False
        self.unit = unit
        self.scale = scale
        self.bar_length = bar_length if bar_length is not None else get_terminal_width() - 45
        self.current = 0
        self.start_time = time.time()
        self.last_update = self.start_time
        self.last_speed = 0
        self.last_eta = 0

    def __iter__(self):
        """Support iteration over the wrapped iterable."""
        if self.iterable is None:
            raise ValueError("No iterable provided")
        for item in self.iterable:
            yield item
            self.update(1)
        self.final_update()

    def update(self, n=1):
        """Advance the progress by n units."""
        self.current += n
        current_time = time.time()
        # Refresh every 0.1s or upon completion
        if current_time - self.last_update >= 0.1 or (self.total and self.current >= self.total):
            elapsed_time = current_time - self.start_time
            if elapsed_time > 0:
                self.last_speed = self.current / elapsed_time  # Скорость в единицах/с
                if self.total:
                    self.last_eta = (self.total - self.current) / self.last_speed if self.last_speed > 0 else 0
            self.last_update = current_time
            self.display_bar()

    def display_bar(self):
        """Render the progress bar to the terminal."""
        if self.total:
            progress = int(self.bar_length * self.current / self.total)
            remaining = self.bar_length - progress
            bar_str = f'{green}{"━" * progress}{gray}{"━" * remaining}{end}'

            current_display = self.current / self.scale
            total_display = self.total / self.scale
            speed_display = self.last_speed / self.scale
            eta_minutes = int(self.last_eta // 60)
            eta_seconds = int(self.last_eta % 60)

            size_str = f'{green}{current_display:.1f}/{total_display:.1f} {self.unit}{end}'
            speed_str = f'{red}{speed_display:.1f} {self.unit}/s{end}'
            eta_str = f'eta {cyan}{eta_minutes:02d}:{eta_seconds:02d}{end}'

            print(f'\r\033[K   {bar_str} {size_str} {speed_str} {eta_str}', end='', flush=True)

    def final_update(self):
        """Final progress update at completion."""
        if self._finished:
            return
        if self.total is not None and self.current < self.total:
            self.current = self.total
            self.display_bar()
        print()
        self._finished = True

    def __enter__(self):
        """Enter context manager."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """On context exit, do final update if no exception."""
        if exc_type is None:
            self.final_update()