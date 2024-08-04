"""
This module takes the pdfs in the output.pdf folder and imposes them into a single pdf per part for printing.
"""

import os
import pypdf
import library_tools

from constants import SPLITSORT

def count_pdf_pages(pdf_path: str) -> int:
    """
    Returns the number of pages in a pdf
    """
    with open(pdf_path, 'rb') as pdf:
        pdf_reader = pypdf.PdfReader(pdf)
        return pdf_reader.get_num_pages()

class Part(library_tools.Chart):
    def __init__(self, chart: library_tools.Chart, page_id, part_path):
        super().__init__(chart.slug, chart.is_single, chart.sl, chart.title)
        self.page_id = page_id
        self.part_path = part_path
        self.pagect = count_pdf_pages(part_path)

def get_book_paths(ensemble_info: dict, source_dir: str) -> list:
    """
    Returns a list of paths to the pdfs in the output folder
    """
    book_paths = []
    for instrument in ensemble_info['instruments']:
        if instrument['div'] == 1:
            book_paths.append(os.path.join(source_dir, instrument['slug']))
        elif instrument['div'] > 1:
            book_paths.append(os.path.join(source_dir, f"{instrument['slug']}{instrument['div']}"))
        else:
            raise ValueError("""an instrument can't be divided into less than one part!
                             check your ensemble json file!""")
    return book_paths

def get_book_path(instrument, source_dir):
    """
    Returns the a list of path to the pdfs for a single instrument
    """
    list_of_paths = []
    if instrument['div'] == 1:
        list_of_paths.append(os.path.join(source_dir, instrument['slug']))
    elif instrument['div'] > 1:
        books = SPLITSORT[instrument['div']]
        for n in books:
            list_of_paths.append(os.path.join(source_dir, instrument['slug'], n['name']))
    else:
        raise ValueError("""an instrument can't be divided into less than one part!
                            check your ensemble json file!""")
    return list_of_paths
        

def impose_and_merge(parts: list, blanks: int, output_name: str):
    """
    merges the pdfs from a list of parts, and adds n blank pages to the end
    """
    merger = pypdf.PdfWriter()
    for part in parts:
        merger.append(part.part_path)
    if blanks > 0:
        for n in range(0, blanks):
            merger.add_blank_page(width=504, height=345.6)
    merger.write(output_name)
    merger.close()


def merge_marchpacks(charts: list, custom_order: bool, source_dir: str, ensemble_info: dict):
    """
    For each instrument, assembles all parts into a single pdf,
    with a specified order and page size.
    """

    total_charts = len(charts)
    marchpack_pages = (total_charts // 2)
    marchpack_diff = (total_charts % 2)

    if custom_order is True:
        charts_rem = charts
        print("select charts for A side")
        a_index = {}
        a_id = 1
        for n in range(0, (marchpack_pages + marchpack_diff)):
            chart = library_tools.lib_single_query(charts_rem, pageid=f"A{a_id}")
            charts_rem.remove(chart)
            a_index[a_id] = chart
            a_id += 1
        b_index = {}
        b_id = 1
        print("select charts for B side")
        for n in range(0, (marchpack_pages)):
            chart = library_tools.lib_single_query(charts_rem, pageid=f"B{b_id}")
            charts_rem.remove(chart)
            b_index[b_id] = chart
            b_id += 1
    else:
        charts_rem = charts
        a_index = {}
        a_id = 1
        for n in range(0, (marchpack_pages + marchpack_diff)):
            a_index[a_id] = chart[0]
            charts_rem.pop(0)
            a_id += 1
        b_index = {}
        b_id = 1
        for n in range(0, (marchpack_pages)):
            b_index[b_id] = chart[0]
            charts_rem.pop(0)
            b_id += 1

    for instrument in ensemble_info['instruments']:
        book_paths = get_book_path(instrument, source_dir)
        print(f"{instrument}, {book_paths}")
        div = 1
        for path in book_paths:
            print(f'merging {instrument["name"]} {div} book')
            a_parts = []
            a_pages = 0
            for chart_id in a_index.keys():
                for file in os.listdir(path):
                    if a_index[chart_id].slug in file:
                        part_obj = Part(a_index[chart_id], f"A{chart_id}", os.path.join(path, file))
                        a_parts.append(part_obj)
                        a_pages += part_obj.pagect
            b_parts = []
            b_pages = 0
            for chart_id in b_index.keys():
                for file in os.listdir(path):
                    if b_index[chart_id].slug in file:
                        part_obj = Part(b_index[chart_id], f"A{chart_id}", os.path.join(path, file))
                        b_parts.append(part_obj)
                        b_pages += part_obj.pagect
            
            os.makedirs(f"{source_dir}/temp/{instrument['slug']}{div}")

            if a_pages > b_pages:
                x_pages = a_pages - b_pages
                ## merge pdfs with blank pages on b side
                impose_and_merge(a_parts, 0, f"{source_dir}/temp/{instrument['slug']}{div}/A.pdf")
                impose_and_merge(a_parts, x_pages, f"{source_dir}/temp/{instrument['slug']}{div}/B.pdf")
            else:
                x_pages = b_pages - a_pages
                ## merge pdfs with blank pages on a side
                impose_and_merge(a_parts, x_pages, f"{source_dir}/temp/{instrument['slug']}{div}/A.pdf")
                impose_and_merge(a_parts, 0, f"{source_dir}/temp/{instrument['slug']}{div}/B.pdf")
            div += 1

