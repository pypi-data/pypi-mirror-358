from abc import ABC
from enum import Enum


class ABCEnvironment(ABC):
    def __init__(self, block_start: int, block_end: int, sealing_status: Enum) -> None:
        self._block_start: int = block_start
        self._block_end: int = block_end
        self._sealing_status: Enum = sealing_status
