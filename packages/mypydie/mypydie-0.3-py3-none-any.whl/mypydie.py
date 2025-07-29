import sys
import time
import inspect
from pprint import pprint
from typing import Any, Union

def dier(*args: Any, exit: Union[bool, int] = False, label: str = "", sleep_before_exit: float = 0.0) -> None:
    caller = inspect.stack()[1]
    print(f"[DIER] Called from {caller.filename}:{caller.lineno}")

    if label:
        print(f"=== {label} ===")

    for msg in args:
        pprint(msg)

    if sleep_before_exit > 0:
        time.sleep(sleep_before_exit)

    if exit is False or exit == 0:
        return
    sys.exit(exit if isinstance(exit, int) else 1)
