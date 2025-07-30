from datetime import datetime, timezone
from math import floor


class Time:

    def __init__(self, mode="now"):

        mode = mode.lower()

        if mode == "now":
            timestamp = datetime.now(timezone.utc).timestamp()
            self.__time_sec: int = floor(timestamp)
            self.__time_micro: float = timestamp - self.__time_sec
        elif mode == "zero":
            self.__time_sec: int = 0
            self.__time_micro: float = 0.0
        else:
            raise ValueError(f"Unsupported mode: {mode}")

    def __str__(self) -> str:
        return f"{self.__time_sec}.{floor(self.__time_micro * 1e6):06d}"


__all__ = ["Time"]
