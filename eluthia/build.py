from functools import reduce
import importlib
from importlib.machinery import SourceFileLoader
import os
import tempfile
from textwrap import dedent
from sh import git, pushd, ErrorReturnCode_128
import subprocess
import shutil
import zipapp

def get_builds(folder):
    for package_name in os.listdir(folder):
        yield package_name, SourceFileLoader("machine", os.path.join(folder, package_name, 'build.py')).load_module()

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

def get_temp_folder():
    with tempfile.TemporaryDirectory() as folder:
        return folder

def get_git_version(folder):
    with pushd(folder):
        try:
            return git('rev-list', '--count', 'HEAD').strip() + '-' + git('rev-parse', '--short', 'HEAD').strip()
        except ErrorReturnCode_128:
            pass

def build_app(app):
    return {
        **app,
        'version': app.get('version', get_git_version(app['folder']) or 0),
        'port': 9999,
    }

if __name__ == '__main__':
    apps = SourceFileLoader("apps", os.environ['APPS_PY']).load_module()
    build_folder = os.environ.get('BUILD_FOLDER', get_temp_folder())
    print('Build_folder:', build_folder)

    if os.environ['SKIP_DEB'].lower() != "true":
        os.makedirs(f'{build_folder}/zipapp/', exist_ok=True)
        shutil.copy(f'{build_folder}/../eluthia/archive_script.py', f'{build_folder}/zipapp/__main__.py')

    for package_name, build in get_builds(os.environ['MACHINE_FOLDER']):
        args = (package_name, {
            name: build_app(d)
            for name, d in apps.config.items()
        })
        tree = build.get_package_tree(*args)

        for path, f in flatten_lists(flatten_paths(tree)):
            full_path = (build_folder, package_name, *path)
            f(full_path, *args)
        
        if os.environ['SKIP_DEB'].lower() != "true":
            subprocess.run(["dpkg-deb", "--build", f"{build_folder}/{package_name}"],check=True)
            shutil.copy(f'{build_folder}/{package_name}.deb', f'{build_folder}/zipapp/{package_name}.deb')
    
    if os.environ['SKIP_DEB'].lower() != "true":
        zipapp.create_archive(f'{build_folder}/zipapp',f'{build_folder}/zipapp.pyz','/usr/bin/python3')
        subprocess.run(['chmod','+x',f'{build_folder}/zipapp.pyz'])
