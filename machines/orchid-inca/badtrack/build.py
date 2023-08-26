import os

from eluthia.decorators import chmod, copy_folder, file, git_clone
from eluthia.defaults import control
from eluthia.functional import pipe
from eluthia.py_configs import deb822

is_test = 'TEST_MODE' in os.environ

@chmod(0o755)
@file
def postinst(full_path, package_name, apps):
    return f'''\
        #!/bin/bash
        getent passwd badtrackuser > /dev/null || sudo useradd -r -s /bin/false badtrackuser
        chown -R badtrackuser:badtrackuser \"/var/lib/badtrack/\"
        # Reload the systemd daemon to recognize the new service file
        systemctl daemon-reload

        # Enable and start the service
        systemctl enable {package_name}
        systemctl restart {package_name}
    '''

@file
def systemd_service(full_path, package_name, apps):
    return f'''\
        [Unit]
        Description=BadTrack Service
        After=network.target
        [Service]
        Type=simple
        User=badtrackuser
        WorkingDirectory=/usr/local/bin/badtrack
        ExecStart=/usr/bin/python3 /usr/local/bin/badtrack/main.py
        Environment=HISTORY_FOLDER=/var/lib/badtrack/history
        Environment=CACHE_FOLDER=/var/lib/badtrack/cache
        #This is to allow for testing.
        Environment=EMAIL_HOST={'localhost' if is_test else 'relay.mailbaby.net'}
        Environment=EMAIL_PORT={'1025' if is_test else '465'}
        Environment=EMAIL_FROM=sender@obsi.com.au
        Environment=EMAIL_TO={'yannstaggl@gmail.com' if is_test else 'robinchew@gmail.com'}
        EnvironmentFile=/var/lib/badtrack/secrets.env
        [Install]
        WantedBy=multi-user.target
    '''

# I think it'd be better if this was somewhere else and then could be imported in, but I wasn't sure where to put it. 
def blank_folder(full_path, package_name, apps):
    os.makedirs(os.path.join(*full_path), exist_ok=True)
    return

def get_package_tree(package_name, apps):
    return {
        'DEBIAN': {
            'postinst': postinst,
            'control': file(pipe(
                control,
                lambda d: {**d, 'Description': 'Badtrack!'},
                deb822)),
        },
        'etc': {
            'systemd': {
                'system': {
                    f'{package_name}.service': systemd_service,
                },
            },
        },
        'usr': {
            'local': {
                'bin': {
                    'badtrack': copy_folder('/home/ystaggl/Workspace/badtrack') if is_test else git_clone(apps[package_name]['folder']),
                }
            },
        },
        'var':{
            'lib':{
                'badtrack': {
                    'history': blank_folder,
                    'cache': blank_folder,
                }
            }
        }
    }
