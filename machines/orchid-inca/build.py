from functools import reduce
import importlib
from importlib.machinery import SourceFileLoader
import os
from textwrap import dedent

def get_builds():
    for package_name in os.listdir():
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

    for package_name, build in get_builds():
        args = (package_name, apps.apps)
        tree = build.get_package_tree(*args)

        for path, content in flatten_lists(flatten_paths(tree)):
            full_path = (build_folder, package_name, *path)
            os.makedirs(os.path.join(*full_path[0:-1]), exist_ok=True)
            with open(os.path.join(*full_path), 'w') as f:
                f.write(content(*args))
