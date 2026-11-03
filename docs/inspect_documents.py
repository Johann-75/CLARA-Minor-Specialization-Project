"""
Comprehensive programmatic inspection of all generated academic documents:
- docs/final/CLARA_Final_Project_Report.docx
- docs/final/CLARA_Final_Project_Report.pdf
- docs/final/CLARA_Final_Presentation.pptx
- docs/final/CLARA_Final_Presentation.pdf
- docs/final/CLARA_Presentation_Script.docx
- docs/final/CLARA_Presentation_Script.md
- docs/final/CLARA_Project_Diary.docx
- docs/final/CLARA_Project_Diary.pdf
"""

import os
import re
import docx
from pptx import Presentation
import pypdf

DOCS_DIR = os.path.join(os.path.dirname(__file__), "final")

report_docx = os.path.join(DOCS_DIR, "CLARA_Final_Project_Report.docx")
report_pdf = os.path.join(DOCS_DIR, "CLARA_Final_Project_Report.pdf")
pres_pptx = os.path.join(DOCS_DIR, "CLARA_Final_Presentation.pptx")
pres_pdf = os.path.join(DOCS_DIR, "CLARA_Final_Presentation.pdf")
diary_docx = os.path.join(DOCS_DIR, "CLARA_Project_Diary.docx")
diary_pdf = os.path.join(DOCS_DIR, "CLARA_Project_Diary.pdf")
script_docx = os.path.join(DOCS_DIR, "CLARA_Presentation_Script.docx")
script_md = os.path.join(DOCS_DIR, "CLARA_Presentation_Script.md")


def inspect_report_docx():
    print("\n--- Inspecting Technical Report DOCX ---")
    doc = docx.Document(report_docx)
    sections = len(doc.sections)
    paragraphs = len(doc.paragraphs)
    tables = len(doc.tables)
    non_empty_p = sum(1 for p in doc.paragraphs if p.text.strip())
    
    # Check placeholders
    placeholders = []
    for p in doc.paragraphs:
        txt = p.text
        matches = re.findall(r'\[[A-Za-z0-9 _-]+\]', txt)
        for m in matches:
            if m not in ['[1]', '[2]', '[3]', '[4]', '[5]', '[6]', '[7]', '[8]', '[9]', '[10]', '[11]', '[12]', '[13]', '[14]', '[15]']:
                placeholders.append(m)

    print(f"Sections: {sections}, Total Paragraphs: {paragraphs}, Non-empty: {non_empty_p}")
    print(f"Tables: {tables}")
    print(f"Unresolved placeholders detected: {set(placeholders)}")


def inspect_report_pdf():
    print("\n--- Inspecting Technical Report PDF ---")
    reader = pypdf.PdfReader(report_pdf)
    num_pages = len(reader.pages)
    file_size_kb = os.path.getsize(report_pdf) / 1024
    print(f"Total Pages: {num_pages}")
    print(f"File Size: {file_size_kb:.2f} KB")
    
    # Check text from first and last pages
    p1_txt = reader.pages[0].extract_text()[:200].replace('\n', ' ')
    p_last_txt = reader.pages[-1].extract_text()[:200].replace('\n', ' ')
    print(f"Page 1 snippet: {p1_txt}")
    print(f"Last Page snippet: {p_last_txt}")


def inspect_presentation_pptx():
    print("\n--- Inspecting Presentation PPTX ---")
    prs = Presentation(pres_pptx)
    num_slides = len(prs.slides)
    print(f"Total Slides: {num_slides}")
    for idx, slide in enumerate(prs.slides):
        texts = [s.text.strip().replace('\n', ' ') for s in slide.shapes if s.has_text_frame and s.text.strip()]
        title = texts[0] if texts else "No title"
        print(f"  Slide {idx+1}: {title[:60]} ({len(texts)} text elements)")


def inspect_presentation_pdf():
    print("\n--- Inspecting Presentation PDF ---")
    reader = pypdf.PdfReader(pres_pdf)
    num_pages = len(reader.pages)
    file_size_kb = os.path.getsize(pres_pdf) / 1024
    print(f"Total Slides / Pages in PDF: {num_pages}")
    print(f"File Size: {file_size_kb:.2f} KB")


def inspect_diary_docx_and_pdf():
    print("\n--- Inspecting Project Diary DOCX & PDF ---")
    d_doc = docx.Document(diary_docx)
    print(f"Diary DOCX - Paragraphs: {len(d_doc.paragraphs)}, Tables: {len(d_doc.tables)}")
    
    d_reader = pypdf.PdfReader(diary_pdf)
    num_pages = len(d_reader.pages)
    file_size_kb = os.path.getsize(diary_pdf) / 1024
    print(f"Diary PDF - Total Pages: {num_pages}, File Size: {file_size_kb:.2f} KB")
    for i, p in enumerate(d_reader.pages):
        txt = p.extract_text().replace('\n', ' ')[:150]
        print(f"  Page {i+1}: {txt}...")


if __name__ == "__main__":
    inspect_report_docx()
    inspect_report_pdf()
    inspect_presentation_pptx()
    inspect_presentation_pdf()
    inspect_diary_docx_and_pdf()
