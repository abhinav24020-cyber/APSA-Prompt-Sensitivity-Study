"""Convert the APSA research paper (Markdown subset) to a Word document.

Supports: # / ## / ### headings, paragraphs, **bold**, *italic*, `code`, bullet and
numbered lists, pipe tables, images ``![caption](path)``, block quotes and fenced code.
No pandoc required (python-docx only).

Usage:
  .\\.venv\\Scripts\\python.exe scripts\\build_paper_docx.py docs\\paper\\APSA_research_paper.md
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

INLINE = re.compile(r"(<sub>[^<]+</sub>|<sup>[^<]+</sup>|\*\*[^*]+\*\*|\*[^*\s][^*]*\*|`[^`]+`)")


def add_inline(paragraph, text: str, size: float | None = None) -> None:
    for part in INLINE.split(text):
        if not part:
            continue
        if part.startswith("<sub>") or part.startswith("<sup>"):
            run = paragraph.add_run(part[5:-6])
            if part.startswith("<sub>"):
                run.font.subscript = True
            else:
                run.font.superscript = True
            if size:
                run.font.size = Pt(size)
            continue
        if part.startswith("**") and part.endswith("**"):
            run = paragraph.add_run(part[2:-2])
            run.bold = True
        elif part.startswith("`") and part.endswith("`"):
            run = paragraph.add_run(part[1:-1])
            run.font.name = "Consolas"
            run.font.size = Pt(9)
        elif part.startswith("*") and part.endswith("*") and len(part) > 2:
            run = paragraph.add_run(part[1:-1])
            run.italic = True
        else:
            run = paragraph.add_run(part)
        if size and not (part.startswith("`")):
            run.font.size = Pt(size)


def shade(cell, hex_fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_fill)
    tc_pr.append(shd)


def add_table(doc, rows: list[list[str]]) -> None:
    header, body = rows[0], rows[1:]
    table = doc.add_table(rows=1 + len(body), cols=len(header))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r_idx, row in enumerate([header] + body):
        for c_idx, value in enumerate(row[: len(header)]):
            cell = table.cell(r_idx, c_idx)
            cell.text = ""
            p = cell.paragraphs[0]
            add_inline(p, value.strip(), size=8)
            if r_idx == 0:
                for run in p.runs:
                    run.bold = True
                shade(cell, "E8EEF7")
    doc.add_paragraph()


def convert(md_path: Path, out_path: Path) -> None:
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)
    for section in doc.sections:
        section.left_margin = section.right_margin = Inches(0.9)
        section.top_margin = section.bottom_margin = Inches(0.8)

    lines = md_path.read_text(encoding="utf-8").splitlines()
    i = 0
    base = md_path.parent
    title_done = False
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped or stripped == "---":
            i += 1
            continue
        if stripped.startswith("```"):
            block = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                block.append(lines[i])
                i += 1
            p = doc.add_paragraph()
            run = p.add_run("\n".join(block))
            run.font.name = "Consolas"
            run.font.size = Pt(8.5)
            i += 1
            continue
        if stripped.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [c for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r"\s*:?-{2,}:?\s*", c) for c in cells):
                    rows.append(cells)
                i += 1
            add_table(doc, rows)
            continue
        img = re.match(r"!\[(.*?)\]\((.*?)\)", stripped)
        if img:
            path = (base / img.group(2)).resolve()
            if path.exists():
                doc.add_picture(str(path), width=Inches(6.4))
                doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
            cap = doc.add_paragraph()
            add_inline(cap, img.group(1), size=9)
            cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in cap.runs:
                run.italic = True
            i += 1
            continue
        heading = re.match(r"^(#{1,4})\s+(.*)", stripped)
        if heading:
            level = len(heading.group(1))
            text = heading.group(2)
            if level == 1 and not title_done:
                p = doc.add_paragraph()
                run = p.add_run(text)
                run.bold = True
                run.font.size = Pt(18)
                run.font.color.rgb = RGBColor(0x0B, 0x2E, 0x5C)
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                title_done = True
            else:
                doc.add_heading(text, level=min(level, 3))
            i += 1
            continue
        if stripped.startswith(">"):
            p = doc.add_paragraph(style="Intense Quote")
            add_inline(p, stripped.lstrip("> ").strip())
            i += 1
            continue
        bullet = re.match(r"^(\s*)[-*]\s+(.*)", line)
        number = re.match(r"^(\s*)\d+\.\s+(.*)", line)
        if bullet or number:
            m = bullet or number
            p = doc.add_paragraph(style="List Bullet" if bullet else "List Number")
            add_inline(p, m.group(2))
            i += 1
            continue
        para = [stripped]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(
            r"^(#|\||!\[|```|>|\s*[-*]\s|\s*\d+\.\s)", lines[i]
        ):
            para.append(lines[i].strip())
            i += 1
        p = doc.add_paragraph()
        add_inline(p, " ".join(para))
        p.paragraph_format.space_after = Pt(6)
    doc.save(out_path)


if __name__ == "__main__":
    src = Path(sys.argv[1])
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else src.with_suffix(".docx")
    convert(src, out)
    print(f"Wrote {out}")
