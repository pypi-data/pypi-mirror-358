from math import floor


class Period:

    def __init__(self):
        self.__period_sec: int = 0
        self.__period_micro: float = 0.0

    def __str__(self) -> str:
        return f"{self.__period_sec}.{floor(self.__period_micro * 1e-6):06d}"


__all__ = ["Period"]
