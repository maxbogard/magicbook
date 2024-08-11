import os
import json
import jsonschema
import survey

from constants import PAGE_FORMATS


class Song:
    def __init__(self, title: str, artist: str = None, arranger: str = None):
        self.title = title
        self.artist = artist
        self.arranger = arranger


class Chart:
    def __init__(self,
                 slug: str,
                 is_single: bool,
                 sl: list,
                 t=None):
        self.slug = slug
        self.is_single = is_single
        self.sl = sl
        songs = []
        for s in sl:
            entry = object.__new__(Song)
            entry.__dict__ = s
            songs.append(entry)
        self.songs = songs
        if is_single is True:
            self.title = sl[0]['title']
        else:
            self.title = t

    def __str__(self):
        """
        if chart is a single, returns its song title
        otherwise, returns the chart title
        """
        return self.title

    def path(self, libdir):
        return os.path.join(libdir, self.slug)


def strip_part_filename(
        file,
        chart_name
        ) -> str:
    """
    returns only the name of the part (no chart name or .pdf)
    """
    part_core = str(file).removeprefix(chart_name).removesuffix(".pdf")
    for format in PAGE_FORMATS:
        if format in part_core:
            return part_core.removeprefix(
                f" {format} "
                )
    return part_core


# this function is user i/o, has been replaced by a new function
# in simple_io_tools.py

# def lib_query(lib) -> list[Chart]:
#     """
#     Prompts the user to select one or more charts

#     Returns:
#         a list of charts, in object form
#     """
#     while True:
#         choices = []
#         for cha in lib:
#             print(cha)
#             print(cha.title)
#             choices.append(cha.title)
#         print(choices)
#         selection = survey.routines.basket('SELECT CHARTS:', options=choices)
#         print("\n")
#         selected = []
#         for c in selection:
#             # selected.append(choices[c])
#             selected.append(lib[c])
#         print("You have selected the following charts:")
#         for s in selected:
#             print(f" - {s.title}")
#         if survey.routines.inquire("Is this correct?", default=True) is True:
#             break
#     return selected


def lib_single_query(loc, pageid="", prefix=None):
    """
    prompts the user to select a single chart from a list of charts
    optional input to specify the page ID
    """
    if prefix is None:
        pre = ""
    else:
        pre = f"{prefix}"
    choices = []
    for cha in loc:
        choices.append(cha.title)
    selection = survey.routines.select(
        f'SELECT CHART: {pre}{pageid}',
        options=choices
        )
    print("\n")
    selected = loc[selection]
    if pageid is True:
        print(f"{pageid}: - {selected.title}")
    return selected


def show_chart_details(chart, lib):
    """
    Prints the details of a chart to the standard output
    """
    pass


def audit_chart_json(chart: str, infopath: str, scmpath: str):
    """
    Validates a chart's info.json file against the schema
    """
    with open(scmpath) as schema:
        chartschema = json.load(schema)
    with open(infopath) as info:
        chartinfo = json.load(info)
    try:
        jsonschema.validate(instance=chartinfo, schema=chartschema)
    except Exception as err:
        print(f'{chart} info.json falied validation')
        print(err)
        return False, None
    else:
        print(
            f'{chart} info.json passed validation'
        )
        chart_obj = Chart(chartinfo['slug'],
                          chartinfo['is_single'],
                          chartinfo['songs'],
                          t=chartinfo.get('title'))
        return True, chart_obj


def audit_library(libdir: str, scmpath: str) -> bool | int | int:
    """
    Checks each chart in the library for a valid info.json file

    Args:
        libdir: path pointing to the library directory
        schmdir: path pointing to the schema directory

    Returns:
        integers x, t
        where x = number of charts failing audit,
          and t = total number of charts in library
    """
    x = 0
    t = 0
    chart_list = []
    for chart in sorted(os.listdir(libdir)):
        chartpath = os.path.join(libdir, chart)
        infopath = os.path.join(chartpath, "info.json")
        if os.path.isdir(chartpath):
            t += 1
            if os.path.isfile(infopath):
                r, chart_obj = audit_chart_json(chart, infopath, scmpath)
                if r is True:
                    chart_list.append(chart_obj)
                    continue
                else:
                    x += 1
            else:
                x += 1
                print(f'{chart} is missing info.json file')
    if x == 0:
        return True, x, t, chart_list
    else:
        return False, x, t, chart_list
