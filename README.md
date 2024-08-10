# magicbook

A set of utilities for managing your large ensemble sheet music

## Getting Started

magicbook _currently_ assumes you have the directory `./music-library/` in the
root of the project, with the charts arranged in the following structure:

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
- Selecting a subset of the charts to perform actions on
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

- Update the chart "info.json" file
- This is not a complete list of planned features, will add more to this section
  as I organize my thoughts.

## Limitations

- **magicbook** only works with instruments divided into four parts at most.
  Since most large ensemble sheet music doesn't split instruments into more than
  four parts, increasing this limit is not a priority.
