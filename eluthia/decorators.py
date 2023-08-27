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
        content = func(full_path, *args, **kwargs)
        with open(os.path.join(*full_path), 'w') as f:
            f.write(dedent(content))
    return wrapper

def copy_folder(from_folder):
    def copy_to(full_path, *args, **kwargs):
        shutil.copytree(
            from_folder,
            os.path.join(*full_path))
    return copy_to

def git_clone(git_folder):
    def clone_to(full_path_list, *args, **kwargs):
        git.clone(git_folder, os.path.join(*full_path_list))
    return clone_to

def empty_folder(full_path, package_name, apps):
    os.makedirs(os.path.join(*full_path), exist_ok=True)
    return

# This is so that I can specify using local files when testing (Replaces where I previously had my path hardcoded).
# For now the environment variable isn't in apps.py because it's not package specific. I could add a generic env field for all packages though
def source_app(folder_path):
    if os.environ.get('APP_SOURCE').lower() == 'local':
        return copy_folder(folder_path)
    return git_clone(folder_path)
