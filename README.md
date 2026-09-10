# CSIR NET Mathematical Sciences — NRSTATLAB

Free study material for CSIR NET Mathematical Sciences (Subject Code 704): previous-year
question papers worked out question by question, the official syllabus, and the exam
strategy that follows from the marking scheme.

Published with GitHub Pages at
<https://nrstatlab.github.io/CSIR-NET-MATHEMATICS/>.

Part of [NRSTATLAB](https://nrstatlab.github.io/planning-for-future/).

## What is here

| Page | Purpose |
| --- | --- |
| `index.html` | Site home: what the archive is, the paper at a glance |
| `syllabus.html` | Complete CSIR-HRDG syllabus, Units I–IV, plus the marking scheme |
| `strategy.html` | Time budget, the expected-value arithmetic of guessing, revision order |
| `papers/index.html` | Index of every paper in the collection, with its solved percentage |
| `papers/<slug>.html` | One fully solved paper |
| `HOW-TO-ADD-A-PAPER.html` | The pipeline, written up for contributors |

## How the solved papers are produced

Paper pages are **generated, never hand-written**. All content lives in
`data/papers/<slug>.json`; `tools/build.py` turns it into HTML.

```
papers-inbox/<paper>.pdf     raw source, archived
data/papers/<slug>.json      questions, options, answers, worked steps
tools/build.py               generator (Python standard library only)
papers/<slug>.html           generated output — do not edit
papers/index.html            generated index — do not edit
```

Rebuild after any edit to the JSON:

```bash
python3 tools/build.py
```

A question with an empty `body` or empty `answer` is treated as not yet solved and is
omitted from the published page, so a long paper can go up in instalments without ever
showing a blank question. The progress bar on each paper page and the status pill on the
index are both computed from the JSON and cannot drift out of step with what is published.

The JSON field reference is in `HOW-TO-ADD-A-PAPER.html`.

## Adding a paper

1. Commit the PDF to `papers-inbox/` (see that folder's README for the naming rule).
2. Copy an existing `data/papers/*.json`, change the metadata, empty the question bodies.
3. Transcribe and solve, batch by batch.
4. `python3 tools/build.py`, then commit and push.

## Technology

Plain HTML and CSS with [MathJax 3](https://www.mathjax.org/) for the mathematics — no
framework, no build step for the browser, nothing to install to read the site offline.
Every question is real text rather than a screenshot, so it renders sharply on a phone,
can be copied into your own notes, and is findable by search.

## Licence and attribution

Question papers are the property of CSIR-HRDG / NTA and are reproduced here only for
educational discussion. The solutions, the site and the code are NRSTATLAB's own work.
