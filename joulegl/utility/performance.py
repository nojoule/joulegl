import os
import time
from typing import Any, Callable

from .file import StatsFileHandler

running_times = []


def track_time(
    _func=None, *, track_recursive: bool = True, app_name: str | None = None
) -> Callable:
    def track_time_inner(func) -> Callable:
        def tracked_func(*args, **kwargs) -> Any:
            global running_times
            start_time = time.perf_counter()
            running_times.append(start_time)
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            time_diff = (
                (end_time - running_times.pop())
                if track_recursive
                else end_time - start_time
            )
            running_times = [start_time + time_diff for start_time in running_times]
            stats = dict()
            stats[func.__name__] = time_diff
            StatsFileHandler(data_path=os.getcwd()).append_statistics(
                stats, app_name=app_name
            )
            return result

        return tracked_func

    if _func is None:
        return track_time_inner
    else:
        return track_time_inner(_func)


class Timed:
    def __init__(self) -> None:
        self.fps: float = 120
        self.current_fps: float = 0
        self.frame_count: int = 0
        self.__to_pause_time: float = 0
        self.__last_frame_count: int = 0
        self.__checked_frame_count: int = -1
        self.__check_time: float = time.perf_counter()
        self.__start_time: float = self.__check_time
        self.__last_time: float = self.__check_time

    def start_time(self) -> None:
        self.__start_time = time.perf_counter()
        self.__to_pause_time -= self.__start_time - self.__last_time

    def check_time(self) -> int:
        self.frame_count += 1

        current_time: float = time.perf_counter()
        if current_time - self.__check_time > 1.0:
            self.current_fps = float(self.frame_count - self.__checked_frame_count) / (
                current_time - self.__check_time
            )
            self.__checked_frame_count = self.frame_count
            self.__check_time = current_time

        pause_for: int = 0

        elapsed_time: float = current_time - self.__start_time
        if elapsed_time > 0.0001:
            self.__to_pause_time += (
                float(self.frame_count - self.__last_frame_count) / self.fps
            ) - elapsed_time
        if self.__to_pause_time > 0.015:
            pause_for = int(self.__to_pause_time * 1000.0)
        elif self.__to_pause_time < -0.1:
            self.__to_pause_time = -0.1
        self.__last_time = current_time
        self.__last_frame_count = self.frame_count

        return pause_for
