from collections import namedtuple

machines = './machines/orchid-inca'

App = namedtuple('App', ('folder', 'version', 'port'))

app_config = {
    'badtrack': {
        'folder': '/home/robin/work/badtrack',
    },
    'fuel': {
        'folder': '/home/robin/work/fueltrack',
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
