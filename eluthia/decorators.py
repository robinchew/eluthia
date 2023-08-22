from functools import wraps
from textwrap import dedent
import os
import shutil
from sh import git

def chmod(octal):
    def decorate(func):
        @wraps(func)
        def wrapper(full_path, *args, **kwargs):
            res = func(full_path, *args, **kwargs)
            os.chmod(os.path.join(*full_path), octal)
            return res
        return wrapper
    return decorate

def file(func):
    @wraps(func)
    def wrapper(full_path, *args, **kwargs):
        os.makedirs(os.path.join(*full_path[0:-1]), exist_ok=True)
        content = func(*args, **kwargs)
        with open(os.path.join(*full_path), 'w') as f:
            f.write(dedent(content))
    return wrapper

def copy_folder(from_folder):
    def copy_to(full_path, *args):
        shutil.copytree(
            from_folder,
            os.path.join(*full_path))
    return copy_to

def git_clone(git_folder):
    def clone_to(full_path_list, *args):
        git.clone(git_folder, os.path.join(*full_path_list))
    return clone_to
