"""
This module takes the pdfs in the output.pdf folder and imposes them
into a single pdf per part for printing.
"""

import os
import pypdf
import library_tools
from library_tools import Chart, strip_part_filename
from toc_tools import compile_toc_data, create_toc
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from constants import (SPLITSORT,
                       LYRE_PAPER_X,
                       LYRE_PAPER_Y,
                       LYRE_CONTENT_X,
                       LYRE_CONTENT_Y,
                       #    LETTER_MARGIN_X,
                       #    LETTER_MARGIN_Y,
                       MARCHPACK_FORMATS,
                       BINDER_FORMATS
                       )


def count_pdf_pages(pdf_path: str) -> int:
    """
    Returns the number of pages in a pdf
    """
    with open(pdf_path, 'rb') as pdf:
        pdf_reader = pypdf.PdfReader(pdf)
        num_pages = pdf_reader.get_num_pages()
        pdf_reader.close()
        print(num_pages)
        return num_pages


class Part(Chart):
    def __init__(self, chart: Chart, part_title, page_id, part_path, format):
        super().__init__(chart.slug, chart.is_single, chart.sl, chart.title)
        self.part_title = part_title
        self.page_id = page_id
        self.part_path = part_path
        self.format = format
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
            book_paths.append(os.path.join(
                source_dir,
                f"{instrument['slug']}{instrument['div']}"
                ))
        else:
            raise ValueError("""an instrument can't be divided into
                             less than one part!
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
            list_of_paths.append(os.path.join(source_dir,
                                              instrument['slug'],
                                              n['name']
                                              ))
    else:
        raise ValueError("""an instrument can't be divided into
                         less than one part!
                         check your ensemble json file!""")
    return list_of_paths


def impose_and_merge_portrait(part: Part,
                              format: str,
                              blanks: int,
                              output_name: str,
                              toc=None):
    pass


def merge_parts(parts: list):
    """
    given a list of Parts, merges all parts into a single PDF
    and returns the merged PDF and a list of chart IDs
    """

    print("merging parts using new function....")

    merged_parts = BytesIO()

    list_of_stamps = []
    counter = 0
    merger = pypdf.PdfWriter()
    for part in parts:
        merger.append(part.part_path)
        for n in range(0, (merger.get_num_pages() - counter)):
            list_of_stamps.append(part.page_id)
        counter = merger.get_num_pages()
    merger.write(merged_parts)
    merger.close()

    return merged_parts, list_of_stamps


def create_stamp(stamp,
                 stamp_location: str,
                 paper_size: tuple,
                 stamp_font: str,
                 stamp_size: int):
    """
    Given the paper size, stamp location and a list of stamps,
    creates a series of stamps that can be merged onto a
    book of parts post-scaling
    """

    stamp_packet = BytesIO()

    can = canvas.Canvas(stamp_packet, paper_size)
    can.setFont(stamp_font, stamp_size)
    if stamp_location == 'bottom_right':
        can.drawRightString(
            (paper_size[0] - 5),
            5,
            stamp
            )
    elif stamp_location == 'top_right':
        can.drawRightString(
            (paper_size[0] - 5),
            (paper_size[1] - (stamp_size + 5)),
            stamp
            )
    can.save()

    return stamp_packet


def impose_and_merge(
        parts: list,
        blanks: int,
        output_name: str,
        format: str,
        toc=None,
        prefix=None
        ):
    """
    merges the pdfs from a list of parts, and adds n blank pages to the end
    calls create_stamp to add a chart ID to each page as well
    then subsequently scales all pages to fit on selected paper
    """

    if format in MARCHPACK_FORMATS:
        paper_x = LYRE_PAPER_X
        paper_y = LYRE_PAPER_Y
        content_x = LYRE_CONTENT_X
        content_y = LYRE_CONTENT_Y
        stamp_location = 'bottom_right'
        stamp_size = 30
    elif format in BINDER_FORMATS:
        paper_x = letter[0]
        paper_y = letter[1]
        content_x = paper_x
        content_y = paper_y
        # content_x = (paper_x - (LETTER_MARGIN_X * 2))
        # content_y = (paper_y - (LETTER_MARGIN_Y * 2))
        stamp_location = 'top_right'
        stamp_size = 40

    new_bytes_object = BytesIO()

    new_bytes_object, list_of_stamps = merge_parts(parts)

    # note: at this pointin the code new_bytes_object stores the merged PDFs,
    # without any scaling or stamping

    reader = pypdf.PdfReader(new_bytes_object)
    writer = pypdf.PdfWriter()

    # if a table of contents is provided to the function,
    # it is the first PDF added
    # to the merged and imposed PDF
    # note that for this to work, we need to always
    # provide a TOC that is pre-scaled!
    if toc is not None:
        toc_reader = pypdf.PdfReader(toc)
        toc_page = toc_reader.get_page(0)
        writer.add_page(toc_page)
        toc_reader.close()

    # executes the code on each page in the
    for n in range(0, reader.get_num_pages()):
        # opens the PDF stored in the buffer (merged unscaled parts)
        packet = BytesIO()

        packet = create_stamp(list_of_stamps[n],
                              stamp_location,
                              (paper_x, paper_y),
                              "Helvetica-Bold",
                              stamp_size)

        page = reader.get_page(n)

        # if the page was cropped, this makes sure
        # we operate on the cropped dimensions
        page.mediabox = page.cropbox

        # moves the content to start at 0,0
        xt = (page.mediabox.left * -1)
        yt = (page.mediabox.bottom * -1)
        trans = pypdf.Transformation().translate(tx=xt, ty=yt)
        page.add_transformation(trans)

        # set of operations to move the mediabox and cropbox
        # to the new location of the content
        newx = page.mediabox.width
        newy = page.mediabox.height
        page.cropbox = pypdf.generic.RectangleObject((0, 0, newx, newy))
        page.mediabox = page.cropbox
        h = float(page.mediabox.height)
        w = float(page.mediabox.width)

        # scales to fit the page while maintaining aspect ratio
        scale_factor = min(content_x / w, content_y / h)
        transform = pypdf.Transformation().scale(scale_factor, scale_factor)
        page.add_transformation(transform)

        page.cropbox = pypdf.generic.RectangleObject([0, 0, paper_x, paper_y])

        print(f"{list_of_stamps[n]}: {h}")
        # opens the previously created stamp from the packet
        new_pdf = pypdf.PdfReader(packet)
        page_new = new_pdf.get_page(0)
        page.mediabox = page_new.mediabox

        # merges the page onto the stamp
        page_new.merge_transformed_page(
            page,
            pypdf.Transformation().translate(
                tx=0,
                ty=((content_y - (h * scale_factor)) / 2)
            ))
        writer.add_page(page_new)
        packet.close()

    # for loop finshed, now appends blank page
    # to the end of the PDF to balance it with
    # the opposite side of the marchpack
    if blanks > 0:
        for n in range(0, blanks):
            writer.add_blank_page(width=paper_x, height=paper_y)
    writer.write(output_name)
    writer.close()
    reader.close()
    new_bytes_object.close()


def impose_for_printing(path_to_a: str,
                        path_to_b: str,
                        final_output_path: str):
    """
    Places the marchpacks onto US Letter paper for printing, with the
    A side on the top of each page and the B side on the bottom.
    """
    if os.path.exists(os.path.dirname(final_output_path)) is False:
        os.makedirs(os.path.dirname(final_output_path))
    reader_n = pypdf.PdfReader(path_to_a)
    # num_of_pages = reader_n.get_num_pages()

    writer = pypdf.PdfWriter()

    reader_a = pypdf.PdfReader(path_to_a)
    reader_b = pypdf.PdfReader(path_to_b)

    for pg in range(0, reader_n.get_num_pages()):
        reader_template = pypdf.PdfReader(
            "config/templates/trim-guides.pdf"
            )
        page = reader_template.get_page(0)
        a_page = reader_a.get_page(pg)
        b_page = reader_b.get_page(pg)
        page.merge_transformed_page(
            a_page,
            pypdf.Transformation().translate(tx=54, ty=396),
            False)
        page.merge_transformed_page(
            b_page,
            pypdf.Transformation().rotate(180).translate(tx=558, ty=396),
            False)
        writer.add_page(page)
        reader_template.close()

    writer.write(final_output_path)
    reader_a.close()
    reader_b.close()

    writer.close()
    reader_n.close()


def select_chart_order(charts: list[Chart], abside: bool) -> list[dict]:
    """
    Takes a list of charts and asks the user to select how they should be
    ordered in the book. Can either order A/B based on side of the marchpack,
    or a non-prefixed numerical value
    """
    charts_rem = charts.copy()
    if abside is True:
        marchpack_pages = (len(charts_rem) // 2)
        marchpack_rem = (len(charts_rem) % 2)
        print('select charts for A side, in order from first to last')
        a_index = {}
        a_id = 1
        for n in range(0, (marchpack_pages)):
            chart = library_tools.lib_single_query(
                charts_rem,
                pageid=f"A{a_id}"
                )
            charts_rem.remove(chart)
            a_index[a_id] = chart
            a_id += 1
        print('select charts for B side, in order from first to last')
        b_index = {}
        b_id = 1
        for n in range(0, (marchpack_pages + marchpack_rem)):
            chart = library_tools.lib_single_query(
                charts_rem,
                pageid=f"B{a_id}"
                )
            charts_rem.remove(chart)
            b_index[b_id] = chart
            b_id += 1

        return [a_index, b_index]
    else:
        book_pages = len(charts_rem)
        print('select charts in order from first to last')
        x_index = {}
        x_id = 1
        for n in range(0, book_pages):
            chart = library_tools.lib_single_query(
                charts_rem,
                pageid=f"{x_id}"
                )
            charts_rem.remove(chart)
            x_index[x_id] = chart
            x_id += 1
        return [x_index]


def auto_order_charts(charts: list[Chart], abside: bool) -> list[dict]:
    """
    Automatically orders the charts in the order they are received
    returns a list of one or two chart indices
    """
    charts_rem = charts.copy()
    if abside is True:
        marchpack_pages = (len(charts_rem) // 2)
        marchpack_rem = (len(charts_rem) % 2)
        a_index = {}
        a_id = 1
        for n in range(0, (marchpack_pages)):
            a_index[a_id] = charts_rem.pop(0)
            a_id += 1
        b_index = {}
        b_id = 1
        for n in range(0, (marchpack_pages + marchpack_rem)):
            b_index[b_id] = charts_rem.pop(0)
            b_id += 1

        return [a_index, b_index]
    else:
        book_pages = len(charts_rem)
        x_index = {}
        x_id = 1
        for n in range(0, book_pages):
            x_index[x_id] = charts_rem.pop(0)
            x_id += 1
        return [x_index]


def pdf_path_list(path: str, index: dict, format: str, prefix=None) -> list:
    """
    given an index, rturns a list of pdf paths
    """
    for f in MARCHPACK_FORMATS:
        if format is f:
            preferred_format = "LYRE"
            other_format = "PORTRAIT"
        else:
            preferred_format = "PORTRAIT"
            other_format = "LYRE"

    if prefix is None:
        pre = ''
    else:
        pre = prefix

    pdf_list = []
    pdf_pages = 0
    for chart_id in index.keys():
        prefer_find = []
        other_find = []
        for file in os.listdir(path):
            if index[chart_id].slug in file:
                if preferred_format in file:
                    print(f"found {index[chart_id].slug}")
                    print(f"in file {file}")
                    prefer_find.append(file)
                else:
                    other_find.append(file)
        for part in prefer_find:
            print(f"part in prefer_find: {part}")

            part_slug = strip_part_filename(
                part,
                index[chart_id].slug
            )
            part_obj = Part(
                index[chart_id],
                part_slug,
                f'{pre}{chart_id}',
                os.path.join(path, part),
                preferred_format
            )
            pdf_list.append(part_obj)
            pdf_pages += part_obj.pagect
        for part in other_find:
            part_slug = strip_part_filename(
                part,
                index[chart_id].slug
            )
            print(f"found non-preferred format {part_slug}")
            if any(part_slug in s for s in prefer_find) is False:
                part_obj = Part(
                    index[chart_id],
                    part_slug,
                    f'{pre}{chart_id}',
                    os.path.join(path, part),
                    other_format
                    )
                pdf_list.append(part_obj)
                pdf_pages += part_obj.pagect
    return pdf_list, pdf_pages


def merge_marchpacks(
        charts: list,
        custom_order: bool,
        source_dir: str,
        ensemble_info: dict,
        max_id: int,
        book_format: str
        ):
    """
    For each instrument, assembles all parts into a single pdf,
    with a specified order and page size.
    """

    # !!! function settings here
    # - eventually these should be passed through arguments
    add_toc = True
    # book_format = 'MarchpackComprehensive'

    # !!!

    if custom_order is True:
        book_index = select_chart_order(charts, custom_order)
    else:
        book_index = auto_order_charts(charts)

    # temporary before refactoring
    a_index = book_index[0]
    b_index = book_index[1]

    for instrument in ensemble_info['instruments']:
        if instrument['div'] == 1:
            path = os.path.join(source_dir, instrument['slug'])
            print(f'merging {instrument["name"]} book')

            a_parts, a_pages = pdf_path_list(
                path,
                a_index,
                book_format,
                prefix='A'
                )
            b_parts, b_pages = pdf_path_list(
                path,
                b_index,
                book_format,
                prefix='B'
                )

            assemble_path = f"{source_dir}/temp/{instrument['slug']}"

            os.makedirs(assemble_path)

            if add_toc is True:
                a_pages += 1
                toc_data = compile_toc_data(charts, a_parts, b_parts)
                toc_path = create_toc(ensemble_info['name'],
                                      instrument['name'],
                                      book_format,
                                      assemble_path,
                                      toc_data)

            if a_pages > b_pages:
                x_pages = a_pages - b_pages
                # merge pdfs with blank pages on b side
                impose_and_merge(a_parts,
                                 0,
                                 f"{assemble_path}/A.pdf",
                                 book_format,
                                 toc=toc_path,
                                 prefix='A')
                impose_and_merge(b_parts,
                                 x_pages,
                                 f"{assemble_path}/B.pdf",
                                 book_format,
                                 prefix='B')
                impose_for_printing(
                    f"{assemble_path}/A.pdf",
                    f"{assemble_path}/B.pdf",
                    f"{source_dir}/output/{instrument['slug']}.pdf"
                    )
            else:
                x_pages = b_pages - a_pages
                # merge pdfs with blank pages on a side
                impose_and_merge(a_parts,
                                 x_pages,
                                 f"{assemble_path}/A.pdf",
                                 book_format,
                                 toc=toc_path,
                                 prefix='A')
                impose_and_merge(b_parts,
                                 0,
                                 f"{assemble_path}/B.pdf",
                                 book_format,
                                 prefix='B')

            if book_format in MARCHPACK_FORMATS:
                impose_for_printing(
                    f"{assemble_path}/A.pdf",
                    f"{assemble_path}/B.pdf",
                    f"{source_dir}/output/{instrument['slug']}.pdf"
                                    )
            else:
                if os.path.exists(f"{source_dir}/output/") is False:
                    os.makedirs(f"{source_dir}/output/")
                merger = pypdf.PdfWriter()

                for pdf in [
                        f"{assemble_path}/A.pdf",
                        f"{assemble_path}/B.pdf"
                        ]:
                    merger.append(pdf)

                merger.write(f"{source_dir}/output/{instrument['slug']}.pdf")
                merger.close()

        elif instrument['div'] < 1:
            raise ValueError("""an instrument can't be divided
                             into less than one part!
                            check your ensemble json file!""")
        else:
            for book in SPLITSORT[instrument['div']]:
                path = os.path.join(source_dir,
                                    instrument['slug'],
                                    book['name'])
                print(f"merging{instrument['name']} {book['name']}:")

                a_parts, a_pages = pdf_path_list(path, a_index, book_format)
                b_parts, b_pages = pdf_path_list(path, b_index, book_format)

                assemble_path = f"""{source_dir}/temp/\
                {instrument['slug']}{book['name']}"""

                os.makedirs(assemble_path)

                if add_toc is True:
                    a_pages += 1
                    toc_data = compile_toc_data(charts, a_parts, b_parts)
                    toc_path = create_toc(
                        ensemble_info['name'],
                        f"{instrument['name']} {book['name']}",
                        book_format,
                        assemble_path,
                        toc_data
                        )

                if a_pages > b_pages:
                    x_pages = a_pages - b_pages
                    # merge pdfs with blank pages on b side
                    impose_and_merge(a_parts,
                                     0,
                                     f"{assemble_path}/A.pdf",
                                     book_format,
                                     toc=toc_path,
                                     prefix='A'
                                     )
                    impose_and_merge(b_parts,
                                     x_pages,
                                     f"{assemble_path}/B.pdf",
                                     book_format,
                                     prefix='B'
                                     )
                else:
                    x_pages = b_pages - a_pages
                    # merge pdfs with blank pages on a side
                    impose_and_merge(a_parts,
                                     x_pages,
                                     f"{assemble_path}/A.pdf",
                                     book_format,
                                     toc=toc_path,
                                     prefix='A'
                                     )
                    impose_and_merge(b_parts,
                                     0,
                                     f"{assemble_path}/B.pdf",
                                     book_format,
                                     prefix='B'
                                     )
                pdfname = f'{instrument['slug']}{book['name']}.pdf'

                if book_format in MARCHPACK_FORMATS:
                    impose_for_printing(
                        f"{assemble_path}/A.pdf",
                        f"{assemble_path}/B.pdf",
                        f"{source_dir}/output/{pdfname}"
                        )
                else:
                    if os.path.exists(f"{source_dir}/output/") is False:
                        os.makedirs(f"{source_dir}/output/")
                    merger = pypdf.PdfWriter()

                    for pdf in [
                            f"{assemble_path}/A.pdf",
                            f"{assemble_path}/B.pdf"
                            ]:
                        merger.append(pdf)

                    merger.write(f"{source_dir}/output/{pdfname}")
                    merger.close()
