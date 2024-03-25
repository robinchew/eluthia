from datetime import datetime
from functools import partial, reduce
from hashlib import md5
import importlib
from importlib.machinery import SourceFileLoader
import json
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

NO_CHANGE = False
CHANGED = True
VALID_DEBIAN_PACKAGE_NAME = re.compile('^[a-z0-9-+.]+$')

def list_dir_full_path(path):
    for file_name in os.listdir(path):
        yield os.path.join(path, file_name)

def now_version():
    return datetime.now().strftime('%Y-%m-%d_%H%M')

def extract_app_config(bundle, file_name, app_config):
    new_app_config = getattr(bundle, 'update_app_config', lambda ac: ac)(app_config)
    actual_md5_version = md5(canonical_json.dumps(new_app_config).encode()).hexdigest()
    splitted = file_name.split('_')

    app_name, num_version, md5_version = {
        1: lambda: (splitted[0], 0, None),
        3: lambda: (splitted[0], int(splitted[1]), splitted[2]),
    }[len(splitted)]()

    return (
        app_name,
        # Increment num_version when md5 version changes from filename
        num_version + 1 if md5_version != actual_md5_version else num_version,
        actual_md5_version,
        new_app_config,
        md5_version != actual_md5_version, # config has changed
    )

assert extract_app_config(None, 'file-saver', {'abc': 1}) == ('file-saver', 1, '35aa17374cf016b32a3e3aa23caa0e5e', {'abc': 1}, CHANGED)
assert extract_app_config(None, 'file-saver_11_35aa17374cf016b32a3e3aa23caa0e5e', {'abc': 1}) == ('file-saver', 11, '35aa17374cf016b32a3e3aa23caa0e5e', {'abc': 1}, NO_CHANGE)
assert extract_app_config(None, 'file-saver_6_abc123', {'abc': 1}) == ('file-saver', 7, '35aa17374cf016b32a3e3aa23caa0e5e', {'abc': 1}, CHANGED)

def extract_app_config_from_path(bundle, app_path):
    file_name = os.path.basename(app_path).split('.', 1)[0]
    app = SourceFileLoader(file_name, app_path).load_module()
    return extract_app_config(bundle, file_name, app.app_config)

def try_different_args(f, different_args):
    e_list = []
    for args in different_args:
        try:
            return f(*args)
        except TypeError as e:
            if 'positional arguments' in str(e):
                e_list.append(e)
            else:
                raise

    for e in e_list:
        print(e)
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

def create_clean_git_folder(source_git_folder):
    def create(app):
        clean_git_folder = app['clean_git_folder']
        makedirs(clean_git_folder)
        git.clone(source_git_folder, clean_git_folder)
        return app
    return create

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

def build(find_git_path, apps_config, machines, machine_name):
    verify_apps_config(apps_config)

    build_folder = os.environ.get('BUILD_FOLDER', get_temp_folder())
    print('Build folder:', build_folder)

    skip_deb = 'SKIP_DEB' in os.environ

    # Prepare zipapp directory
    makedirs(f'{build_folder}/zipapp/')
    shutil.copy(f'{os.path.abspath(os.path.dirname(__file__))}/zipapp_script.py', f'{build_folder}/zipapp/__main__.py')

    all_machines = {
        mach_name: build_machine_config(d)
        for mach_name, d in machines.items()
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
                'clean_git_folder': os.path.join(build_folder, 'clean_git', package_name),
            },
            create_clean_git_folder(find_git_path(package_name)),
            lambda app : {
                **app,
                '_app_folder': app['clean_git_folder'],
            },
            lambda app: {
                **app,
                'build_module_path': os.path.abspath(os.path.join(app['_app_folder'], app.get('build_module_relpath', 'build.py')))
            },
            lambda app: {
                **app,
                'build_module': load_module_from_path(package_name, app['build_module_path']),
                'version': get_git_version(find_git_path(package_name)),
            },
        )(initial_config)
        for package_name, initial_config in apps_config.items()
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

def iter_bundled_app_configs(bundle, apps_folder):
    for file_name in (path for path in list_dir_full_path(apps_folder) if os.path.isfile(path) and path.endswith('.py')):
        app_path = os.path.join(apps_folder, file_name)
        app_name, version_num, version_md5, app_config, config_changed = extract_app_config_from_path(bundle, app_path)

        if config_changed:
            new_config_name_without_extension = app_name + '_' + str(version_num) + '_' + version_md5
            new_file_path_no_ext = os.path.join(apps_folder, new_config_name_without_extension)

            with open(new_file_path_no_ext + '.py', 'w') as f, \
                 open(os.path.join(app_path)) as fr:
                f.write(fr.read())

            with open(new_file_path_no_ext + '.json', 'w') as f:
                json.dump(app_config, f, indent=4)

            # md5 in the filename no longer matches the containing app_config,
            # so delete file after the new file has been created above.
            print(f"'{app_path}' has been deleted! {new_file_path_no_ext}.(py/json) created.")
            os.remove(app_path)

        yield (app_name, app_config)

def build_apps_config(env):
    if 'APPS_PY' in env:
        app_name = os.path.basename(os.environ['APPS_PY']).rsplit('.', 1)[0]
        apps = SourceFileLoader(app_name, os.environ['APPS_PY']).load_module()
        return apps.config, apps.machines, env['MACHINE']
    elif 'APPS_BUNDLE' in env:
        bundle_root = env['APPS_BUNDLE']
        bundle_name = os.path.basename(env['APPS_BUNDLE'])
        apps_folder = os.path.join(bundle_root, 'apps')
        bundle = SourceFileLoader(bundle_name + '_bundle', os.path.join(bundle_root, 'bundle.py')).load_module()
        machine = SourceFileLoader(bundle_name + '_machine', os.path.join(bundle_root, 'machine.py')).load_module()

        return (
            dict(iter_bundled_app_configs(bundle, apps_folder)),
            {machine.name: {'ports_map': machine.ports_map}},
            machine.name,
        )
    raise Exception('Cannot determine apps_config')

if __name__ == '__main__':
    with open(os.environ['GIT_LOOKUP']) as f:
        git_lookup = json.load(f)
    build(git_lookup.get, *build_apps_config(os.environ))
