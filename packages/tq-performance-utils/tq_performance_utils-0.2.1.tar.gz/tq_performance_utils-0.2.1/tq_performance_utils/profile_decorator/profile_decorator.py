from typing import Literal

from pyinstrument import Profiler, profile
from functools import wraps


def profiling(enable_profiling: bool = True, interval=0.001, output_mode=Literal['print', 'text', 'html', 'browser']):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if enable_profiling:
                p = Profiler(interval=interval)
                with p:
                    r = func(*args, **kwargs)
                if output_mode == 'print':
                    p.print(unicode=True, color=True)
                elif output_mode == 'text':
                    p.output_text(unicode=True, color=True)
                elif output_mode == 'html':
                    p.output_html()
                elif output_mode == 'browser':
                    p.open_in_browser()
                return r
            else:
                return func(*args, **kwargs)

        return wrapper

    return decorator
