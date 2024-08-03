# magicbook

A set of utilities for managing your large ensemble sheet music

## Getting Started

magicbook _currently_ assumes you have the directory `./music-library/` in the
root of the project, with the charts arranged in the following structure

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

A sample music library with this structure is [available for download here](https://1drv.ms/f/s!AlNWUe2YKW0ehYUQOrpQwFzMWRFiQQ?e=VboBnD)

## Features

As of this writing, **magicbook** performs the following tasks:

- Auditing the library on startup
  - ensures every chart has a valid info.json file
- Selecting a subset of the charts to perform actions on
- Assembling books from a selection of charts, where parts are in directories based on their instrument rather than based on their assocated chart

### Planned Features

- I plan to write this section soon