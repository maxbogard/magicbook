"""
This module takes the pdfs in the output.pdf folder and imposes them
into a single pdf per part for printing.
"""

import os
import pypdf
# import library_tools
import json
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from .library_tools import Chart, strip_part_filename, create_chart_object
from .toc_tools import compile_toc_data, create_toc
from .constants import (SPLITSORT,
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
    def __init__(
            self,
            chart: Chart,
            part_title,
            page_id,
            part_path,
            format,
            prefix=None
            ):
        super().__init__(chart.slug, chart.is_single, chart.sl, chart.title)
        self.part_title = part_title
        self.page_id = page_id
        self.part_path = part_path
        self.format = format
        self.pagect = count_pdf_pages(part_path)
        self.prefix = prefix


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


def impose_and_merge_portrait(
        part: Part,
        format: str,
        blanks: int,
        output_name: str,
        toc: BytesIO = None
        ):
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


def create_stamp(
        stamp,
        stamp_location: str,
        paper_size: tuple,
        stamp_font: str,
        stamp_size: int,
        prefix: str
        ):
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
            (stamp_size + 5),
            prefix
        )
        can.drawRightString(
            (paper_size[0] - 5),
            5,
            stamp
            )
    elif stamp_location == 'top_right':
        can.drawRightString(
            (paper_size[0] - 10),
            (paper_size[1] - (stamp_size + 5)),
            f"{prefix}{stamp}"
            )
    can.save()

    return stamp_packet


def impose_and_merge(
        parts: list,
        blanks: int,
        output_name: str,
        format: str,
        toc: BytesIO = None,
        prefix=None
        ) -> BytesIO:
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
                              stamp_size,
                              prefix)

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

        # moves content as close to centered on the page x axis as possible
        # without overlapping the right margin area.
        trans_x = ((paper_x - (w * scale_factor)) / 2)
        if trans_x + (w * scale_factor) > content_x:
            trans_x = ((content_x - (w * scale_factor)) / 2)

        # merges the page onto the stamp
        page_new.merge_transformed_page(
            page,
            pypdf.Transformation().translate(
                tx=trans_x,
                ty=((content_y - (h * scale_factor)) / 2),
            ),
            False
            )
        writer.add_page(page_new)
        packet.close()

    # for loop finshed, now appends blank page
    # to the end of the PDF to balance it with
    # the opposite side of the marchpack
    if blanks > 0:
        for n in range(0, blanks):
            writer.add_blank_page(width=paper_x, height=paper_y)
    bytes_output = BytesIO()
    writer.write(bytes_output)
    writer.close()
    reader.close()
    new_bytes_object.close()

    return bytes_output


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
                str(part),
                str(index[chart_id].slug)
            )
            part_obj = Part(
                index[chart_id],
                part_slug,
                f'{chart_id}',
                os.path.join(path, part),
                preferred_format,
                prefix=str(pre)
            )
            pdf_list.append(part_obj)
            pdf_pages += part_obj.pagect
        for part in other_find:
            part_slug = strip_part_filename(
                str(part),
                str(index[chart_id].slug)
            )
            print(f"found non-preferred format {part_slug}")
            if any(part_slug in s for s in prefer_find) is False:
                part_obj = Part(
                    index[chart_id],
                    part_slug,
                    f'{chart_id}',
                    os.path.join(path, part),
                    other_format,
                    str(pre)
                    )
                pdf_list.append(part_obj)
                pdf_pages += part_obj.pagect
    return pdf_list, pdf_pages


def merge_marchpacks(
        charts: list,
        source_dir: str,
        book_format: str
        ):
    """
    For each instrument, assembles all parts into a single pdf,
    with a specified order and page size.
    """

    with open(os.path.join(source_dir, 'book-info.json')) as b:
        book_info = json.load(b)

    raw_dir = os.path.join(source_dir, book_info['files']['raw'])
    imposed_dir = os.path.join(source_dir, book_info['files']['imposed'])

    if imposed_dir is False:
        os.makedirs(imposed_dir)

    max_id = book_info['max_id']
    # custom_order = book_info['custom_order']
    abside = book_info['abside']

    # !!! function settings here
    # - eventually these should be passed through arguments
    add_toc = True
    # book_format = 'MarchpackComprehensive'

    c_list = []

    if abside is True:
        a_index = {}
        a_id = 1
        for c in book_info['charts'][0]:
            a_index[a_id] = create_chart_object(c)
            a_id += 1
        b_index = {}
        b_id = ((max_id - len(a_index)) + 1)
        for c in book_info['charts'][1]:
            b_index[b_id] = create_chart_object(c)
            b_id += 1
        for c in a_index.values():
            c_list.append(c)
        for c in b_index.values():
            c_list.append(c)
    else:
        x_index = {}
        x_id = 1
        for c in book_info['charts'][0]:
            x_index[x_id] = create_chart_object(c)
            x_id += 1
        for c in x_index.values():
            c_list.append(c)

    for instrument in book_info['instruments']:
        if instrument['div'] == 1:
            path = os.path.join(raw_dir, instrument['slug'])
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

            assemble_path = (
                f"{imposed_dir}/{book_format}/{instrument['slug']}"
                )

            a_pgs = BytesIO()
            b_pgs = BytesIO()
            toc_pg = BytesIO()

            if add_toc is True:
                a_pages += 1
                toc_data = compile_toc_data(c_list, a_parts, b_parts)
                toc_pg = create_toc(
                    book_info['ensemble'],
                    instrument['name'],
                    book_format,
                    assemble_path,
                    toc_data
                    )

            if a_pages > b_pages:
                x_pages = a_pages - b_pages
                # merge pdfs with blank pages on b side
                a_pgs = impose_and_merge(
                    a_parts,
                    0,
                    f"{assemble_path}/A.pdf",
                    book_format,
                    toc=toc_pg,
                    prefix='A')
                b_pgs = impose_and_merge(
                    b_parts,
                    x_pages,
                    f"{assemble_path}/B.pdf",
                    book_format,
                    prefix='B')

            else:
                x_pages = b_pages - a_pages
                # merge pdfs with blank pages on a side
                a_pgs = impose_and_merge(
                    a_parts,
                    x_pages,
                    f"{assemble_path}/A.pdf",
                    book_format,
                    toc=toc_pg,
                    prefix='A'
                    )
                b_pgs = impose_and_merge(
                    b_parts,
                    0,
                    f"{assemble_path}/B.pdf",
                    book_format,
                    prefix='B'
                    )

            pdfname = f'{instrument['slug']}.pdf'

            if book_format in MARCHPACK_FORMATS:
                impose_for_printing(
                    a_pgs,
                    b_pgs,
                    f"{imposed_dir}/{book_format}/{pdfname}"
                    )
            else:
                if os.path.exists(
                        f"{imposed_dir}/{book_format}/"
                        ) is False:
                    os.makedirs(f"{imposed_dir}/{book_format}/")
                merger = pypdf.PdfWriter()

                for pdf in [
                        a_pgs,
                        b_pgs
                        ]:
                    merger.append(pdf)

                merger.write(
                    f"{imposed_dir}/{book_format}/{pdfname}"
                    )
                merger.close()

        elif instrument['div'] < 1:
            raise ValueError("""an instrument can't be divided
                             into less than one part!
                            check your ensemble json file!""")
        else:
            for book in SPLITSORT[instrument['div']]:
                path = os.path.join(
                    raw_dir,
                    instrument['slug'],
                    book['name']
                    )
                print(f"merging{instrument['name']} {book['name']}:")

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
                    prefix='B')

                assemble_path = os.path.join(
                    imposed_dir,
                    book_format,
                    f'{instrument['slug']}{book['name']}'
                )

                if add_toc is True:
                    a_pages += 1
                    toc_data = compile_toc_data(
                        c_list,
                        a_parts,
                        b_parts
                        )
                    toc_pg = create_toc(
                        book_info['ensemble'],
                        f"{instrument['name']} {book['name']}",
                        book_format,
                        assemble_path,
                        toc_data
                        )

                if a_pages > b_pages:
                    x_pages = a_pages - b_pages
                    # merge pdfs with blank pages on b side
                    a_pgs = impose_and_merge(
                        a_parts,
                        0,
                        f"{assemble_path}/A.pdf",
                        book_format,
                        toc=toc_pg,
                        prefix='A'
                        )
                    b_pgs = impose_and_merge(
                        b_parts,
                        x_pages,
                        f"{assemble_path}/B.pdf",
                        book_format,
                        prefix='B'
                        )
                else:
                    x_pages = b_pages - a_pages
                    # merge pdfs with blank pages on a side
                    a_pgs = impose_and_merge(
                        a_parts,
                        x_pages,
                        f"{assemble_path}/A.pdf",
                        book_format,
                        toc=toc_pg,
                        prefix='A'
                        )
                    b_pgs = impose_and_merge(
                        b_parts,
                        0,
                        f"{assemble_path}/B.pdf",
                        book_format,
                        prefix='B'
                        )
                pdfname = f'{instrument['slug']}{book['name']}.pdf'

                if book_format in MARCHPACK_FORMATS:
                    impose_for_printing(
                        a_pgs,
                        b_pgs,
                        f"{imposed_dir}/{book_format}/{pdfname}"
                        )
                else:
                    if os.path.exists(
                            f"{imposed_dir}/{book_format}/"
                            ) is False:
                        os.makedirs(f"{imposed_dir}/{book_format}/")
                    merger = pypdf.PdfWriter()

                    for pdf in [
                            a_pgs,
                            b_pgs
                            ]:
                        merger.append(pdf)

                    merger.write(
                        f"{imposed_dir}/{book_format}/{pdfname}"
                        )
                    merger.close()
