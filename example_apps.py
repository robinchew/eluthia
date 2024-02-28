import os

from eluthia.functional import overlay
from eluthia.constants import GIT, UNSET

from apps import config as base_config, machines

HERE = os.path.abspath(os.path.dirname(__file__))

config = overlay(
    {
        # Get only robin-com-au from base config
        'robin-com-au': base_config['robin-com-au'],
    },
    {
        # Deep merge to set VENV_BUILD_PATH which is UNSET in the base config
        'robin-com-au': {
            'env': {
                'VENV_BUILD_PATH': os.path.join(HERE, 'venv-robin'),
            },
        },
    })
