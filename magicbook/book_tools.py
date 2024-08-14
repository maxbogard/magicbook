import os
import shutil
import datetime
import json

from .library_tools import strip_part_filename

# should instruments even bee a class? not sure what benefit is gained over
# reading from a dictionary.

# class Instrument:
#     def __init__(self, slug, name, divs):
#         self.slug = slug
#         self.name = name
#         self.divs = divs


def list_books(
        output_dir: str,
        ):
    book_list = []
    for dir in os.listdir(output_dir):
        for subdir in os.listdir(os.path.join(output_dir, dir)):
            if os.path.exists(
                    os.path.join(
                        output_dir,
                        dir,
                        subdir,
                        "book-info.json"
                        )
                    ):
                with open(
                    os.path.join(
                            output_dir,
                            dir,
                            subdir,
                            "book-info.json"
                            ),
                        'r') as f:
                    book_data = json.load(f)
                book_list.append([subdir, book_data["ensemble"]])

    return book_list


def prepare_folder(
        output_dir: str,
        ensemble_dir: str
        ) -> tuple[str, str, str]:
    """
    Creates a directory for the book charts (both raw copied PDFs and imposed
    final output) to be stored, based on the base output directory defined in
    the config file, the name of the ensemble, and the time the books were
    issued.
    """
    ensemble_loc = os.path.join(output_dir, ensemble_dir)
    is_existing = os.path.exists(ensemble_loc)
    if not is_existing:
        os.makedirs(ensemble_loc)

    isnow = datetime.datetime.now()
    issued = isnow.strftime("%Y-%m-%d %H%M%S")
    issue_dir = os.path.join(ensemble_loc, issued)
    raw_dir = "raw"
    imposed_dir = "imposed"

    if os.path.exists(issue_dir) is True:
        raise Exception("The output folder already exists.\
                         This should not happen!")

    os.makedirs(issue_dir)

    return issue_dir, raw_dir, imposed_dir


def list_parts(
        chart,
        lib_dir: str,
        ) -> list[tuple]:
    """
    Given a Chart, and the directory it is located in, returns a list of tuples
    containing the chart slug, the part slug, and the filename of the part.
    """
    output_list = []
    for root, dirs, files in os.walk(os.path.join(lib_dir, chart.slug)):
        for file in files:
            if file.endswith(".pdf"):
                part_slug = file.replace(chart.slug, "")
                output_list.append((chart.slug, part_slug, file))
    return output_list


def parts_grabber(
        parts: list,
        ins_slug: str,
        out_slug: str,
        input: str,
        output: str,
        ) -> int:
    """
    Given an instrument and a list of parts, copies parts for that instrument
    to a specified output directory, and returns the number of UNIQUE parts
    found. Calls the strip_part_filename function to remove formatting data
    from the part name (i.e. "PORTRAIT", "LANDSCAPE"), so it can see whether a
    part is unique, or is a different format of an already found part.
    """
    n = 0
    p_slugs_found = []
    for c_slug, p_slug, fil in parts:
        if f" {ins_slug}" in p_slug:
            # space character filters out an instrument[slug] that is
            # potentially a substring of another instrument[slug]
            with open(os.path.join(input, c_slug, fil), 'rb') as source:
                with open(os.path.join(
                        output,
                        out_slug,
                        (c_slug + p_slug)
                        ), 'wb') as dest:
                    shutil.copyfileobj(source, dest)
                    p_slug_short = strip_part_filename(p_slug, c_slug)
                    print(f" - added {c_slug} {p_slug_short}")

            # this should stop portrait and landscape parts from
            # being counted as separate parts
            if p_slug_short not in p_slugs_found:
                n += 1
            p_slugs_found.append(p_slug_short)
    return n


def grab_instrument_parts(
        instrument: dict,
        charts: list,
        input: str,
        output: str,
        ) -> dict:
    """
    For a given instrument, iterates through a list of charts:
     - for each chart, searches for relevant parts for the instrument
     - if part(s) written specifically for the instrument are found,
       it copies those parts to the instrument's directory in the
       specified output directory.
     - if no parts written specifically for the instrument are found,
       iterates through the instrument's list of alternate instruments.
       - if it finds parts for the alternate, it copies them to the folder
         and stops iterating through the list.
       - if it doesn't find parts for the alternate, moves on to the next
         alternate in the list
     - counts the number of parts found for the instrument (0 if no parts
       were found for the instrument or any of its alternates)

    Args:
        instrument (dict): a list of instrument dictionaires containing info
        about the instrument
        charts (list): a list of Chart objects (see object for details)
        input (str): the directory where the library is stored
        output (str): the directory where the parts will be copied

    Returns:
        inst_charts_info: a dictionary with chart slugs as keys and the number
        of parts found for that chart as values.
    """
    inst_charts_info = {}
    for chart in charts:
        n = parts_grabber(
            list_parts(chart, input),
            instrument['slug'],
            instrument['slug'],
            input,
            output
            )

        if n < 1:
            alternates = instrument['alternates']
            r = 0
            for alternate in alternates:
                r = parts_grabber(
                    list_parts(chart, input),
                    alternate,
                    instrument['slug'],
                    input,
                    output
                    )
                if r > 0:
                    inst_charts_info[chart.slug] = r
                    break
            if r == 0:
                print(f"!!! MISSING {chart.title}")
                inst_charts_info[chart.slug] = 0

        else:
            inst_charts_info[chart.slug] = n

    print('\n')
    return inst_charts_info


def grab_parts(
        instruments: list[dict],
        charts: list,
        issue_dir: str,
        lib_dir: str,
        SPLITSORT: dict,
        ):
    """
    Iterates a list of instruments. For each instrument:
     - calls a function to grab the relevant part(s) from the library
       for each selected chart
     - looks at instrument 'div' value to determine if one or multiple
       books should be created for each instrument.
     - If multiple books should be created for each instrument:
       - reads SPLITSORT (a dictonary of lists of dictionaries) to determine
         how to split parts when the number of available parts does not equal
         the number of books for the instrument.
       - copies the relevant parts into the appropriate book folders.
       - removes parts from the base instrument folder.
     - creates a "MISSING_PARTS.txt" file in the base instrument folder
       - if no relevant parts (either written for that instrument or an
         alternate part for another instrument) are found, writes the chart
         title to the text file.

    NOTE
     - this function is a bit of a mess and could use some refactoring.
       - (thank you copilot for suggesting this =P)
     - this function does NOT return any values in Python as of this writing.
       It copies PDFs to a directory specified in the input. The internal
       directory structure is assumed. Any function that operates on the output
       of this function needs to be aware of the internal directory structure.
    """
    for instrument in instruments:
        inspath = os.path.join(issue_dir, instrument['slug'])
        os.makedirs(inspath)

        print(f"Generating {instrument['name']} folder(s)!")
        print("===================")

        if instrument['div'] == 1:
            divdict = grab_instrument_parts(
                instrument,
                charts,
                lib_dir,
                issue_dir
                )
        else:
            divdict = grab_instrument_parts(
                instrument,
                charts,
                lib_dir,
                issue_dir
                )

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


def assemble_books(
        selected_charts: list,
        lib_dir: str,
        output_dir: str,
        instruments: list,
        ensemble_dir: str,
        ensemble_name: str,
        book_order_data: tuple[bool, int, bool],
        SPLITSORT: dict,
        ) -> str:
    """
    Create books to hand out to ensemble members
    with charts for their instrument

    Returns:
        issue_dir (str): the directory where the sorted charts are saved, based
        on the ensemble name and the date and time the books were generated
    """
    abside = book_order_data[0]
    max_id = book_order_data[1]
    custom_order = book_order_data[2]

    issue_dir, raw, imposed = prepare_folder(output_dir, ensemble_dir)

    raw_dir = os.path.join(issue_dir, raw)

    loc = []
    for d in selected_charts:
        for c in d.values():
            loc.append(c)

    # parts_in_book = list_parts(selected_charts, lib_dir)
    grab_parts(
        instruments,
        loc,
        raw_dir,
        lib_dir,
        SPLITSORT
        )

    if abside is True:
        a_list = []
        for chart in selected_charts[0].values():
            song_list = []
            for song in chart.songs:
                song_dict = {
                    "title": song.title,
                    "artist": song.artist,
                    "arranger": song.arranger,
                }
                song_list.append(song_dict)
            chart_dict = {
                "slug": chart.slug,
                "is_single": chart.is_single,
                "title": chart.title,
                "songs": song_list
            }
            a_list.append(chart_dict)

        b_list = []
        for chart in selected_charts[1].values():
            song_list = []
            for song in chart.songs:
                song_dict = {
                    "title": song.title,
                    "artist": song.artist,
                    "arranger": song.arranger,
                }
                song_list.append(song_dict)
            chart_dict = {
                "slug": chart.slug,
                "is_single": chart.is_single,
                "title": chart.title,
                "songs": song_list
            }
            b_list.append(chart_dict)
        chart_list = [a_list, b_list]
    else:
        x_list = []
        for chart in selected_charts[0].values():
            song_list = []
            for song in chart.songs:
                song_dict = {
                    "title": song.title,
                    "artist": song.artist,
                    "arranger": song.arranger,
                }
                song_list.append(song_dict)
            chart_dict = {
                "slug": chart.slug,
                "is_single": chart.is_single,
                "title": chart.title,
                "songs": song_list
            }
            x_list.append(chart_dict)
        chart_list = [x_list]

    book_data = {
        "valid_book": True,
        "files": {
            "raw": raw,
            "imposed": imposed
        },
        "ensemble": ensemble_name,
        "abside": abside,
        "max_id": max_id,
        "custom_order": custom_order,
        "instruments": instruments,
        "charts": chart_list
    }

    with open(os.path.join(issue_dir, "book-info.json"), 'w') as f:
        json.dump(book_data, f)

    return issue_dir
