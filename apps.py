from collections import namedtuple

App = namedtuple('App', ('working_folder', 'version', 'port'))

app_config = {
    'badtrack': {
        'working_folder': '/home/robin/work/badtrack',
    },
    'fuel': {
        'working_folder': '/home/robin/work/fueltrack',
    },
}


apps = {
    name: App(**{
        **d,
        'version': '',
        'port': 9999,
    })
    for name, d in app_config.items()
}
