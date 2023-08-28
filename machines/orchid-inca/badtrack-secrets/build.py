from eluthia.decorators import chmod, copy_folder, file, git_clone, empty_folder
from eluthia.defaults import control
from eluthia.functional import pipe
from eluthia.py_configs import deb822

@chmod(0o755)
@file
def postinst(full_path, package_name, apps):
    return f'''\
        #!/bin/bash
        # Set ownership of secrets.env to badtrackuser
        getent passwd badtrackuser > /dev/null || sudo useradd -r -s /bin/false badtrackuser
        chown -R badtrackuser:badtrackuser \"/var/lib/badtrack/secrets.env\"
    '''

@chmod(0o600)
@file
def secrets(full_path, package_name, apps):
    return f'''\
        EMAIL_USER = {apps[package_name]['env']['EMAIL_USER']}
        EMAIL_PASSWORD = {apps[package_name]['env']['EMAIL_PASSWORD']}
    '''

def get_package_tree(package_name, apps):
    return {
        'DEBIAN': {
            'postinst': postinst,
            'control': file(pipe(
                control,
                lambda d: {**d, 'Description': 'Contains email credentials for badtrack'},
                deb822)),
        },
        'var': {
            'lib': {
                'badtrack': {
                    'secrets.env': secrets
                }
            }
        }
    }
