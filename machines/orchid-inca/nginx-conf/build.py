from textwrap import dedent

from eluthia.decorators import chmod, copy_folder, file, git_clone, empty_folder
from eluthia.defaults import control
from eluthia.functional import pipe
from eluthia.py_configs import deb822

@chmod(0o755)
@file
def postinst(full_path, package_name, apps):
    return f'''\
#!/bin/bash
systemctl reload nginx
    '''

def deployed(path, package, apps):
    return dedent('''\
        server {
            listen 9999;
            location / {
                echo "Serving for port 9999";
            }
        }
    ''')

def get_package_tree(package_name, apps):
    return {
        'DEBIAN': {
            'postinst': postinst,
            'control': file(pipe(
                control,
                lambda d: {**d,
                    'Version': apps[package_name]['version'],
                    'Description': 'nginx-conf',
                    'Depends': 'nginx',
                },
                deb822)),
        },
        'etc': {
            'nginx': {
                'sites-enabled': {
                    'deployed_example': file(lambda path, package, apps: ''),
                },
            },
        },
    }
