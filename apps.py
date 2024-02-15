import os
from eluthia.constants import GIT, NORMAL, UNSET

HERE = os.path.abspath(os.path.dirname(__file__))

config = {
    'robin-com-au': {
        'folder_type': GIT,
        'folder': '../robin.com.au',
        'build_module_relpath': 'build.py',
        'https_domains': ['www.robin.com.au'],
        'env': {
            'VENV_BUILD_PATH': UNSET,
        },
    },
    'badtrack': {
        'folder_type': GIT,
        'folder': '../badtrack',
        'build_module_relpath': 'build.py',
        'env': {
            'HISTORY_FOLDER': '/var/lib/badtrack/history',
            'CACHE_FOLDER': '/NON_EXISTENT_FOLDER', # Remove once badtrack can run without setting CACHE_FOLDER
            'EMAIL_HOST': UNSET,
            'EMAIL_PORT': 465,
            'EMAIL_TO': 'robinchew@gmail.com',
            'EMAIL_FROM': 'sender@obsi.com.au',
            'EMAIL_PASSWORD': UNSET,
            'EMAIL_USER': UNSET,
        },
    },
    'check-ssl': {
        'folder_type': GIT,
        'folder': '../check-ssl',
        'build_module_relpath': 'build.py',
        'env': {
            'EMAIL_HOST': UNSET,
            'EMAIL_TO': 'robinchew@gmail.com',
            'EMAIL_FROM': 'sender@obsi.com.au',
            'EMAIL_USERNAME': UNSET,
            'EMAIL_PASSWORD': UNSET,
        },
    },
    'chat': {
        'folder_type': GIT,
        'folder': '../chat',
        'build_module_relpath': 'build.py',
        'env': {},
    },
    'file-saver': {
        'folder_type': GIT,
        'folder': '../file_saver',
        'build_module_relpath': 'build.py',
        'env': {
            'SMTP_USERNAME': UNSET,
            'SMTP_PASSWORD': UNSET,
            'TOTP_SECRET': UNSET,
            'DOMAIN_MAP': {
                'VIEW': 'view.robin.au',
                'EDIT': 'edit.robin.au',
                'POC': 'secure.robin.au',
                'SERVER': 'txt.robin.au',
            },
        },
    },
    #'fuel': {
    #    'folder_type': GIT,
    #    'folder': '../fueltrack',
    #},
    'ozmeetup': {
        'folder_type': GIT,
        'folder': '../ozmeetup',
        'build_module_relpath': 'build.py',
        'env': {
            'PUBLIC_HOST': 'demo.robin.au',
            'PUBLIC_PORT': 80,
            'DB_HOST': 'localhost',
            'DB_NAME': 'ozm_db',
            'DB_USER': 'db_user',
            'DB_PASSWORD': UNSET,
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

machines = {
    'orchid-inca': {
        'ports_map': [
            (4555, 'file_saver_server'),
            (4556, 'ozm_api_server'),
            (9000, 'chat_server'),
        ],
    }
}
