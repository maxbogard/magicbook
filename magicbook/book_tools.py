import os
import shutil
import datetime

from library_tools import strip_part_filename


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


def parts_grabber(parts, ins_slug, out_slug, input, output):
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


def grab_instrument_parts(instrument, charts, input, output):
    inst_charts_info = {}
    for chart in charts:
        n = parts_grabber(
            list_parts(chart, input),
            instrument['slug'],
            instrument['slug'],
            input,
            output
            )
        # n = 0
        # parts = list_parts(chart, input)
        # p_slugs_found = []
        # for c_slug, p_slug, fil in parts:
        #     if f" {instrument['slug']}" in p_slug:
        #         # space character filters out an instrument[slug] that is
        #         # potentially a substring of another instrument[slug]
        #         with open(os.path.join(input, c_slug, fil), 'rb') as source:
        #             with open(os.path.join(output,
        #                                    instrument['slug'],
        #                                    (c_slug + p_slug)
        #                                    ), 'wb') as dest:
        #                 shutil.copyfileobj(source, dest)
        #                 p_slug_short = strip_part_filename(p_slug, c_slug)
        #                 print(f" - added {c_slug} {p_slug_short}")

        #         # this should stop portrait and landscape parts from
        #         # being counted as separate parts
        #         if p_slug_short not in p_slugs_found:
        #             n += 1
        #         p_slugs_found.append(p_slug_short)
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
        SPLITSORT: dict,
        ) -> str:
    """
    Create books to hand out to ensemble members
    with charts for their instrument
    """
    issue_dir = prepare_folder(output_dir, ensemble_dir)

    # parts_in_book = list_parts(selected_charts, lib_dir)
    grab_parts(
        instruments,
        selected_charts,
        issue_dir,
        lib_dir,
        SPLITSORT
        )
    return issue_dir
