'''
Functions that produce a table of contents given a list of charts, and page format.
'''

from reportlab.platypus import BaseDocTemplate, Frame, Table, PageTemplate, TableStyle, Paragraph, FrameBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from library_tools import Chart, Song
from functools import partial
from constants import LYRE_PAPER_X, LYRE_PAPER_Y

def compile_toc_data(charts: list[Chart], a_parts: dict, b_parts: dict) -> list[list]:
    '''
    Given a list of charts in a book, and a list of the available parts for
    each chart for a selected instrument, generates a table in the format of
    CHART NAME, PART NAME, PAGE NUMBER, (list of songs, if the chart isn't a single)
    '''

    charts.sort(key=lambda x: x.slug)
    all_parts = a_parts + b_parts

    toc_data = []

    for chart in charts:
        for part in all_parts: 
            if chart.slug in part.slug:
                songs_entry = []
                if len(part.songs) > 1:
                    for song in part.songs:
                        songs_entry.append(song.title)
                toc_data.append([chart.title, part.part_title, part.page_id, songs_entry])
    
    return toc_data

def create_toc(ensemble_name: str, book_name: str, toc_data):
    '''
    Given the table of contents data, generates a table of contents
    '''
    toc_path = f"./output/test/toc - {book_name}.pdf"
    doc = BaseDocTemplate(toc_path,
                            pagesize = (LYRE_PAPER_X, LYRE_PAPER_Y),
                            rightMargin = 10,
                            leftMargin = 10,
                            topMargin = 10,
                            bottomMargin = 10,
                            title=f"Table of Contents - {book_name}",
                            )
    
    style_title = getSampleStyleSheet()['Title']

    style_cell = getSampleStyleSheet()['BodyText']
    style_cell.alignment = TA_LEFT

    style_right = ParagraphStyle(
        name = 'Right Cell',
        parent = style_cell
    )
    
    style_right.alignment = TA_RIGHT

    style_song = ParagraphStyle(
        name = "Song Entry",
        parent = style_cell,
        leftIndent = 10,
        bulletFontSize = 10,
        bulletIndent = 0
        )

    toc_with_songs = [['CHART', 'PART', '##']]
    row_counter = 0
    style = [('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('TOPPADDING', (0, 0), (-1, -1), 2),
             ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
             ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
             ('VALIGN', (0,0), (-1, -1), 'MIDDLE'),
             ('FONTSIZE', (0, 1), (-1, -1), 10),]

    # height_rows = [16]

    for entry in toc_data:
        row_counter += 1
        # height_rows.append(16)
        toc_with_songs.append([Paragraph(entry[0], style_cell), Paragraph(entry[1], style_cell), entry[2]])
        if entry[3] != []:
            for song in entry[3]:
                row_counter += 1
                # height_rows.append(12)
                style.append(('SPAN', (0, row_counter), (-1, row_counter)))
                style.append(('FONTSIZE', (0, row_counter), (-1, row_counter), 8))
                toc_with_songs.append([Paragraph(f'<bullet>&bull;</bullet><i>    {song}</i>', style_song), '', ''])

    toc = Table(toc_with_songs, colWidths=[141, 72, 24], style=style, repeatRows=1)

    frame1 = Frame(doc.leftMargin, doc.bottomMargin, doc.width/2-5, doc.height-16, id='column1')
    frame2 = Frame(doc.leftMargin + doc.width/2+5, doc.bottomMargin, doc.width/2-5, doc.height-16, id='column2')
    
    def header(canvas, doc, content):
        canvas.saveState()
        w, h = content.wrap(doc.width, doc.topMargin)
        content.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h)
        canvas.restoreState()

    toc_title = Paragraph(f"<b><i>{ensemble_name}: {book_name} book</i></b>", style_title)

    elements = [toc]

    doc.addPageTemplates([PageTemplate(id='TOC', frames=[frame1, frame2], onPage = partial(header, content=toc_title))])

    doc.build(elements) 

    return toc_path