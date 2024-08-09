import os
import shutil
import datetime
import survey

from library_tools import lib_query


class Instrument:
    def __init__(self, slug, name, divs):
        self.slug = slug
        self.name = name
        self.divs = divs


def prepare_folder(output_dir, ensemble_dir):
    ensemble_loc = os.path.join(output_dir, ensemble_dir)
    is_existing = os.path.exists(ensemble_loc)
    if not is_existing:
        os.makedirs(ensemble_loc)

    isnow = datetime.datetime.now()
    issued = isnow.strftime("%Y-%m-%d %H%M%S")
    issue_dir = os.path.join(ensemble_loc, issued)

    if os.path.exists(issue_dir) is True:
        raise Exception("The output folder already exists.\
                         This should not happen!")

    os.makedirs(issue_dir)

    return issue_dir


def list_parts(chart, lib_dir):
    output_list = []
    for root, dirs, files in os.walk(os.path.join(lib_dir, chart.slug)):
        for file in files:
            if file.endswith(".pdf"):
                part_slug = file.replace(chart.slug, "")
                output_list.append((chart.slug, part_slug, file))
    return output_list


def grab_instrument_parts(instrument, charts, input, output):
    inst_charts_info = {}
    for chart in charts:
        n = 0
        parts = list_parts(chart, input)
        for c_slug, p_slug, fil in parts:
            if f" {instrument['slug']}" in p_slug:
                # space character filters out an instrument[slug] that is
                # potentially a substring of another instrument[slug]
                with open(os.path.join(input, c_slug, fil), 'rb') as source:
                    with open(os.path.join(output,
                                           instrument['slug'],
                                           (c_slug + p_slug)
                                           ), 'wb') as dest:
                        shutil.copyfileobj(source, dest)
                        n += 1
                        print(f" - added {c_slug} {p_slug}")
        if n < 1:
            print(f"!!! MISSING {chart.title}")
            inst_charts_info[chart.slug] = 0
        else:
            inst_charts_info[chart.slug] = n
    print('\n')
    return inst_charts_info


def grab_parts(instruments,
               charts,
               issue_dir,
               lib_dir,
               SPLITSORT,):
    for instrument in instruments:
        inspath = os.path.join(issue_dir, instrument['slug'])
        os.makedirs(inspath)
        if instrument['div'] == 1:
            print(f"Generating {instrument['name']} folder!")
            print("===================")
            divdict = grab_instrument_parts(
                instrument,
                charts,
                lib_dir,
                issue_dir
                )
        else:
            print(f"Generating {instrument["name"]} folders!")
            print("========================")
            divdict = grab_instrument_parts(
                instrument,
                charts,
                lib_dir,
                issue_dir
                )
            # divdict = {}
            # for chart in charts:
            #     for root, dirs, files in os.walk(inspath):
            #         divct = 0
            #         for file in files:
            #             if chart.slug in file:
            #                 divct += 1
            #         divdict[chart] = divct
            for book in SPLITSORT[instrument['div']]:
                bpath = os.path.join(issue_dir,
                                     instrument["slug"],
                                     book["name"]
                                     )
                if not os.path.exists(bpath):
                    os.makedirs(bpath)
                print(f"{instrument["name"]} {book["name"]}:")
                for chart in divdict:
                    chart_part_divs = divdict[chart]
                    if chart_part_divs == 1:
                        for file in os.listdir(inspath):
                            if chart in file:
                                dpath = os.path.join(bpath, file)
                                source = open(os.path.join(inspath,
                                                           file
                                                           ), 'rb')
                                dest = open(dpath, 'wb')
                                shutil.copyfileobj(source, dest)
                                print(f" * added {file}")

                                source.close()
                                dest.close()
                    elif chart_part_divs > 1:
                        bookparts = book["parts"]

                        z = bookparts[(chart_part_divs - 2)]
                        for file in os.listdir(inspath):
                            if chart in file:
                                if f"{instrument['slug']}{z}" in file:
                                    dpath = os.path.join(bpath, file)
                                    source = open(os.path.join(inspath,
                                                               file
                                                               ), 'rb')
                                    dest = open(dpath, 'wb')
                                    shutil.copyfileobj(source, dest)
                                    print(f" * added {file}")
                                    source.close()
                                    dest.close()
            for item in os.listdir(inspath):
                itempath = os.path.join(inspath, item)
                if os.path.isfile(itempath):
                    os.remove(itempath)
            print("\n")
        print("\n")
        with open(
            os.path.join(
                issue_dir,
                instrument['slug'],
                "MISSING_PARTS.txt"),
                'w'
                ) as f:
            f.write(f"Missing parts for {instrument['name']}:\n")
            f.write("========================\n")
            for chart in divdict:
                if divdict[chart] == 0:
                    f.write(str(chart))
                    f.write("\n")


def assemble_books(lib,
                   lib_dir,
                   output_dir,
                   instruments,
                   ensemble_dir,
                   SPLITSORT
                   ):
    """
    Create books to hand out to ensemble members
    with charts for their instrument
    """
    issue_dir = prepare_folder(output_dir, ensemble_dir)
    print("What charts are going in this book?")
    selected_charts = lib_query(lib)
    qty = len(selected_charts)
    lowest_max_id = ((qty // 2) + (qty % 2))
    print(f"This marchpack has {qty} charts.")
    print(
        "What number would you like to assign to the last chart of the B side?"
        )
    print(
        f"""::The minimum number is {lowest_max_id}, \
            and it is recommended to choose a larger number"""
        )
    print(
        """so you have flexibility to add charts in the future. \
            Max. number is 99."""
        )
    while True:
        max_id = survey.routines.numeric("Last B ID:", decimal=False)
        if max_id < lowest_max_id:
            print(
                f"""Please choose a number equal to \
                    or greater than {lowest_max_id}."""
                    )
        elif max_id > 99:
            print("Please choose a number less than 100.")
        else:
            break
    # parts_in_book = list_parts(selected_charts, lib_dir)
    grab_parts(instruments,
               selected_charts,
               issue_dir,
               lib_dir,
               SPLITSORT
               )
    return selected_charts, issue_dir, max_id
