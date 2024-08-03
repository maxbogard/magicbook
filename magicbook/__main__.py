import os
import yaml
from simple_term_menu import TerminalMenu

from library_tools import audit_library
from library_tools import lib_query
from book_tools import assemble_books
from prompt_toolkit import print_formatted_text as print
from prompt_toolkit import HTML

# various unorganized config files

config_dir = "./config/"
ensembles_dir = os.path.join(config_dir, "ensembles")
schema_dir = "./schema/"
output_dir = "./output/"
chart_schema = "chart-info.json"
library_path = "./music-library/"
active_ensemble = "generic_ensemble.yaml"

splitsort = {
    2: [
        {"parts": [1], "name": "1"},
        {"parts": [2], "name": "2"},
    ],
    3: [
        {"parts": [1, 1], "name": "1"},
        {"parts": [1, 2], "name": "2A"},
        {"parts": [2, 2], "name": "2B"},
        {"parts": [2, 3], "name": "3"}
    ],
    4: [
        {"parts": [1, 1, 1], "name": "1"},
        {"parts": [1, 1, 2], "name": "2A"},
        {"parts": [1, 2, 2], "name": "2B"},
        {"parts": [2, 2, 2], "name": "2C"},
        {"parts": [2, 2, 3], "name": "3A"},
        {"parts": [2, 3, 3], "name": "3B"},
        {"parts": [2, 3, 4], "name": "4"}
    ]
}

# and now the code begins...


def going_home():
    print('\n...returning to main menu\n')


def main():
    """
    Will run various functions from various modules
    """
    options = ["Query Charts",
               "Assemble Books",
               "Exit"]

    print(
        f"opening library {library_path}, auditing charts"
    )

    v, x, t, lib = audit_library(library_path,
                                 os.path.join(schema_dir, chart_schema))
    if v is False:
        print(f'{x} / {t} charts info.json failed validation.')
        print('Please fix these and try again')
        exit()
    else:
        print(f'The library passed the audit with all {t} charts valid!\n')

    with open(os.path.join(ensembles_dir, active_ensemble)) as ensemble:
        ensemble_info = yaml.safe_load(ensemble)

    ensemble_instruments = ensemble_info['instruments']
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
            assemble_books(lib,
                           library_path,
                           output_dir,
                           ensemble_instruments,
                           ensemble_dir,
                           splitsort)
            going_home()
        elif options[menu_entry_index] == "Query Charts":
            lib_query(lib)
            going_home()


if __name__ == "__main__":
    main()
