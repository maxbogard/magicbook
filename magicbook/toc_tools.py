'''
Functions that produce a table of contents given a list of charts, and page format.
'''

from reportlab.platypus import BaseDocTemplate, Frame, Table, PageTemplate, TableStyle, Paragraph
from reportlab.lib import colors
from library_tools import Chart, Song
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

def create_toc(book_name: str, toc_data):
    '''
    Given the table of contents data, generates a table of contents
    '''
    toc_path = f"./output/test/toc - {book_name}.pdf"
    doc = BaseDocTemplate(toc_path,
                            pagesize = (LYRE_PAPER_X, LYRE_PAPER_Y),
                            rightMargin = 16,
                            leftMargin = 16,
                            topMargin = 16,
                            bottomMargin = 16,
                            title=f"Table of Contents - {book_name}"
                            )

    toc_with_songs = [['CHART', 'PART', '##']]
    row_counter = 0
    style = [('LINEBELOW', (0, 0), (-1, 0), 1, colors.black)]
    print(toc_data)
    for entry in toc_data:
        row_counter += 1
        toc_with_songs.append([entry[0], entry[1], entry[2]])
        if entry[3] != []:
            row_counter += 1
            song_contents = "     "
            style.append(('SPAN', (0, row_counter), (-1, row_counter)))
            for song in entry[3]:
                print(song)
                song_contents.join(f"{song}, ")
            toc_with_songs.append([song_contents])

    toc = Table(toc_with_songs, style=style, repeatRows=1)

    frame1 = Frame(doc.leftMargin, doc.bottomMargin, doc.width/2-5, doc.height, id='column1')
    frame2 = Frame(doc.leftMargin + doc.width/2+5, doc.bottomMargin, doc.width/2-5, doc.height, id='column2')
    
    elements = [toc]

    doc.addPageTemplates([PageTemplate(id='TOC', frames=[frame1, frame2])])

    doc.build(elements) 

    return toc_path