from eluthia.decorators import file

@file
def postinst(package_name, apps):
    return f'''\
#!/bin/bash
systemctl reload nginx
    '''

def get_package_tree(package_name, apps):
    return {
        'DEBIAN': {
            'postinst': postinst,
        },
        'etc': {
            'nginx': {
                'sites-enabled': {
                    'deployed': file(lambda a, b: ''),
                },
            },
        },
    }