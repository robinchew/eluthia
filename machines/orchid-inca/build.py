from functools import reduce
import importlib
from importlib.machinery import SourceFileLoader
import os
from textwrap import dedent

HERE = os.path.abspath(os.path.dirname(__file__))

def get_builds(folder):
    for package_name in os.listdir(folder):
        try:
            yield package_name, importlib.import_module(package_name + '.build')
        except ModuleNotFoundError:
            pass

def flatten_paths(d, l = ()):
    if type(d) is dict:
        return [
            flatten_paths(v, l + (k,))
            for k, v in d.items()
        ]
    return l, d

def flatten_lists(l):
    return reduce(
        lambda acc, item:
            acc + (flatten_lists(item) if type(item) is list else [item]),
        l,
        [])

if __name__ == '__main__':
    apps = SourceFileLoader("apps", os.environ['APPS_PY']).load_module()
    build_folder = os.environ['BUILD_FOLDER']

    for package_name, build in get_builds(HERE):
        args = (package_name, apps.apps)
        tree = build.get_package_tree(*args)

        for path, f in flatten_lists(flatten_paths(tree)):
            full_path = (build_folder, package_name, *path)
            f(full_path, *args)
