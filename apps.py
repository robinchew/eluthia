import os
from eluthia.constants import GIT, NORMAL

HERE = os.path.abspath(os.path.dirname(__file__))

config = {
    'badtrack': {
        'folder_type': GIT,
        'folder': '../badtrack',
        'env': {
            'HISTORY_FOLDER': '/var/lib/badtrack/history',
            'CACHE_FOLDER': '/NON_EXISTENT_FOLDER', # Remove once badtrack can run without setting CACHE_FOLDER
            'EMAIL_HOST': os.environ.get('EMAIL_HOST', 'relay.mailbaby.net'),
            'EMAIL_PORT': os.environ.get('EMAIL_PORT', '465'),
            'EMAIL_TO': os.environ.get('EMAIL_TO', 'robinchew@gmail.com'),
            'EMAIL_FROM': 'sender@obsi.com.au',
            'EMAIL_PASSWORD': os.environ['EMAIL_PASSWORD'],
            'EMAIL_USER': os.environ['EMAIL_USER'],
        },
    },
    'file-saver': {
        'folder_type': GIT,
        'folder': '../file_saver',
        'build_module_relpath': 'build.py',
        'env': {
            'SMTP_USERNAME': os.environ['EMAIL_USER'],
            'SMTP_PASSWORD': os.environ['EMAIL_PASSWORD'],
            'TOTP_SECRET': os.environ['TOTP_SECRET'],
        },
    },
    #'fuel': {
    #    'folder_type': GIT,
    #    'folder': '../fueltrack',
    #},
    'nginx-conf': {
        'folder_type': NORMAL,
        'folder': '../nginx-conf'
    },
    'eluthia-cron-example': {
        'folder_type': GIT,
        'folder': '../eluthia-cron-example',
        'env': {
            'EMAIL_PASSWORD': os.environ['EMAIL_PASSWORD'],
            'EMAIL_USER': os.environ['EMAIL_USER'],
        },
    },
}
config = {
    k: {
        **d,
        'folder': os.path.abspath(os.path.join(HERE, d['folder'])),
    }
    for k, d in config.items()
}
