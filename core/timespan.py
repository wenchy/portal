import datetime
import time
from typing import Callable


class Timespan(object):
    """
    Timespan is used to measure time consuming of a block of code.

    e.g.:

    ```
    with Timespan(lambda duration: print(f"time consuming: {duration}")):
        time.sleep(1)
    ```

    output:
    ```
    time consuming: 0:00:01.000990
    ```
    """

    def __init__(self, on_exit: Callable[[datetime.timedelta], None]):
        self._on_exit = on_exit

    def __enter__(self):
        self._enter_time = time.time()

    def __exit__(self, *args):
        delta = time.time() - self._enter_time
        duration = datetime.timedelta(seconds=delta)
        self._on_exit(duration)


if __name__ == "__main__":
    with Timespan(lambda duration: print(f"time consuming: {duration}")):
        time.sleep(1)
