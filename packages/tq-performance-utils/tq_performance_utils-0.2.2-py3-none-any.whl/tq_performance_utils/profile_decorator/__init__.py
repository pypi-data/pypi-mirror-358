from .profile_decorator import profiling, Profiler, profile

"""
usage:
with Profiler(internal=0.0001) as p:
    # your code
p.print()  # use p out of context manager scope
# or
# p.output_text()
# p.output_html()
# p.open_in_browser()

@profile()
def func():
    # your code
func()  # output on console

# my profiling decorator
@profiling(enable_profiling: bool = True, interval=0.001, output_mode=Literal['print', 'text', 'html', 'browser'], output_file='./.../profile.html')
def func():
    # your code
func()

"""

__all__ = ['profiling', 'Profiler', 'profile']
