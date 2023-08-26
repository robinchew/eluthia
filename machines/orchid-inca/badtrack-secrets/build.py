from eluthia.decorators import chmod, copy_folder, file, git_clone
import os

@chmod(0o755)
@file
def postinst(full_path, package_name, apps):
    return f'''\
        #!/bin/bash
        # Set ownership of secrets.env to badtrackuser
        getent passwd badtrackuser > /dev/null || sudo useradd -r -s /bin/false badtrackuser
        chown -R badtrackuser:badtrackuser \"/var/lib/badtrack/secrets.env\"
    '''

@file
def control(full_path, package_name, apps):
    return f'''\
        Package: {package_name}
        Version: {apps[package_name].version}
        Section: custom
        Priority: optional
        Architecture: all
        Essential: no
        #Installed-Size: 1024
        Maintainer: Your Name <your-email@example.com>
        Description: Badtracksecrets is a sample package
    '''

@chmod(0o600)
@file
def secrets(full_path, package_name, apps):
    return f'''\
        EMAIL_USER = {os.environ['EMAIL_USER']}
        EMAIL_PASSWORD = {os.environ['EMAIL_PASSWORD']}
    '''

def get_package_tree(package_name, apps):
    return {
        'DEBIAN': {
            'postinst': postinst,
            'control': control,
        },
        'var': {
            'lib': {
                'badtrack': {
                    'secrets.env': secrets
                }
            }
        }
    }
