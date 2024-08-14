'''
Functions that produce a table of contents
given a list of charts, and page format.
'''
from io import BytesIO

from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Table,
    PageTemplate,
    # TableStyle,
    Paragraph,
    # FrameBreak
)
from reportlab.lib import colors
from reportlab.lib.enums import (
    TA_LEFT,
    # TA_RIGHT,
)
from reportlab.lib.styles import (
    ParagraphStyle,
    getSampleStyleSheet
)
from reportlab.lib.pagesizes import (
    letter
)
from .library_tools import (
    Chart,
    # Song
)
from functools import partial
from .constants import (
    LYRE_PAPER_X,
    LYRE_PAPER_Y,
    LYRE_MARGIN_X,
    LYRE_MARGIN_TOP,
    LYRE_MARGIN_BOTTOM,
    LETTER_MARGIN_X,
    LETTER_MARGIN_Y,
    MARCHPACK_FORMATS,
    BINDER_FORMATS,
)


def compile_toc_data(
        charts: list[Chart],
        a_parts: dict,
        b_parts: dict
        ) -> list[list]:
    '''
    Given a list of charts in a book, and a list of the available
    parts for each chart for a selected instrument, generates a
    table in the format of CHART NAME, PART NAME, PAGE NUMBER,
    (list of songs, if the chart isn't a single)
    '''

    # if b_parts is not None:
    #     for part in a_parts:
    #         part.page_id = f'A{part.page_id}'

    #     for part in b_parts:
    #         part.page_id = f'B{part.page_id}'

    charts.sort(key=lambda x: x.slug)
    all_parts = a_parts + b_parts

    toc_data = []

    for chart in charts:
        for part in all_parts:
            if chart.slug in part.slug:
                songs_entry = []
                if chart.is_single is False:
                    for song in part.songs:
                        songs_entry.append(song.title)
                toc_data.append(
                    [chart.title, part.part_title,
                     f"{part.prefix}{part.page_id}",
                     songs_entry]
                     )

    return toc_data


def create_toc(
        ensemble_name: str,
        book_name: str,
        format: str,
        output_loc,
        toc_data
        ):
    '''
    Given the table of contents data, generates a table of contents
    '''

    if format in MARCHPACK_FORMATS:
        # page_format = "LYRE"
        page_size = (LYRE_PAPER_X, LYRE_PAPER_Y)
        margin_x = LYRE_MARGIN_X
        margin_top = LYRE_MARGIN_TOP
        margin_bottom = LYRE_MARGIN_BOTTOM
        font_size = 9
        song_font_size = 7
        title_font_size = 14
        column_widths = [20, 145, 72]
    elif format in BINDER_FORMATS:
        # page_format = "PORTRAIT"
        page_size = letter
        margin_x = LETTER_MARGIN_X
        margin_top = LETTER_MARGIN_Y
        margin_bottom = LETTER_MARGIN_Y
        font_size = 12
        song_font_size = 10
        title_font_size = 24
        column_widths = [26, 160, 78]

    toc_output = BytesIO()

    # toc_path = f"{output_loc}/toc.pdf"
    doc = BaseDocTemplate(
        toc_output,
        pagesize=page_size,
        rightMargin=margin_x,
        leftMargin=margin_x,
        topMargin=margin_top,
        bottomMargin=margin_bottom,
        title=f"Table of Contents - {book_name}"
        )

    style_title = getSampleStyleSheet()['Title']

    style_toc_title = ParagraphStyle(
        name='TOC Title',
        parent=style_title,
        fontSize=title_font_size,
    )

    style_cell = getSampleStyleSheet()['BodyText']
    style_cell.alignment = TA_LEFT

    style_toc_h = ParagraphStyle(
        name='Chart Cell',
        parent=style_cell,
        fontName='Helvetica-Bold',
        fontSize=font_size,
        leading=font_size*1.2
    )

    style_chart = ParagraphStyle(
        name='Chart Cell',
        parent=style_cell,
        fontSize=font_size,
        leading=font_size*1.2
    )

    style_part = ParagraphStyle(
        name='Part Cell',
        parent=style_cell,
        fontSize=font_size,
        leading=font_size*1.2

    )

    style_id = ParagraphStyle(
        name='ID Cell',
        fontSize=font_size,
        leading=font_size*1.2
    )

    style_song = ParagraphStyle(
        name="Song Entry",
        parent=style_cell,
        fontSize=song_font_size,
        leading=song_font_size*1.2,
        leftIndent=8,
        bulletFontSize=song_font_size,
        bulletIndent=4
        )

    toc_with_songs = [
        [
            Paragraph(
                '##',
                style_toc_h
                ),
            Paragraph(
                'CHART',
                style_toc_h
                ),
            Paragraph(
                'PART',
                style_toc_h
                )
            ]
        ]
    row_counter = 0
    style = [('FONTNAME',       (0, 0), (-1, 0), 'Helvetica-Bold'),
             ('LEFTPADDING',    (0, 0), (-1, -1), 0),
             ('RIGHTPADDING',   (0, 0), (-1, -1), 0),
             ('TOPPADDING',     (0, 0), (-1, -1), 2),
             ('BOTTOMPADDING',  (0, 0), (-1, -1), 0),
             ('LINEBELOW',      (0, 0), (-1, 0), 1, colors.black),
             ('VALIGN',         (0, 0), (-1, -1), 'MIDDLE'),
             ('FONTSIZE',       (0, 1), (-1, -1), font_size),]

    # height_rows = [16]

    for entry in toc_data:
        row_counter += 1
        # height_rows.append(16)
        toc_with_songs.append(
            [Paragraph(entry[2], style_id),
             Paragraph(entry[0], style_chart),
             Paragraph(entry[1], style_part)])
        if entry[3] != []:
            for song in entry[3]:
                row_counter += 1
                # height_rows.append(12)
                style.append(
                    ('SPAN', (0, row_counter), (-1, row_counter))
                    )
                style.append(
                    ('TOPPADDING', (0, row_counter), (-1, row_counter), 1)
                    )
                toc_with_songs.append(
                    [Paragraph(f'<bullet>&bull;</bullet><i>    {song}</i>',
                               style_song), '', ''])

    toc = Table(
        toc_with_songs,
        colWidths=column_widths,
        style=style,
        repeatRows=1
        )

    frame1 = Frame(
        doc.leftMargin,
        doc.bottomMargin,
        doc.width/2-5,
        doc.height-(title_font_size*1.4),
        id='column1'
        )
    frame2 = Frame(
        doc.leftMargin + doc.width/2+5,
        doc.bottomMargin,
        doc.width/2-5,
        doc.height-(title_font_size*1.4),
        id='column2'
        )

    def header(canvas, doc, content):
        canvas.saveState()
        w, h = content.wrap(doc.width, doc.topMargin)
        content.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h)
        canvas.restoreState()

    toc_title = Paragraph(
        f"<b><i>{ensemble_name}: {book_name} Book</i></b>",
        style_toc_title
        )

    elements = [toc]

    doc.addPageTemplates(
        [PageTemplate(
            id='TOC',
            frames=[frame1, frame2],
            onPage=partial(
                header,
                content=toc_title
                )
            )]
        )

    doc.build(elements)

    return toc_output
