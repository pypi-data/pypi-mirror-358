from enum import Enum
from functools import wraps
from typing import Any, Callable

from nqs_sdk.environment import ABCEnvironment


def check_sealing_status(permitted_status: Enum) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self: ABCEnvironment, *args: Any, **kwargs: Any) -> Any:
            if self._sealing_status.value != permitted_status.value:
                raise ValueError(f"Function not allowed in {self._sealing_status.name} state...")
            return func(self, *args, **kwargs)

        return wrapper

    return decorator
