import argparse
from pathlib import Path

import os
import json
from simple_term_menu import TerminalMenu
from prompt_toolkit import print_formatted_text as print
from prompt_toolkit import HTML

from library_tools import audit_library
from book_tools import assemble_books
# from book_tools import Instrument
from imposition_tools import merge_marchpacks
from simple_io_tools import assemble_book_questions

from constants import (
    MAGICBOOK_DIRECTORY,
    DEFAULT_CONFIG,
    DEFAULT_SCHEMA,
    DEFAULT_ENSEMBLE,
    DEFAULT_INSTRUMENTS,
    SPLITSORT,
    MARCHPACK_FORMATS,
    BINDER_FORMATS
)

# various unorganized config files


def load_config(config_dir) -> dict:
    """
    Load a JSON config file
    """
    with open(os.path.join(config_dir, 'config.json')) as config_file:
        config = json.load(config_file)
    return config


def load_ensemble(ensemble):
    """
    Load a JSON ensemble file
    """
    with open(ensemble) as ensemble:
        ensemble_info = json.load(ensemble)
    return ensemble_info


def load_instruments(instruments):
    """
    Load a JSON default instruments file
    """
    with open(instruments) as instruments:
        instrument_defaults = json.load(instruments)
    return instrument_defaults


# and now the code begins...
def list_assembled_books(dir):
    """
    List all the books in a directory
    """
    books = []
    for file in os.listdir(dir):
        if file.endswith(".pdf"):
            books.append(file)
    return books


def going_home():
    print('\n...returning to main menu\n')


def text_adventure():
    """
    The old, text-adventure style UI for magicbook
    Find the argparse command in main() to launch
    """
    CONFIG_DIR = './config/'
    config = load_config(CONFIG_DIR)

    schema_dir = os.path.join(
        CONFIG_DIR,
        config['directories']['schema']
        )

    chart_schema = os.path.join(schema_dir, 'chart-info.json')
    library_path = config['directories']['library']
    output_dir = config['directories']['output']
    # active_ensemble = os.path.join(CONFIG_DIR, config['default-ensemble'])
    active_ensemble = os.path.join(CONFIG_DIR, 'ensembles/bcrband.json')
    default_instruments = os.path.join(
        CONFIG_DIR,
        config['default-instruments']
        )

    options = [
        "Assemble Books",
        "Impose Created Books",
        "Exit"
        ]

    book_formats = []
    book_formats.extend(MARCHPACK_FORMATS)
    book_formats.extend(BINDER_FORMATS)
    book_formats.append("Return to Main Menu")

    print(
        f"opening library {library_path}, auditing charts"
    )

    v, x, t, lib = audit_library(library_path, chart_schema)
    if v is False:
        print(f'{x} / {t} charts info.json failed validation.')
        print('Please fix these and try again')
        exit()
    else:
        print(f'The library passed the audit with all {t} charts valid!\n')

    ensemble_info = load_ensemble(active_ensemble)
    default_instruments = load_instruments(default_instruments)

    ensemble_instruments = ensemble_info['instruments']
    for instrument in ensemble_instruments:
        if instrument.get('alternates') is None:
            if instrument['slug'] in default_instruments.keys():
                instrument['alternates'] = (
                    default_instruments[instrument['slug']]['alternates']
                )
    ensemble_dir = ensemble_info['slug']

    print(
        HTML("hey, you're running <b>magicbook</b>!")
        )

    while True:
        print('MAIN MENU')
        terminal_menu = TerminalMenu(options)
        menu_entry_index = terminal_menu.show()
        if options[menu_entry_index] == "Exit":
            quit()
        elif options[menu_entry_index] == "Assemble Books":
            selected_charts, book_order_data = (
                assemble_book_questions(ensemble_info, lib)
            )
            issue_dir = assemble_books(
                selected_charts,
                library_path,
                output_dir,
                ensemble_instruments,
                ensemble_dir,
                ensemble_info['name'],
                book_order_data,
                SPLITSORT
                )
            print('Books assembled! How would you like them printed?')
            while True:
                print('SELECT BOOK FORMAT:')
                format_menu = TerminalMenu(book_formats)
                format_entry_index = format_menu.show()
                if book_formats[format_entry_index] == 'MarchpackSplit':
                    print('Not yet implemented')
                elif book_formats[
                        format_entry_index
                        ] == 'MarchpackComprehensive':
                    merge_marchpacks(
                        selected_charts,
                        issue_dir,
                        book_format='MarchpackComprehensive'
                        )
                    print('MarchpackComprehensive books printed!')
                    print('Print another format, or return to main menu')
                elif book_formats[format_entry_index] == 'BinderOnePartPg':
                    merge_marchpacks(
                        selected_charts,
                        issue_dir,
                        book_format='BinderOnePartPg'
                        )
                    print('MarchpackComprehensive books printed!')
                    print('Print another format, or return to main menu')
                elif book_formats[
                        format_entry_index
                        ] == 'BinderOneChartPg':
                    print('Not yet implemented')
                elif book_formats[
                        format_entry_index
                        ] == 'BinderSaveSomePaper':
                    print('Not yet implemented')
                elif book_formats[
                        format_entry_index
                        ] == 'BinderSaveLotsPaper':
                    print('Not yet implemented')
                elif book_formats[
                        format_entry_index
                        ] == '(Return to Main Menu)':
                    break

            going_home()
        elif options[menu_entry_index] == "Impose Created Books":
            print('Not yet implemented')
            going_home()


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


def load_settings(mbp, config):
    if os.path.exists(
        os.path.join(mbp, 'config', 'config.json')
    ):
        with open(
            os.path.join(mbp, 'config', 'config.json')
        ) as config_file:
            config = json.load(config_file)
        return config
    else:
        return False


def setup_magicbook_library(library_path):
    mbp = os.path.join(library_path, MAGICBOOK_DIRECTORY)
    mbp_config = os.path.join(mbp, 'config')

    if os.path.exists(mbp):
        print(
            'Directory "magicbook-library" already exists in the cwd.\n'
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
            mbp,
            'generic_ensemble.json',
            DEFAULT_ENSEMBLE,
        )
        setup_json(
            mbp,
            'instruments.json',
            DEFAULT_INSTRUMENTS,
        )
        print('New magicbook library created in cwd/magicbook-library')
        print('message about trim-guides PDF goes here')


def main():
    """
    The CLI-style UI for magicbook, taking arguments.
    The goal is to use this to run a GUI with gooey
    """

    parser = argparse.ArgumentParser()

    parser.add_argument("path")

    # parser.add_argument("-t", "--text-adventure", action="store_true")
    parser.add_argument("-n", "--new-library", action="store_true")
    parser.add_argument(
        "-a",
        "--audit-library",
        help="Audits each chart dir in the library for a valid info.json file",
        action="store_true")
    parser.add_argument("-b", "--build-books", action="store_true")

    args = parser.parse_args()

    magicbook_path = Path(args.path)

    # if args.text_adventure is True:
    #     text_adventure()
    #     exit()

    if args.new_library is True:
        setup_magicbook_library(magicbook_path)
        exit()
    else:
        settings = load_settings(magicbook_path, DEFAULT_CONFIG)
        if settings is False:
            print(
                'This directory doesn\'t look like a magicbook library\n'
                'Or the magicbook library might be corrupted\n'
                'Please run magicbook with the -n flag to create a new library'
            )
            exit()

    if args.audit_library is True:
        v, x, t, lib = audit_library(
            os.path.join(
                magicbook_path,
                settings['directories']['library']
            ),
            os.path.join(
                magicbook_path,
                'config',
                settings['directories']['schema'],
                'chart-info.json'
            )
            )
        if v is False:
            print(f'{x} / {t} charts info.json failed validation.')
            print('Please fix these and try again')
            exit()
        else:
            print(
                'The library passed the audit '
                f'with all {t} charts valid!\n'
                )
            exit()
    if args.build_books is True:
        print('Not yet implemented')
        exit()


if __name__ == "__main__":
    main()
