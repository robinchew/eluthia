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

def overlay(v1, v2):
    if v1 == v2:
        return v1
    if v2 is None:
        return v1
    if type(v1) is dict:
        missed_keys = set(v2).difference(v1)
        assert not missed_keys, f'Overlayed non-existent key(s) {missed_keys}'
        return {
            key: overlay(value, v2.get(key, None))
            for key, value in v1.items()
        }
    # Not supporting iterables
    return v2
