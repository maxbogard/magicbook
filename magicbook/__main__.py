import argparse
from pathlib import Path
import sys

import os
import json
from simple_term_menu import TerminalMenu
from rich import print

from setup_tools import setup_magicbook_library
from library_tools import audit_library
from book_tools import assemble_books
# from book_tools import Instrument
from imposition_tools import merge_marchpacks
from simple_io_tools import (
    assemble_book_questions,
    impose_choose_book,
    impose_choose_ensemble,
    choose_format_questions,
    display_chart_list
)

from constants import (
    DEFAULT_CONFIG,
    SPLITSORT,
    MARCHPACK_FORMATS,
    BINDER_FORMATS
)

# various unorganized config files


def load_config(config_dir) -> dict:
    """
    ***CONFIG IS NOW STORED IN A MAGICBOOK LIBRARY
    ***DEPRECATE THIS FUNCTION !!!
    Load a JSON config file
    """
    with open(os.path.join(config_dir, 'config.json')) as config_file:
        config = json.load(config_file)
    return config


def load_ensemble(ensemble):
    """
    ~NOT DEPRECATED
    Load a JSON ensemble file
    """
    with open(ensemble) as ensemble:
        ensemble_info = json.load(ensemble)
    return ensemble_info


def load_instruments(instruments):
    """
    ~NOT DEPRECATED
    Load a JSON default instruments file
    """
    with open(instruments) as instruments:
        instrument_defaults = json.load(instruments)
    return instrument_defaults


# and now the code begins...
def list_assembled_books(dir):
    """
    ***DEPRECATE THIS ???
    List all the books in a directory
    """
    books = []
    for file in os.listdir(dir):
        if file.endswith(".pdf"):
            books.append(file)
    return books


def going_home():
    print('\n...returning to main menu\n')


def interactive_mode():
    """
    A fully interactive mode to run magicbook, in the style of an 80s text
    adventure game, that doesn't require the user to pass any arguments.
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

    print("hey, you're running magicbook!")

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


def load_settings(mbp, config):
    """
    Loads a config json file from the selected magicbook library
    """
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


def main():
    """
    The CLI-style UI for magicbook, taking arguments.
    The goal is to use this to run a GUI with gooey
    """

    parser = argparse.ArgumentParser(
        prog="magicbook",
        description="Sheet music management for large ensembles",
        epilog="v0.0.2, licensed under the AGPL-3.0"
    )

    parser.add_argument(
        "path"
        )

    primary = parser.add_mutually_exclusive_group()
    primary.add_argument(
        "-int",
        "--interactive",
        action="store_true",
        help="Runs magicbook with the old interactive text-adventure style UI"
        )
    primary.add_argument(
        "-n",
        "--new-library",
        action="store_true",
        help="Creates a new magicbook library in the specified path"
        )
    primary.add_argument(
        "-a",
        "--audit-library",
        action="store_true",
        help="Audits each chart dir in the library for a valid info.json file"
        )
    primary.add_argument(
        "-b",
        "--build-books",
        action="store_true",
        help="Builds a set of books from the specified library"
        )
    primary.add_argument(
        "-p",
        "--impose-books",
        action="store_true",
        help="Imposes a set of books for printing into the specified format"
    )
    primary.add_argument(
        "-l",
        "--list-charts",
        action="store_true",
        help="Lists all charts in the library, with chart details"
    )

    parser.add_argument(
        "-ens",
        "--ensemble",
        type=str,
        help="Specify an ensemble to perform an action with"
    )
    parser.add_argument(
        "-bk",
        "--book",
        type=str,
        help="Specify a book to perform an action with"
    )
    parser.add_argument(
        "-pfmt",
        "--print-format",
        type=str,
        help="Specify a format to impose books into"
    )

    args = parser.parse_args(args=None if sys.argv[1:] else ["-h"])

    magicbook_path = Path(args.path)

    if args.interactive is True:
        interactive_mode()
        exit()

    if args.new_library is True:
        setup_magicbook_library(magicbook_path)
        exit()

    settings = load_settings(magicbook_path, DEFAULT_CONFIG)
    if settings is False:
        print(
            'This directory doesn\'t look like a magicbook library\n'
            'Or the magicbook library might be corrupted\n'
            'Please run magicbook with the -n flag to create a new library'
        )
        exit()

    library_path = os.path.join(
        magicbook_path,
        settings['directories']['library']
        )

    v, x, t, lib = audit_library(
        library_path,
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
    if args.audit_library is True:
        exit()

    default_instruments = load_instruments(
        os.path.join(
            magicbook_path,
            'config',
            settings['default-instruments']
            )
        )

    ensemble_path = os.path.join(
        magicbook_path,
        'config',
        settings['default-ensemble']
        )

    ensemble_info = load_ensemble(ensemble_path)
    ensemble_instruments = ensemble_info['instruments']
    for instrument in ensemble_instruments:
        if instrument.get('alternates') is None:
            if instrument['slug'] in default_instruments.keys():
                instrument['alternates'] = (
                    default_instruments[instrument['slug']]['alternates']
                )

    output_dir = os.path.join(
        magicbook_path,
        settings['directories']['output']
        )

    if args.list_charts is True:
        display_chart_list(lib)
        exit

    if args.build_books is True:
        selected_charts, book_order_data = (
            assemble_book_questions(
                ensemble_info,
                lib
                )
            )
        issue_dir = assemble_books(
            selected_charts,
            library_path,
            output_dir,
            ensemble_instruments,
            ensemble_info['slug'],
            ensemble_info['name'],
            book_order_data,
            SPLITSORT
                )

        print(f'Books assembled to {magicbook_path}/{issue_dir}')
        exit()

    if args.impose_books is True:
        if args.ensemble is None:
            ensemble_slug = impose_choose_ensemble(output_dir)
        else:
            ensemble_slug = args.ensemble

        if args.book is None:
            book_dir = impose_choose_book(
                output_dir,
                ensemble_slug
                )
        else:
            book_dir = args.book

        if args.print_format is None:
            book_format = choose_format_questions()
        else:
            book_format = args.print_format

        path_to_book = os.path.join(
            output_dir,
            ensemble_slug,
            book_dir
            )

        book_info_f = os.path.join(
            output_dir,
            ensemble_slug,
            book_dir,
            'book-info.json'
            )

        with open(book_info_f) as book_info:
            book_info = json.load(book_info)

        merge_marchpacks(
            book_info['charts'],
            path_to_book,
            book_format
        )

        exit()


if __name__ == "__main__":
    main()
