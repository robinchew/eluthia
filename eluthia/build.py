from datetime import datetime
from functools import reduce
from hashlib import md5
import importlib
from importlib.machinery import SourceFileLoader
import os
import tempfile
from textwrap import dedent
import re
from sh import git, pushd, ErrorReturnCode_128

from operator import itemgetter
from pprint import pprint
import subprocess
import zipapp
import shutil
import sys
from types import SimpleNamespace

from constants import GIT, UNSET
import canonical_json
from functional import pipe

VALID_DEBIAN_PACKAGE_NAME = re.compile('^[a-z0-9-+.]+$')

def try_different_args(f, different_args):
    for args in different_args:
        try:
            return f(*args)
        except TypeError:
            pass
    raise Exception("Could not execute '{}' with valid arguments".format(f.__name__))

def load_module_from_path(package_name, build_py_path):
    return SourceFileLoader(package_name + "_build_module", build_py_path).load_module()

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
    return git('rev-list', '--count', 'HEAD', _cwd=folder).strip() + '-' + git('rev-parse', '--short', 'HEAD', _cwd=folder).strip()

def get_eluthia_version_of(file):
    # Need to set GIT_PAGER as blank, or else the output will be something like:
    #
    #   \x1b[?1h\x1b=\r4d735de\x1b[m\n\r\x1b[K\x1b[?1l\x1b>'
    #
    # instead of just:
    #
    #   4d735de
    commit_id = git('log', '-n', 1, '--format=%h', '--', file, _env={'GIT_PAGER': ''}, _cwd=os.path.dirname(file)).strip()

    commit_number = git('rev-list', '--count', commit_id, _cwd=os.path.dirname(file)).strip()
    return commit_number + '-' + commit_id

def determine_version(build_py_path, app):
    if 'version' in app:
        return app['version']

    if app['folder_type'] is GIT:
        return get_git_version(app['folder'])

    return get_eluthia_version_of(build_py_path)

def create_clean_git_folder(app):
    clean_git_folder = app['clean_git_folder']
    if clean_git_folder:
        makedirs(clean_git_folder)
        git.clone(app['folder'], clean_git_folder)
    return app

def validate_app(app):
    assert 'build_module_path' not in app, 'Apps config should not set \'build_module_path\' because it is only set by eluthia/build.py. Use \'build_module_relpath\' instead.'
    if 'build_module_relpath' in app:
        assert app['build_module_relpath'][0] not in ('.', '/'), 'Relative path cannot start with . or /'
    return app

def print_app(app):
    print(app)
    return app

def makedirs(path):
    os.makedirs(path, exist_ok=True)
    return path

def verify_apps_config(config):
    for key in config:
        assert VALID_DEBIAN_PACKAGE_NAME.match(key), f"'{key}' contains invalid characters for a Debian package name"

    unset_tuple = tuple(
        path_tuple
        for path_tuple, value in flatten_lists(flatten_paths(config))
        if value is UNSET)

    if unset_tuple:
        pprint(unset_tuple)
        raise Exception('config has UNSET values')

def validate_machine(machine):
    port_numbers = set(map(itemgetter(0), machine['ports_map']))
    port_names = set(map(itemgetter(1), machine['ports_map']))

    assert len(port_numbers) == len(port_names) == len(machine['ports_map']), 'All port numbers, and all port names  must be unique'

    return machine

def build_machine_config(machine):
    return {
        **validate_machine(machine),
        'port_by_name': {
            port_name: port_num
            for port_num, port_name in machine['ports_map']
        }
    }

if __name__ == '__main__':
    app_name = os.path.basename(os.environ['APPS_PY']).rsplit('.', 1)[0]
    apps = SourceFileLoader(app_name, os.environ['APPS_PY']).load_module()
    verify_apps_config(apps.config)

    build_folder = os.environ.get('BUILD_FOLDER', get_temp_folder())
    print('Build_folder:', build_folder)

    skip_deb = 'SKIP_DEB' in os.environ

    # Prepare zipapp directory
    makedirs(f'{build_folder}/zipapp/')
    shutil.copy(f'{os.path.abspath(os.path.dirname(__file__))}/zipapp_script.py', f'{build_folder}/zipapp/__main__.py')

    machine_name = os.environ['MACHINE']

    all_machines = {
        machine_name: build_machine_config(d)
        for machine_name, d in apps.machines.items()
    }

    assert machine_name in all_machines, f"{os.environ['MACHINE']} does not exist in machines in config"

    all_apps_config = {
        package_name: pipe(
            validate_app,
            lambda app: {
                **app,
                'app_config_version': md5(canonical_json.dumps(app).encode()).hexdigest(),
                'port': 9999,
            },
            lambda app: {
                'package_name': package_name,
                **app,
                'clean_git_folder': os.path.join(build_folder, 'clean_git', package_name) if app['folder_type'] is GIT else None,
            },
            create_clean_git_folder,
            lambda app : {
                **app,
                '_app_folder': app['clean_git_folder'] or app['folder'],
            },
            lambda app: {
                **app,
                'build_module_path': os.path.abspath(os.path.join(app['_app_folder'], app.get('build_module_relpath', 'build.py')))
            },
            lambda app: {
                **app,
                'build_module': load_module_from_path(package_name, app['build_module_path']),
                'version': determine_version(app['build_module_path'], app),
            },
        )(initial_config)
        for package_name, initial_config in apps.config.items()
    }
    for package_name, app in all_apps_config.items():
        build = app['build_module']
        different_args = (
            (package_name, all_apps_config, machine_name, all_machines),
            (package_name, all_apps_config),
        )
        tree = try_different_args(build.get_package_tree, different_args)
        full_package_name = '-'.join((package_name, app['version'], app['app_config_version']))

        def abs_path(*path):
            d = tree
            for name in path:
                d = d[name]
            return '/' + os.path.join(*path)

        def build_path(*path):
            d = tree
            for name in path:
                d = d[name]
            return os.path.join(build_folder, full_package_name, *path)

        path_obj = SimpleNamespace(abs=abs_path, of_build=build_path)

        for path, f in flatten_lists(flatten_paths(tree)):
            full_path = (build_folder, full_package_name, *path)
            try_different_args(f, [
                (full_path, path_obj, package_name, all_apps_config, machine_name, all_machines),
                *((full_path,) + args for args in different_args)
            ])

        if not skip_deb: # Build debian packages and put in zipapp directory
            subprocess.run(["dpkg-deb", "--build", f"{build_folder}/{full_package_name}"],check=True)
            shutil.copy(f'{build_folder}/{full_package_name}.deb', f'{build_folder}/zipapp/')

    if skip_deb:
        print("debian package creation was skipped, so zip package was skipped too.")
        sys.exit(1)
    else:
        # Create executable archive
        bundle_version = md5(''.join(app['app_config_version'] for app in all_apps_config.values()).encode()).hexdigest()
        file_name = 'install-' + bundle_version + '-' + datetime.now().strftime('%Y-%m-%d_%H%M') + '.pyz'
        zipapp.create_archive(f'{build_folder}/zipapp', f'{build_folder}/{file_name}', '/usr/bin/python3')
        subprocess.run(['chmod', '+x', f'{build_folder}/{file_name}'])
