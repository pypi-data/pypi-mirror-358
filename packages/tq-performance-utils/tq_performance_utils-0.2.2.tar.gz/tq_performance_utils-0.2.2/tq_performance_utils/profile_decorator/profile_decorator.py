from typing import Literal, Optional
from functools import wraps

from pyinstrument import Profiler, profile
from tq_utils import file_manager


def profiling(enable_profiling: bool = True, interval=0.001,
              output_mode=Literal['print', 'save_text', 'save_html', 'browser'], output_file=Optional[str]):
    """
    :param enable_profiling:
    :param interval:
    :param output_mode:
    :param output_file: if save text or html, you should specify the output file
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if enable_profiling:
                p = Profiler(interval=interval)
                with p:
                    r = func(*args, **kwargs)
                if output_mode == 'print':
                    p.print(unicode=True, color=True)
                elif output_mode == 'save_text' or output_mode == 'save_html':
                    if output_file is None:
                        raise ValueError('if save text or html, you should specify the output file')
                    if output_mode == 'save_text':
                        t = p.output_text(unicode=True, color=True)
                    else:
                        t = p.output_html()
                    with file_manager.FileManager(output_file, 'w') as f:
                        f.write(t)
                elif output_mode == 'browser':
                    p.open_in_browser()
                return r
            else:
                return func(*args, **kwargs)

        return wrapper

    return decorator
