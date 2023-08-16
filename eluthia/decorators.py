from functools import wraps
import os

def file(func):
    @wraps(func)
    def wrapper(full_path, *args, **kwargs):
        os.makedirs(os.path.join(*full_path[0:-1]), exist_ok=True)
        content = func(*args, **kwargs)
        with open(os.path.join(*full_path), 'w') as f:
            f.write(content)
    return wrapper
