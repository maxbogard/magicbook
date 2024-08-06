"""
This module takes the pdfs in the output.pdf folder and imposes them into a single pdf per part for printing.
"""

import os
import pypdf
import library_tools
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from constants import SPLITSORT, LYRE_PAPER_X, LYRE_PAPER_Y, LYRE_CONTENT_X, LYRE_CONTENT_Y

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
    merges the pdfs from a list of parts, and ads n blank pages to the end
    then subsequently scales all pages to fit on marchpack-sized paper
    """ 

    new_bytes_object = BytesIO()

    print("merging parts...")
    list_of_stamps = []
    counter = 0
    merger = pypdf.PdfWriter()
    for part in parts:
        merger.append(part.part_path)
        for n in range(0, (merger.get_num_pages() - counter)):
            list_of_stamps.append(part.page_id)
        counter = merger.get_num_pages()
    merger.write(new_bytes_object)
    merger.close()

    reader = pypdf.PdfReader(new_bytes_object)
    writer = pypdf.PdfWriter()

    for n in range(0, reader.get_num_pages()):
        packet = BytesIO()
        can = canvas.Canvas(packet, (LYRE_PAPER_X, LYRE_PAPER_Y))
        can.setFont("Helvetica-Bold", 30)
        can.drawRightString((LYRE_PAPER_X - 5), 5, list_of_stamps[n])
        can.save()
        
        page = reader.get_page(n)
        page.mediabox = page.cropbox
        xt = (page.mediabox.left * -1)
        yt = (page.mediabox.bottom * -1)
        newx = page.mediabox.width
        newy = page.mediabox.height
        trans = pypdf.Transformation().translate(tx=xt, ty=yt)
        page.add_transformation(trans)
        page.cropbox = pypdf.generic.RectangleObject((0, 0, newx, newy))
        page.mediabox = page.cropbox
        h = float(page.mediabox.height)
        w = float(page.mediabox.width)
        scale_factor = min(LYRE_CONTENT_X / w, LYRE_CONTENT_Y / h)
        transform = pypdf.Transformation().scale(scale_factor, scale_factor)
        page.add_transformation(transform)
        page.cropbox = pypdf.generic.RectangleObject([0, 0, LYRE_PAPER_X, LYRE_PAPER_Y])
        new_pdf = pypdf.PdfReader(packet)
        page_new = new_pdf.get_page(0)
        page.mediabox = page_new.mediabox
        page.merge_page(page_new)   
        writer.add_page(page)
    if blanks > 0:
        for n in range(0, blanks):
            writer.add_blank_page(width=504, height=345.6)
    writer.write(output_name)
    writer.close()
    reader.close()
    new_bytes_object.close()
    packet.close()


def impose_for_printing(path_to_a: str, path_to_b: str, final_output_path: str):
    """
    Places the marchpacks onto US Letter paper for printing, with the 
    A side on the top of each page and the B side on the bottom.
    """
    if os.path.exists(os.path.dirname(final_output_path)) is False:
        os.makedirs(os.path.dirname(final_output_path))
    reader_n = pypdf.PdfReader(path_to_a)
    num_of_pages = reader_n.get_num_pages()

    # packet = BytesIO()

    # can = canvas.Canvas(packet, letter)
    # for pg in range(0, reader_a.get_num_pages()):
    #     can.showPage()
    # can.save()

    writer = pypdf.PdfWriter()

    reader_a = pypdf.PdfReader(path_to_a)
    reader_b = pypdf.PdfReader(path_to_b)


    for pg in range(0, reader_n.get_num_pages()):
        reader_template = pypdf.PdfReader("config/templates/trim-guides.pdf")
        # base_pdf = pypdf.pdfReader(packet)
        # page = base_pdf.get_page(pg)
        page = reader_template.get_page(0)
        a_page = reader_a.get_page(pg)
        b_page = reader_b.get_page(pg)
        page.merge_transformed_page(a_page, pypdf.Transformation().translate(tx=54, ty=396), False)
        page.merge_transformed_page(b_page, pypdf.Transformation().rotate(180).translate(tx=558, ty=396), False)
        writer.add_page(page)

    
    writer.write(final_output_path)
    reader_a.close()
    reader_b.close()
    reader_template.close()
    writer.close()
    reader_n.close()
    



def merge_marchpacks(charts: list, custom_order: bool, source_dir: str, ensemble_info: dict, max_id: int):
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
        b_id = ((max_id - marchpack_pages) + 1)
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
        b_id = ((max_id - marchpack_pages) + 1)
        for n in range(0, (marchpack_pages)):
            b_index[b_id] = chart[0]
            charts_rem.pop(0)
            b_id += 1

    for instrument in ensemble_info['instruments']:
        if instrument['div'] == 1:
            path = os.path.join(source_dir, instrument['slug'])
            print(f'merging {instrument["name"]} book')
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
                        part_obj = Part(b_index[chart_id], f"B{chart_id}", os.path.join(path, file))
                        b_parts.append(part_obj)
                        b_pages += part_obj.pagect

            os.makedirs(f"{source_dir}/temp/{instrument['slug']}")

            if a_pages > b_pages:
                x_pages = a_pages - b_pages
                ## merge pdfs with blank pages on b side
                impose_and_merge(a_parts, 0, f"{source_dir}/temp/{instrument['slug']}/A.pdf")
                impose_and_merge(b_parts, x_pages, f"{source_dir}/temp/{instrument['slug']}/B.pdf")
                impose_for_printing(f"{source_dir}/temp/{instrument['slug']}/A.pdf",
                                    f"{source_dir}/temp/{instrument['slug']}/B.pdf", 
                                    f"{source_dir}/output/{instrument['slug']}.pdf"
                                    )
            else:
                x_pages = b_pages - a_pages
                ## merge pdfs with blank pages on a side
                impose_and_merge(a_parts, x_pages, f"{source_dir}/temp/{instrument['slug']}/A.pdf")
                impose_and_merge(b_parts, 0, f"{source_dir}/temp/{instrument['slug']}/B.pdf")

                impose_for_printing(f"{source_dir}/temp/{instrument['slug']}/A.pdf",
                                    f"{source_dir}/temp/{instrument['slug']}/B.pdf", 
                                    f"{source_dir}/output/{instrument['slug']}.pdf"
                                    )

        elif instrument['div'] < 1:
            raise ValueError("""an instrument can't be divided into less than one part!
                            check your ensemble json file!""")
        else:
            for book in SPLITSORT[instrument['div']]:
                path = os.path.join(source_dir, instrument['slug'], book['name'])
                print(f"merging{instrument['name']} {book['name']}:")
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
                            part_obj = Part(b_index[chart_id], f"B{chart_id}", os.path.join(path, file))
                            b_parts.append(part_obj)
                            b_pages += part_obj.pagect

                os.makedirs(f"{source_dir}/temp/{instrument['slug']}{book['name']}")  

                if a_pages > b_pages:
                    x_pages = a_pages - b_pages
                    ## merge pdfs with blank pages on b side
                    impose_and_merge(a_parts, 0, f"{source_dir}/temp/{instrument['slug']}{book['name']}/A.pdf")
                    impose_and_merge(b_parts, x_pages, f"{source_dir}/temp/{instrument['slug']}{book['name']}/B.pdf")
                else:
                    x_pages = b_pages - a_pages
                    ## merge pdfs with blank pages on a side
                    impose_and_merge(a_parts, x_pages, f"{source_dir}/temp/{instrument['slug']}{book['name']}/A.pdf")
                    impose_and_merge(b_parts, 0, f"{source_dir}/temp/{instrument['slug']}{book['name']}/B.pdf")

                impose_for_printing(f"{source_dir}/temp/{instrument['slug']}{book['name']}/A.pdf",
                                    f"{source_dir}/temp/{instrument['slug']}{book['name']}/B.pdf", 
                                    f"{source_dir}/output/{instrument['slug']}{book['name']}.pdf"
                                    )
