from functools import reduce

def is_iterable(value):
    return type(value) in (tuple, list)

def pipe(*functions):
    return lambda *args: reduce(
        lambda previous, next_: next_(previous),
        functions[1:],
        functions[0](*args))

def replace_key_value_everywhere(replacement_key, replacement_value, data):
    if type(data) is dict:
        return {
            key: replacement_value if key == replacement_key else replace_key_value_everywhere(replacement_key, replacement_value, value)
            for key, value in data.items()
        }
    if is_iterable(data):
        return type(data)(replace_key_value_everywhere(replacement_key, replacement_value, value) for value in data)
    return data
