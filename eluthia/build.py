from functools import reduce
from hashlib import md5
import importlib
from importlib.machinery import SourceFileLoader
import os
import tempfile
from textwrap import dedent
from sh import git, pushd, ErrorReturnCode_128
import subprocess
import shutil
import zipapp
import sys

from constants import GIT
import canonical_json

def get_builds(folder):
    for package_name in os.listdir(folder):
        build_py_path = os.path.abspath(os.path.join(folder, package_name, 'build.py'))
        yield package_name, build_py_path, SourceFileLoader("build_file", build_py_path).load_module()

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
        return git('rev-list', '--count', 'HEAD').strip() + '-' + git('rev-parse', '--short', 'HEAD').strip()

def get_eluthia_version_of(file):
    # Need to set GIT_PAGER as blank, or else the output will be something like:
    #
    #   \x1b[?1h\x1b=\r4d735de\x1b[m\n\r\x1b[K\x1b[?1l\x1b>'
    #
    # instead of just:
    #
    #   4d735de
    commit_id = git('log', '-n', 1, '--format=%h', '--', file, _env={'GIT_PAGER': ''}).strip()

    commit_number = git('rev-list', '--count', commit_id).strip()
    return commit_number + '-' + commit_id

def determine_version(build_py_path, app):
    if 'version' in app:
        return app['version']

    if app['folder_type'] is GIT:
        return get_git_version(app['folder'])

    return get_eluthia_version_of(build_py_path)

def build_app(build_py_path, app):
    return {
        **app,
        'version': determine_version(build_py_path, app),
        'app_config_version': md5(canonical_json.dumps(app).encode()).hexdigest(),
        'port': 9999,
    }

if __name__ == '__main__':
    apps = SourceFileLoader("apps", os.environ['APPS_PY']).load_module()
    build_folder = os.environ.get('BUILD_FOLDER', get_temp_folder())
    print('Build_folder:', build_folder)

    skip_deb = 'SKIP_DEB' in os.environ

    # Prepare zipapp directory
    os.makedirs(f'{build_folder}/zipapp/', exist_ok=True)
    shutil.copy(f'{os.path.abspath(os.path.dirname(__file__))}/zipapp_script.py', f'{build_folder}/zipapp/__main__.py')

    for package_name, build_py_path, build in get_builds(os.environ['MACHINE_FOLDER']):
        all_apps_config = {
            name: build_app(build_py_path, d)
            for name, d in apps.config.items()
        }
        app = all_apps_config[package_name]
        tree = build.get_package_tree(package_name, all_apps_config)
        full_package_name = '-'.join((package_name, app['version'], app['app_config_version']))

        for path, f in flatten_lists(flatten_paths(tree)):
            full_path = (build_folder, full_package_name, *path)
            f(full_path, package_name, all_apps_config)

        if not skip_deb: # Build debian packages and put in zipapp directory
            subprocess.run(["dpkg-deb", "--build", f"{build_folder}/{full_package_name}"],check=True)
            shutil.copy(f'{build_folder}/{full_package_name}.deb', f'{build_folder}/zipapp/')

    if skip_deb:
        print("debian package creation was skipped, so zip package was skipped too.")
        sys.exit(1)
    else:
        # Create executable archive
        zipapp.create_archive(f'{build_folder}/zipapp', f'{build_folder}/zipapp.pyz', '/usr/bin/python3')
        subprocess.run(['chmod', '+x', f'{build_folder}/zipapp.pyz'])
