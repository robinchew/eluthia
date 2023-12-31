from functools import wraps
import json
from textwrap import dedent
import os
import shutil
import sh
from sh import pushd, git

HERE = os.path.abspath(os.path.dirname(__file__))

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

def copy_files(from_folder, file_names):
    def copy_to(full_path, *args, **kwargs):
        empty_folder(full_path, *args, **kwargs)
        for name in file_names:
            shutil.copy(
                os.path.join(from_folder, name),
                os.path.join(*full_path + (name,)))
    return copy_to

def git_clone(git_folder):
    def clone_to(full_path_list, *args, **kwargs):
        git.clone(git_folder, os.path.join(*full_path_list))
    return clone_to

def empty_folder(full_path, package_name, apps):
    os.makedirs(os.path.join(*full_path), exist_ok=True)
    return

def build_and_unpack_erlang_release(erlang_project_folder_path):
    def build_and_unpack(full_path, *args, **kwargs):
        empty_folder(full_path, *args, **kwargs)
        with pushd(erlang_project_folder_path):
            sh.make()

        release_name, version = json.loads(sh.escript(
            os.path.join(HERE, 'read_relx_package.escript'),
            os.path.join(erlang_project_folder_path, 'relx.config')))

        release_file_path = os.path.join(erlang_project_folder_path, '_rel', release_name, release_name + '-' + version + '.tar.gz')
        sh.tar('xf', release_file_path, '-C', os.path.join(*full_path))

    return build_and_unpack
