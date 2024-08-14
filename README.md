# magicbook

A set of utilities for managing your large ensemble sheet music

## Getting Started

Create a new **magicbook** library by running `magicbook (directory) -n`, this
creates a new library in the specified directory. The library will have the
following structure:

```
.
├── config
│   ├── config.json
│   ├── ensembles
│   ├── generic_ensemble.json
│   ├── instruments.json
│   ├── schema
│   │   └── chart-info.json
│   └── templates
├── logs
├── music-library
│  
└── output
```

Once the library is created, magicbook should be run from the root dirctory of
the library. Alternatively, you can specify the path to the library with
`magicbook -p PATH`.

To add charts to the library, run
`magicbook charts add SLUG True --song TITLE ARTIST ARRANGER`

- SLUG is the directory the chart will go in, and can only contain lowercase
  letters and dashes (-)
- TITLE is the title of the song on the chart
- ARTIST and ARRANGER are self-explanatory. If you don't know the artist or the
  arranger, you can use `""` (an empty string).

**magicbook** is still in development, so you have to copy the PDFs into the
directory manually for now, following this structure:

```
├── (chart-slug)
│   ├── info.json
│   ├── (chart-slug) AUDIO.mp3
│   ├── (chart-slug) (FORMAT) (part-slug).pdf
│   ├── ...
│   ├── (chart-slug) (FORMAT) (part-slug).pdf
│   └── (chart-slug) SCORE.pdf
├── (chart-slug)
│   ├── info.json
│   ├── (chart-slug) AUDIO.mp3
│   ├── (chart-slug) (FORMAT) (part-slug).pdf
│   ├── ...
│   ├── (chart-slug) (FORMAT) (part-slug).pdf
│   └── (chart-slug) SCORE.pdf
├── (chart-slug)
│   └── ...
└── (chart-slug)
```

A sample music library with this structure is
[available for download here](https://1drv.ms/f/s!AlNWUe2YKW0ehYUQOrpQwFzMWRFiQQ)

There will be a command to import PDFs into the library in a future release.

Note that **magicbook** currently requires a single-page letter size PDF file to
properly impose the charts, stored as `./config/templates/trim-guides.pdf`. Use
a PDF with trim markings
([like this one](https://1drv.ms/b/s!AlNWUe2YKW0ehYlRwEEp_Zb6asruSA?e=1gVmbA))
if you want them printed on your marchpacks, otherwise use a blank PDF. This is
a temporary workaround that won't be needed in future releases.

### Terminology

For the purposes of this software:

- a **song** is a work of music.
- a **chart** is a set of sheet music, with multiple pdf **parts** for different
  players.
  - A chart may have one or more **songs**.
  - A chart may have one or more pages.

## Features

As of this writing, **magicbook** performs the following tasks:

- Auditing the library on startup
  - ensures every chart has a valid info.json file
- Assembling books from a selection of charts, where parts are in directories
  based on their instrument rather than based on their assocated chart
- Merging these directories of different parts into an A.pdf and B.pdf to be
  printed and placed in marchpacks
- Merging an instrument's charts into one single PDF for printing, either as a
  marchpack (7in x 5in pages that attach to an instrument), or as a full-sized
  binder with 8.5in x 11in pages.
  - For marchpacks, imposing the marchpack pages onto 8.5" x 11" paper (2
    marchpack pages per printing pages), so after printing they can be easily
    cut with a paper cutter and placed into a standard double-sided marchpack
- Searching for alternate parts if a chart doesn't have a part for a specified
  instrument.
  - i.e. if there is no Trombone part, add a Baritone part if one is available.
    If that's not an option, add a Tuba part.
- Printing a table of contents for each book, listing charts in alphabetical
  order.

### Planned Features

- Importing chart files into the library
- Update the chart "info.json" file
- Modifying created books with a record of previous versions and the date
  modified, so PDFs with only updated parts as opposed to the whole book can be
  created.
- This is not a complete list of planned features, will add more to this section
  as I organize my thoughts.

## Limitations

- **magicbook** only works with instruments divided into four parts at most.
  Since most large ensemble sheet music doesn't split instruments into more than
  four parts, increasing this limit is not a priority.
