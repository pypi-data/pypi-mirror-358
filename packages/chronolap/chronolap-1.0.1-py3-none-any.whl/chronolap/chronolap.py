import time
from typing import List, Optional
import logging

class Lap:
    def __init__(self, name: str, duration: float, timestamp: float):
        self.name = name
        self.duration = duration
        self.timestamp = timestamp

    def __str__(self):
        return f"{self.name}: {self.duration * 1000:.0f} ms (At {self.timestamp * 1000:.0f} ms)"


class ChronolapTimer:
    def __init__(self, logger: Optional[logging.Logger] = None):
        self._start_time = None
        self._laps: List[Lap] = []
        self._last_lap_time = None
        self._is_running = False
        self.logger = logger

    def start(self):
        self._start_time = time.perf_counter()
        self._last_lap_time = self._start_time
        self._is_running = True

    def stop(self):
        self._is_running = False

    def reset(self):
        self._laps.clear()
        self._start_time = None
        self._last_lap_time = None
        self._is_running = False

    def lap(self, name: Optional[str] = None):
        now = time.perf_counter()
        duration = now - self._last_lap_time
        lap_name = name or f"Lap {len(self._laps) + 1}"
        lap = Lap(lap_name, duration, now - self._start_time)
        self._laps.append(lap)
        self._last_lap_time = now

        if self.logger:
            self.logger.info(f"Lap recorded: {lap}")

    def measure(self, func, name: Optional[str] = None):
        start = time.perf_counter()
        result = func()
        end = time.perf_counter()
        lap_name = name or f"Measured {len(self._laps) + 1}"
        lap = Lap(lap_name, end - start, end - self._start_time)
        self._laps.append(lap)

        if self.logger:
            self.logger.info(f"Measured lap: {lap}")
        return result

    @property
    def laps(self) -> List[Lap]:
        return self._laps.copy()

    @property
    def total_lap_time(self) -> float:
        return sum(lap.duration for lap in self._laps)

    @property
    def is_running(self) -> bool:
        return self._is_running
