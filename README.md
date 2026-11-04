# Aapka Physics Tutor – website

## Folder layout
index.html                  the whole site (one page, loads content on demand)
content/index.json          master index: chapters -> sections (title, slug, file, question count)
content/chNN/<sec>.json     one file per section: theory (markdown), diagram path, MCQs with answers
content/chNN/diagrams/      section summary images
tools/build_chapter.py      turns a chapter's MCQ markdown into the JSON above
content/curiosity/index.json  Everyday Physics cards (GIF + explanation), shown on the home page and at #everyday
content/curiosity/gifs/     the GIFs, plus a still "_poster.jpg" of each for the grids
content/curiosity/qNN.html  each card as a standalone snippet (qNN.md = same text in Markdown)

## Add a new chapter
1. Make the chapter markdown in the same format as Chapter 1 (## N.M headings, Learning Material, MCQs, Answer Key).
2. Copy it to content/ch02/source.md and its images to content/ch02/diagrams/
3. Run:  python tools/build_chapter.py content/ch02/source.md ch02
   (it adds Chapter 2 to content/index.json without touching other chapters, and stops if any answer is missing)

## Everyday Physics (curiosity series)
- Made by C:\PhysicsTutor\Curiosity\tools\curiosity_cards.py. Add a question to CARDS in that file, put its GIF in
  content/curiosity/gifs/, then run:  python ..\Curiosity\tools\curiosity_cards.py .   (from this folder)
- Links: index.html#everyday shows all questions; index.html#everyday-q02 opens one question.
- The site still works if content/curiosity/index.json is missing (the section just doesn't show).

## Fetch a section directly
- Page links:  index.html#ch01-1-3   opens the Learn tab (diagram + theory); #ch01-1-3-practice opens the MCQs
- Raw data:    content/ch01/1.3.json   (same JSON can power your mobile app)

## Run locally
In this folder: python -m http.server 8000  then open http://localhost:8000
(opening index.html by double-clicking won't work because browsers block loading the JSON from file://)
Any static host works: GitHub Pages, Netlify, Cloudflare Pages.
