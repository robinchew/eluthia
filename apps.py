import os
config = {
    'badtrack': {
        'folder': '../badtrack',
        'env': {
            'EMAIL_HOST': os.environ.get('EMAIL_HOST', 'relay.mailbaby.net'),
            'EMAIL_PORT': os.environ.get('EMAIL_PORT', '465'),
            'EMAIL_TO': os.environ.get('EMAIL_TO', 'robinchew@gmail.com'),
            'EMAIL_FROM': 'sender@obsi.com.au'
        },
    },
    'fuel': {
        'folder': '../fueltrack',
    },
    'badtrack-secrets': {
        'folder': '../badtrack',
        'env': {
            'EMAIL_PASSWORD': os.environ['EMAIL_PASSWORD'],
            'EMAIL_USER': os.environ['EMAIL_USER'],
        },
    },
}
