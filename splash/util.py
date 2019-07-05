from contextlib import contextmanager
from timeit import default_timer

@contextmanager
def context_timer():
    start = default_timer()
    elapser = lambda: default_timer() - start
    yield lambda: elapser()
    end = default_timer()
    elapser = lambda: end - start
