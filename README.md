# Aapka Physics Tutor – website

## Folder layout
index.html                  the whole site (one page, loads content on demand)
content/index.json          master index: chapters -> sections (title, slug, file, question count)
content/chNN/<sec>.json     one file per section: theory (markdown), diagram path, MCQs with answers
content/chNN/diagrams/      section summary images
tools/build_chapter.py      turns a chapter's MCQ markdown into the JSON above

## Add a new chapter
1. Make the chapter markdown in the same format as Chapter 1 (## N.M headings, Learning Material, MCQs, Answer Key).
2. Copy it to content/ch02/source.md and its images to content/ch02/diagrams/
3. Run:  python tools/build_chapter.py content/ch02/source.md ch02
   (it adds Chapter 2 to content/index.json without touching other chapters, and stops if any answer is missing)

## Fetch a section directly
- Page links:  index.html#ch01-1-3   (#ch01-1-3-visual, #ch01-1-3-practice open those tabs)
- Raw data:    content/ch01/1.3.json   (same JSON can power your mobile app)

## Run locally
In this folder: python -m http.server 8000  then open http://localhost:8000
(opening index.html by double-clicking won't work because browsers block loading the JSON from file://)
Any static host works: GitHub Pages, Netlify, Cloudflare Pages.
