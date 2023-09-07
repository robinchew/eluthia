from eluthia.decorators import chmod, copy_folder, file, git_clone, empty_folder
from eluthia.defaults import control
from eluthia.functional import pipe
from eluthia.py_configs import deb822


@chmod(0o644)
@file
def cron_file(full_path, package_name, apps):
    return f'''\
        0 * * * * root python3 /usr/local/bin/eluthia-cron-example/main.py
    '''

def get_package_tree(package_name, apps):
    return {
        'DEBIAN': {
            'control': file(pipe(
                control,
                lambda d: {**d, 'Description': 'example package that sends an email every hour', 'Depends': 'badtrack-secrets'},
                deb822)),
        },
        'usr': {
            'local': {
                'bin': {
                    'eluthia-cron-example': git_clone(apps[package_name]['folder']),
                }
            },
        },
        'etc': {
            'cron.d': {
                'eluthia-cron-example': cron_file,
            }
        }
    }
