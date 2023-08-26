from functools import reduce

def pipe(*functions):
    return lambda *args: reduce(
        lambda previous, next_: next_(previous),
        functions[1:],
        functions[0](*args))
