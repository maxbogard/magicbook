import os
import json
from simple_term_menu import TerminalMenu
import survey
from prompt_toolkit import print_formatted_text as print
from prompt_toolkit import HTML

from library_tools import audit_library
from book_tools import assemble_books
# from book_tools import Instrument
from imposition_tools import merge_marchpacks
from simple_io_tools import assemble_book_questions

from constants import SPLITSORT, MARCHPACK_FORMATS, BINDER_FORMATS

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


def main():
    """
    Will run various functions from various modules
    """

    CONFIG_DIR = './config/'
    config = load_config(CONFIG_DIR)

    # ensembles_dir = os.path.join(
    #     CONFIG_DIR,
    #     config['directories']['ensembles']
    #     )
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
            if survey.routines.inquire("Impose PDFS?", default=True) is True:
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
            if output_dir is False:
                existing_books = list_assembled_books(output_dir)
                print("You didn't assemble any books during this session.")
                if existing_books is False:
                    print("There are no previously assembled books either.")
                    print("Please assemble some books first.")
                    going_home()
            # else:
        # NEED A WAY TO RETREIVE CHART OBJECTS TO PRINT A PREVIOUS BOOK!!
        # print("Would you like to choose a previously assembled book?")
        # existing_books.append("Return to Main Menu")
        # imposition_menu = TerminalMenu(existing_books)
        # imposition_entry_index = imposition_menu.show()
        # if existing_books[imposition_entry_index] == "Return to Main Menu":
        #     going_home()
        # else:
        #     for book in existing_books:
        #         if existing_books[imposition_entry_index] == book:
        #             selected_book = book
        #             break

            merge_marchpacks(selected_charts, True, issue_dir, ensemble_info)
            going_home()


if __name__ == "__main__":
    main()
