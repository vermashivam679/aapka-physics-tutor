#!/usr/bin/env python3
"""
Convert one chapter's MCQ markdown into indexed JSON for the tutor website.

Usage:
    python build_chapter.py <chapter_md> <chapter_id> [--site <site_root>]

Example:
    python tools/build_chapter.py content/ch01/source.md ch01

Writes:
    content/<chapter_id>/<section>.json    one file per section (theory, diagram, MCQs)
    content/index.json                     master index of all chapters + sections (merged, not overwritten)

Expected markdown layout (same as the Chapter 1 file):
    # Chapter N — Title
    ## N.M Section title
    ![alt](diagrams/xxx.png)
    ### 📘 Learning Material
    ...theory markdown...
    ### ❓ MCQs
    (optional "### A. Sub-topic" headings)
    **Q1.** 🟢 Question text
    - (A) option
    ...
    ### Answer Key — N.M
    | Q | Ans | Explanation |
    | 1 | B | ... |
"""
import json, re, sys, argparse
from pathlib import Path

DIFF = {"🟢": "recall", "🟡": "understanding", "🔴": "application"}
SEC_RE = re.compile(r"^## (\d+\.\d+)\s+(.+)$", re.M)
Q_RE = re.compile(r"^\*\*Q(\d+)\.\*\*\s*(🟢|🟡|🔴)?\s*(.+)$")
OPT_RE = re.compile(r"^-\s*\(([A-H])\)\s*(.+)$")
KEY_RE = re.compile(r"^\|\s*(\d+)\s*\|\s*([A-H])\s*\|\s*(.+?)\s*\|\s*$")


def parse_section(num, title, body, chapter_id):
    diagram = None
    m = re.search(r"!\[[^\]]*\]\(([^)]+)\)", body)
    if m:
        diagram = f"content/{chapter_id}/{m.group(1)}"

    theory = ""
    t = re.search(r"### 📘 Learning Material\s*\n(.*?)(?=^### ❓ MCQs)", body, re.S | re.M)
    if t:
        theory = t.group(1).strip()

    mcq_part = re.search(r"^### ❓ MCQs\s*\n(.*?)(?=^### Answer Key)", body, re.S | re.M)
    key_part = re.search(r"^### Answer Key.*?\n(.*)", body, re.S | re.M)

    keys = {}
    if key_part:
        for line in key_part.group(1).splitlines():
            k = KEY_RE.match(line.strip())
            if k:
                keys[int(k.group(1))] = (k.group(2), k.group(3))

    questions, group, cur = [], None, None
    if mcq_part:
        for raw in mcq_part.group(1).splitlines():
            line = raw.strip()
            if line.startswith("### "):
                group = line[4:].strip()
                continue
            q = Q_RE.match(line)
            if q:
                n = int(q.group(1))
                cur = {
                    "id": f"{num}-q{n}",
                    "n": n,
                    "difficulty": DIFF.get(q.group(2) or "", "recall"),
                    "group": group,
                    "prompt": q.group(3).strip(),
                    "options": [],
                }
                questions.append(cur)
                continue
            o = OPT_RE.match(line)
            if o and cur is not None:
                cur["options"].append({"id": o.group(1), "text": o.group(2).strip()})

    for q in questions:
        ans = keys.get(q["n"])
        if not ans:
            raise SystemExit(f"Section {num}: no answer-key row for Q{q['n']}")
        q["answer"], q["explanation"] = ans
        if q["answer"] not in [o["id"] for o in q["options"]]:
            raise SystemExit(f"Section {num} Q{q['n']}: answer {q['answer']} is not an option")

    return {
        "id": num,
        "slug": f"{chapter_id}-{num.replace('.', '-')}",
        "chapter": chapter_id,
        "title": title.strip(),
        "diagram": diagram,
        "theory": theory,
        "questions": questions,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("md")
    ap.add_argument("chapter_id")
    ap.add_argument("--site", default=str(Path(__file__).resolve().parent.parent))
    a = ap.parse_args()

    site = Path(a.site)
    text = Path(a.md).read_text(encoding="utf-8")
    h = re.search(r"^# (.+)$", text, re.M)
    ch_title = h.group(1).strip() if h else a.chapter_id
    cm = re.match(r"Chapter\s+(\d+)\s*[—\-:]\s*(.+)", ch_title)
    ch_num, ch_name = (int(cm.group(1)), cm.group(2).strip()) if cm else (None, ch_title)

    out_dir = site / "content" / a.chapter_id
    out_dir.mkdir(parents=True, exist_ok=True)

    heads = list(SEC_RE.finditer(text))
    sections = []
    for i, m in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        sec = parse_section(m.group(1), m.group(2), text[m.end():end], a.chapter_id)
        (out_dir / f"{sec['id']}.json").write_text(
            json.dumps(sec, ensure_ascii=False, indent=1), encoding="utf-8")
        sections.append({
            "id": sec["id"], "slug": sec["slug"], "title": sec["title"],
            "file": f"content/{a.chapter_id}/{sec['id']}.json",
            "questionCount": len(sec["questions"]),
        })
        print(f"  {sec['id']:>5}  {sec['title']:<35} {len(sec['questions'])} MCQs")

    idx_path = site / "content" / "index.json"
    index = json.loads(idx_path.read_text(encoding="utf-8")) if idx_path.exists() else {"chapters": []}
    index["chapters"] = [c for c in index["chapters"] if c["id"] != a.chapter_id]
    index["chapters"].append({
        "id": a.chapter_id, "number": ch_num, "title": ch_name,
        "book": "H.C. Verma, Concepts of Physics Vol. 1", "sections": sections,
    })
    index["chapters"].sort(key=lambda c: (c["number"] is None, c["number"] or 0, c["id"]))
    idx_path.write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{a.chapter_id}: {len(sections)} sections, "
          f"{sum(s['questionCount'] for s in sections)} MCQs -> {idx_path}")


if __name__ == "__main__":
    main()
