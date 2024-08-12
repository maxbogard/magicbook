from simple_term_menu import TerminalMenu

from library_tools import Chart


def chart_names_list(charts_list: list[Chart]):
    """
    """
    chart_names = [chart.title for chart in charts_list]
    return chart_names


def lib_single_query(loc, pageid="", prefix=None):
    """
    prompts the user to select a single chart from a list of charts
    optional input to specify the page ID
    """
    if prefix is None:
        pre = ""
    else:
        pre = f"{prefix}"

    print(f"SELECT CHART: {pre}{pageid}")

    charts_select_menu = TerminalMenu(
        chart_names_list(loc),
        multi_select=False,
    )
    selected_index = charts_select_menu.show()
    selected_chart = loc[selected_index]

    return selected_chart


def assemble_book_questions(
        ensemble_info: dict,
        charts_list: list[Chart]
        ) -> tuple[
            list[list[Chart]],
            tuple[bool, int, bool]
            ]:
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

    print(
        'How would you like the charts to be ordered?\n'
        ' - [A]lphabetical order\n'
        ' - [C]ustom order\n'
    )
    if input("A/C: ") == 'C':
        custom_order = True
        if abside is True:
            charts_rem = selected_charts_list.copy()
            if abside is True:
                book_pages = (len(charts_rem) // 2)
                book_rem = (len(charts_rem) % 2)
                print(
                    "Select charts for 'A' side, in order from first to last"
                )
                a_index = {}
                a_id = 1
                for i in range(0, book_pages):
                    chart = lib_single_query(
                        charts_rem,
                        pageid=f"{a_id}",
                        prefix='A'
                        )
                    charts_rem.remove(chart)
                    a_index[a_id] = chart
                    a_id += 1
                print(
                    "Select charts for 'B' side, in order from first to last"
                )
                b_index = {}
                b_id = ((max_id - book_pages) + 1)
                for i in range(0, book_pages + book_rem):
                    chart = lib_single_query(
                        charts_rem,
                        pageid=f"{b_id}",
                        prefix='B'
                        )
                    charts_rem.remove(chart)
                    b_index[b_id] = chart
                    b_id += 1

                sorted_charts = [a_index, b_index]

            else:
                book_pages = len(charts_rem)
                print(
                    "Select charts in order from first to last"
                )
                x_index = {}
                x_id = 1
                for n in range(0, book_pages):
                    chart = lib_single_query(
                        charts_rem,
                        pageid=f"{x_id}"
                        )
                    charts_rem.remove(chart)
                    x_index[x_id] = chart
                    x_id += 1

                sorted_charts = [x_index]

        else:
            custom_order = False
            sorted_charts = selected_charts_list

        book_order_data = (abside, max_id, custom_order)

    return sorted_charts, book_order_data
