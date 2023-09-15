import os
config = {
    'badtrack': {
        'folder': '../badtrack',
        'env': {
            'HISTORY_FOLDER': '/var/lib/badtrack/history',
            'CACHE_FOLDER': '/var/lib/badtrack/cache',
            'EMAIL_HOST': os.environ.get('EMAIL_HOST', 'relay.mailbaby.net'),
            'EMAIL_PORT': os.environ.get('EMAIL_PORT', '465'),
            'EMAIL_TO': os.environ.get('EMAIL_TO', 'robinchew@gmail.com'),
            'EMAIL_FROM': 'sender@obsi.com.au',
            'EMAIL_PASSWORD': os.environ.get('EMAIL_PASSWORD', None), # Changes to get so that zipapp can read config to get history folder without KeyError
            'EMAIL_USER': os.environ.get('EMAIL_USER', None),
        },
    },
    'fuel': {
        'folder': '../fueltrack',
    },
    'nginx-conf': {
        'folder': '../nginx-conf'
    },
    'eluthia-cron-example': {
        'folder': '../eluthia-cron-example',
        'env': {
            'EMAIL_PASSWORD': os.environ.get('EMAIL_PASSWORD', None),
            'EMAIL_USER': os.environ.get('EMAIL_USER', None),
        },
    },
}
