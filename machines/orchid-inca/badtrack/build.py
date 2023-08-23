from eluthia.decorators import chmod, copy_folder, file, git_clone

@chmod(0o755)
@file
def postinst(full_path, package_name, apps):
    return f'''\
        #!/bin/bash
        # Reload the systemd daemon to recognize the new service file
        systemctl daemon-reload

        # Enable and start the service
        systemctl enable {package_name}
        systemctl start {package_name}
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
        # Installed-Size: 1024
        Maintainer: Your Name <your-email@example.com>
        Description: Badtrack is a sample package
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
        [Install]
        WantedBy=multi-user.target
    '''

def get_package_tree(package_name, apps):
    return {
        'DEBIAN': {
            'postinst': postinst,
            'control': control,
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
                    'badtrack': git_clone(apps[package_name].folder),
                }
            },
        },
    }
