import os
import json

from .constants import (
    DEFAULT_CONFIG,
    DEFAULT_SCHEMA,
    DEFAULT_ENSEMBLE,
    DEFAULT_INSTRUMENTS
)


def setup_directory(mbp, dir):
    if not os.path.exists(
        os.path.join(
            mbp,
            dir,
        )
    ):
        os.mkdir(
            os.path.join(
                mbp,
                dir,
            )
        )


def setup_json(mbp, file, data, dir=None):
    if dir is None:
        with open(
            os.path.join(
                mbp,
                file
            ), 'w'
        ) as json_file:
            json.dump(data, json_file)
    else:
        with open(
            os.path.join(
                mbp,
                dir,
                file
            ), 'w'
        ) as json_file:
            json.dump(data, json_file)


def setup_magicbook_library(library_path):
    """
    Creates a new magicbook library in the specified path.
    If the directory already exists, informs the user and quits.
    """
    mbp = str(library_path)
    mbp_config = os.path.join(mbp, 'config')

    if os.path.exists(mbp):
        print(
            f'Directory {mbp} already exists in the cwd\n'
            'If this is an existing magicbook library, please open it\n'
            'If not, please rename this directory, so Magicbook won\'t'
            'overwrite it.'
        )
        exit()
    else:
        os.mkdir(mbp)
        os.mkdir(mbp_config)

        with open(f'{mbp_config}/config.json', 'w') as config_file:
            json.dump(DEFAULT_CONFIG, config_file)

        setup_directory(mbp_config, DEFAULT_CONFIG['directories']['ensembles'])
        setup_directory(mbp_config, DEFAULT_CONFIG['directories']['templates'])
        setup_directory(mbp_config, DEFAULT_CONFIG['directories']['schema'])
        setup_directory(mbp, DEFAULT_CONFIG['directories']['library'])
        setup_directory(mbp, DEFAULT_CONFIG['directories']['output'])
        setup_directory(mbp, DEFAULT_CONFIG['directories']['logs'])

        setup_json(
            mbp_config,
            'chart-info.json',
            DEFAULT_SCHEMA,
            dir=DEFAULT_CONFIG['directories']['schema']
        )
        setup_json(
            mbp_config,
            'generic_ensemble.json',
            DEFAULT_ENSEMBLE,
        )
        setup_json(
            mbp_config,
            'instruments.json',
            DEFAULT_INSTRUMENTS,
        )
        print('New magicbook library created in cwd/magicbook-library')
        print('message about trim-guides PDF goes here')
