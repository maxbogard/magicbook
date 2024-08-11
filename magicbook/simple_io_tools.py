from simple_term_menu import TerminalMenu

from library_tools import Chart


def chart_names_list(charts_list: list[Chart]):
    """
    """
    chart_names = [chart.title for chart in charts_list]
    return chart_names


def assemble_book_questions(
        ensemble_info: dict,
        charts_list: list[Chart]
        ) -> tuple[list[Chart], bool, int]:
    """
    """
    ens_name = ensemble_info['name']
    print(f"You are about to assemble books for the {ens_name}.")
    print("What charts are going in these books?")
    while True:
        charts_select_menu = TerminalMenu(
            chart_names_list(charts_list),
            multi_select=True,
            show_multi_select_hint=True
            )
        chart_menu_indices = charts_select_menu.show()
        selected_charts_list = []
        for i in chart_menu_indices:
            selected_charts_list.append(charts_list[i])

        n = len(selected_charts_list)
        print(f"You have selected the following {n} charts:")
        for t in selected_charts_list:
            print(t.title)
        print("Is this correct?")
        if input("y/n: ") == 'y':
            break

    lowest_max_id = ((n // 2) + (n % 2))

    print('Do you intend to print any of these books as march packs?')
    # need better phrasing for this -
    # it determines whether A/B prefixes are created
    if input("y/n: ") == 'y':
        abside = True
        print(
            "What number would you like to assign"
            "to the last chart of the B side?\n"
            f"The minimum number is {lowest_max_id}, and it is recommended to"
            "choose a larger number so you have flexibility to add charts in"
            "the future.\n"
            "Max. number is 99."
            )
        while True:
            max_id = int(input("Last B ID: "))
            if max_id < 1:
                print(
                    f"""
                    Please choose a number equal to or \
                    greater than {lowest_max_id}.
                    """
                    )
            elif max_id > 99:
                print("Please choose a number less than 100.")
            else:
                break
    else:
        abside = False
        max_id = -1

    return selected_charts_list, abside, max_id
