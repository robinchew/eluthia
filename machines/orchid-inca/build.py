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

def walk(tree, args):
    if type(tree) is dict:
        return {
            k: walk(v, args)
            for k, v in tree.items()
        }
    if callable(tree):
        return dedent(tree(*args))
    return tree

def flatten_paths(d, l = ()):
    if type(d) is dict:
        return [
            flatten_paths(v, l + (k,))
            for k, v in d.items()
        ]
    return l

if __name__ == '__main__':
    apps = SourceFileLoader("apps", os.environ['APPS_PY']).load_module()

    for package_name, build in get_builds():
        args = (package_name, apps.apps)
        tree = build.get_package_tree(*args)
        from pprint import pprint
        pprint(walk(tree, args), indent=4)
        pprint(flatten_paths(walk(tree, args)), indent=4)
