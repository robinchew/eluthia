import os
config = {
    'badtrack': {
        'folder': '../badtrack',
        'env': {
            'EMAIL_HOST': os.environ.get('EMAIL_HOST', 'relay.mailbaby.net'),
            'EMAIL_PORT': os.environ.get('EMAIL_PORT', '465'),
            'EMAIL_TO': os.environ.get('EMAIL_TO', 'robinchew@gmail.com'),
            'EMAIL_FROM': 'sender@obsi.com.au',
            'EMAIL_PASSWORD': os.environ['EMAIL_PASSWORD'],
            'EMAIL_USER': os.environ['EMAIL_USER'],
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
            'EMAIL_PASSWORD': os.environ['EMAIL_PASSWORD'],
            'EMAIL_USER': os.environ['EMAIL_USER'],
        },
    },
}
