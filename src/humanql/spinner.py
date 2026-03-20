"""Optional progress spinner (runs in a thread until stopped)."""

import sys
import threading
import time
from typing import TextIO

_SPIN_CHARS = ["|", "/", "-", "\\"]


def run_spinner(stderr: TextIO | None = None, interval: float = 0.1) -> "Spinner":
    """Start a spinner on stderr; return a Spinner instance. Call .stop() when done."""
    out = stderr or sys.stderr
    spinner = Spinner(out, interval)
    spinner.start()
    return spinner


class Spinner:
    """Thread-based spinner that writes 'Processing...' with rotating character until stopped."""

    def __init__(self, stream: TextIO, interval: float = 0.1) -> None:
        self._stream = stream
        self._interval = interval
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        """Start the spinner in a background thread."""
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the spinner and clear the line."""
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=1.0)
        self._clear()

    def _run(self) -> None:
        i = 0
        while not self._stop.wait(self._interval):
            try:
                c = _SPIN_CHARS[i % len(_SPIN_CHARS)]
                self._stream.write(f"\r{c} Processing... ")
                self._stream.flush()
            except (OSError, BrokenPipeError):
                break
            i += 1

    def _clear(self) -> None:
        try:
            self._stream.write("\r" + " " * 20 + "\r")
            self._stream.flush()
        except (OSError, BrokenPipeError):
            pass
