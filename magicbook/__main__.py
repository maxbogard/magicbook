import os
import yaml
from simple_term_menu import TerminalMenu
import survey
from prompt_toolkit import print_formatted_text as print
from prompt_toolkit import HTML

from constants import SPLITSORT
from library_tools import audit_library
from library_tools import lib_query
from book_tools import assemble_books
from imposition_tools import merge_marchpacks


# various unorganized config files

config_dir = "./config/"
ensembles_dir = os.path.join(config_dir, "ensembles")
schema_dir = "./schema/"
output_dir = "./output/"
chart_schema = "chart-info.json"
library_path = "./music-library/"
active_ensemble = "generic_ensemble.yaml"


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
    options = ["Query Charts",
               "Assemble Books",
               "Impose Created Books",
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
            selected_charts, issue_dir = assemble_books(lib,
                                                        library_path,
                                                        output_dir,
                                                        ensemble_instruments,
                                                        ensemble_dir,
                                                        SPLITSORT)
            if survey.routines.inquire("Impose PDFS?", default=True) is True:
                merge_marchpacks(selected_charts, True, issue_dir, ensemble_info)
            going_home()
        elif options[menu_entry_index] == "Impose Created Books":
            if output_dir == False:
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
        elif options[menu_entry_index] == "Query Charts":
            lib_query(lib)
            going_home()


if __name__ == "__main__":
    main()
