import os

from eluthia.decorators import chmod, copy_files, copy_folder, file, git_clone, empty_folder, build_and_unpack_erlang_release
from eluthia.defaults import control
from eluthia.functional import pipe
from eluthia.py_configs import deb822


@chmod(0o755)
@file
def postinst(full_path, package_name, apps):
    return f'''\
        #!/bin/bash
        systemctl daemon-reload

        # Enable and start the service
        systemctl enable {package_name}
        systemctl restart {package_name}
    '''

@file
def systemd_service(full_path, package_name, apps):
    default_env = {
        'LOG_DIR': '/home/ubuntu/system/file_saver_logs',
        'FILE_SAVE_PATH': '/home/ubuntu/system/file_saved',
        'SERVER_PORT': '4555',
        'SMTP_HOST': 'relay.mailbaby.net',
        'SMTP_FROM': 'sender@obsi.com.au',
        'PYTHON_BINARY_PATH': '/usr/bin/python3',
        'CLI_PY_PATH': '/home/ubuntu/system/file_saver_py/cli.py',
        'CLI_WRITE_PY_PATH': '/home/ubuntu/system/file_saver_py/cli_write.py',
    }
    environment_variables = '\n'.join(
        f"        Environment={variable}={value}"
        for variable, value in {**default_env, **apps[package_name]['env']}.items()).strip()

    return f'''\
        [Unit]
        Description=File Saver Service
        After=network.target
        [Service]
        Type=simple
        User=ubuntu
        #WorkingDirectory=/home/ubuntu/system/file_saver
        ExecStart=/home/ubuntu/system/file_saver_erl/bin/erlserver_release foreground
        {environment_variables}
        [Install]
        WantedBy=multi-user.target
    '''

def get_package_tree(package_name, apps):
    return {
        'DEBIAN': {
            'postinst': postinst,
            'control': file(pipe(
                control,
                lambda d: {**d, 'Description': 'File Saver'},
                deb822)),
        },
        'etc': {
            'systemd': {
                'system': {
                    f'{package_name}.service': systemd_service,
                },
            },
        },
        'home': {
            'ubuntu': {
                'system': {
                    'file_saver_erl': build_and_unpack_erlang_release(os.path.join(apps[package_name]['clean_git_folder'], 'erlserver')),
                    'file_saver_py': copy_files(apps[package_name]['folder'], [
                        'cli.py',
                        'cli_write.py',
                        'server.py',
                    ]),
                    'file_saver_logs': empty_folder,
                    'file_saved': empty_folder,
                }
            },
        },
    }
