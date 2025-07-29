import requests
import time
from pathlib import Path
import sys

# Define color codes for terminal (ANSI escape codes)
class Colors:
    RESET = "\033[0m"
    GREEN = "\033[92m"
    BLUE = "\033[94m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    LIGHT_GREEN = "\033[92m"
    LIGHT_BLUE = "\033[94m"
    LIGHT_RED = "\033[91m"
    LIGHT_YELLOW = "\033[93m"
    LIGHT_MAGENTA = "\033[95m"
    LIGHT_CYAN = "\033[96m"

    # List of all available colors for easy access
    ALL_COLORS = [
        GREEN, BLUE, RED, YELLOW, MAGENTA, CYAN, WHITE,
        LIGHT_GREEN, LIGHT_BLUE, LIGHT_RED, LIGHT_YELLOW, LIGHT_MAGENTA, LIGHT_CYAN
    ]

class ProgressBar:
    def __init__(self, total, prefix='', length=40, fill='━', empty=' ', print_end="\r", 
                 download_color=Colors.GREEN, complete_color=Colors.BLUE):
        """
        Initializes the progress bar.

        Parameters:
            total (int): Total number of bytes to download.
            prefix (str): Prefix for the progress bar.
            length (int): Length of the progress bar.
            fill (str): Character to fill the progress bar.
            empty (str): Character to represent empty space in the progress bar.
            print_end (str): Ending character for printing.
            download_color (str): Color code for progress bar during download.
            complete_color (str): Color code for progress bar when download is complete.
        """
        self.total = total
        self.prefix = prefix
        self.length = length
        self.fill = fill
        self.empty = empty
        self.print_end = print_end
        self.download_color = download_color
        self.complete_color = complete_color
        self.start_time = time.time()
        self.downloaded = 0

    def update(self, downloaded):
        self.downloaded = downloaded
        percent = ("{0:.1f}").format(100 * (self.downloaded / float(self.total)))
        filled_length = int(self.length * self.downloaded // self.total)
        bar = self.fill * filled_length + self.empty * (self.length - filled_length)

        # Calculate current file size and total file size
        current_size = self.format_size(self.downloaded)
        total_size = self.format_size(self.total)

        # Set color based on progress
        if self.downloaded == self.total:
            color = self.complete_color  # Completed color
        else:
            color = self.download_color  # Downloading color

        # Print the progress bar with color, percentage, and file size
        sys.stdout.write(f'\r{self.prefix} {color}{bar}{Colors.RESET} {percent}% • {current_size}/{total_size}')
        sys.stdout.flush()

        if self.downloaded == self.total:
            sys.stdout.write(self.print_end)
            sys.stdout.flush()

    def format_size(self, size_in_bytes):
        """Format the size in a human-readable format (e.g., KB, MB, GB)."""
        for unit in ['B', 'KiB', 'MiB', 'GiB', 'TiB']:
            if size_in_bytes < 1024:
                return f"{size_in_bytes:.1f} {unit}"
            size_in_bytes /= 1024

