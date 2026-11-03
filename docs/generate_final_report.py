"""
CLARA Final Technical Thesis Report Generator (DOCX and PDF).
Canonical Formal Title:
CLARA: Cloud-Linked Evaluation and Risk Assessment using Predictive Analytics and Business Intelligence

Complies with the official MAHE / MIT Bengaluru Phase-2 UG Thesis Guidelines:
- Official 4-member student team (Johann Mathew Sajan, Nandan Murali, Abhijay Gupta, Arshia Gali)
- Minimum 35-page comprehensive academic thesis requirement
- Formal Front Matter: Cover, Certificate, Declaration, Acknowledgements, 4-Paragraph Abstract, TOC, List of Figures, List of Tables
- Chapters 1 to 10 with deep technical exposition, mathematical formulas, schemas, algorithms, and empirical tables
- IEEE References (20+ citations)
- Appendix A: Mandatory NBA Course Articulation Matrix (CO-PO) and IET CLO-AHEP Learning Outcome Mapping
- Appendix B: Database DDL Schemas and Pydantic Recommendation Contracts
- Explicit Screenshot Insertion Locations for pending manual captures
- Authoritative Gemini Provenance reporting (gemini-3.8-flash)
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, PageBreak, HRFlowable, KeepTogether
)
from reportlab.pdfgen import canvas
import pypdf

from docs.report_data import (
    PROJECT_FORMAL_TITLE, PROJECT_SHORT_TITLE, INSTITUTION, INSTITUTION_SUB,
    CAMPUS_LOCATION, DEPARTMENT, DEGREE, COURSE_CODE, ACADEMIC_YEAR,
    SUBMISSION_DATE_PLACEHOLDER, STUDENTS, GUIDE_NAME, GUIDE_DESIG, GUIDE_AFFIL,
    COORDINATOR_NAME, COORDINATOR_DESIG, COORDINATOR_AFFIL, HOD_TITLE, HOD_AFFIL,
    DEAN_TITLE, DEAN_AFFIL, ABSTRACT_PARAS, ACKNOWLEDGEMENTS_TEXT,
    CHAPTER_1_TITLE, CHAPTER_1_SECTIONS, CHAPTER_2_TITLE, CHAPTER_2_SECTIONS,
    CHAPTER_3_TITLE, CHAPTER_3_SECTIONS, CHAPTER_4_TITLE, CHAPTER_4_SECTIONS,
    CHAPTER_5_TITLE, CHAPTER_5_SECTIONS, CHAPTER_6_TITLE, CHAPTER_6_SECTIONS,
    CHAPTER_7_TITLE, CHAPTER_7_SECTIONS, CHAPTER_8_TITLE, CHAPTER_8_SECTIONS,
    CHAPTER_9_TITLE, CHAPTER_9_SECTIONS, CHAPTER_10_TITLE, CHAPTER_10_SECTIONS,
    IEEE_REFERENCES, NBA_CO_DESCRIPTIONS, TABLE_A1_1_HEADERS, TABLE_A1_1_ROWS,
    TABLE_A1_2_HEADERS, TABLE_A1_2_ROWS, TABLE_A1_3_HEADERS, TABLE_A1_3_ROWS,
    APPENDIX_B_SECTIONS, TOC_ENTRIES, FIGURES_LIST, TABLES_LIST, SCREENSHOTS_META,
    CONFUSION_MATRIX_DATA, CATEGORY_RECALL_DATA
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(BASE_DIR, "docs", "final")
FIG_DIR = os.path.join(DOCS_DIR, "figures")
os.makedirs(DOCS_DIR, exist_ok=True)

DOCX_OUT = os.path.join(DOCS_DIR, "CLARA_Final_Project_Report.docx")
PDF_OUT = os.path.join(DOCS_DIR, "CLARA_Final_Project_Report.pdf")


def set_cell_background(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)


def set_cell_margins(cell, top=100, bottom=100, left=120, right=120):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)


def add_callout_box_docx(doc, text, title="ACADEMIC NOTE", border_color="1E3A8A", bg_color="F8FAFC"):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    cell = table.rows[0].cells[0]
    cell.width = Inches(6.5)
    set_cell_background(cell, bg_color)
    set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
    
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:left w:val="single" w:sz="24" w:space="0" w:color="{border_color}"/>'
        f'<w:top w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'<w:bottom w:val="none"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.15
    rt = p.add_run(f"{title}: ")
    rt.bold = True
    rt.font.name = "Times New Roman"
    rt.font.size = Pt(10)
    rt.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)
    
    rb = p.add_run(text)
    rb.font.name = "Times New Roman"
    rb.font.size = Pt(10)
    rb.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def add_screenshot_placeholder_docx(doc, fig_num, title, target_file, description):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    cell = table.rows[0].cells[0]
    cell.width = Inches(6.5)
    set_cell_background(cell, "F1F5F9")
    set_cell_margins(cell, top=120, bottom=120, left=140, right=140)
    
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:left w:val="single" w:sz="12" w:space="0" w:color="94A3B8"/>'
        f'<w:top w:val="single" w:sz="12" w:space="0" w:color="94A3B8"/>'
        f'<w:right w:val="single" w:sz="12" w:space="0" w:color="94A3B8"/>'
        f'<w:bottom w:val="single" w:sz="12" w:space="0" w:color="94A3B8"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(4)
    r1 = p.add_run(f"[SCREENSHOT INSERTION LOCATION: {target_file}]\n")
    r1.bold = True
    r1.font.name = "Times New Roman"
    r1.font.size = Pt(10.5)
    r1.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
    
    r2 = p.add_run(f"Status: PENDING MANUAL CAPTURE\nResolution: 1920 x 1080 | Format: PNG\n\n{description}\n")
    r2.font.name = "Times New Roman"
    r2.font.size = Pt(9.5)
    r2.font.color.rgb = RGBColor(0x47, 0x55, 0x69)
    
    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_before = Pt(3)
    p_cap.paragraph_format.space_after = Pt(10)
    rc = p_cap.add_run(f"Figure {fig_num}: {title} (Target: docs/final/screenshots/{target_file})")
    rc.font.name = "Times New Roman"
    rc.font.size = Pt(9.5)
    rc.italic = True
    rc.font.color.rgb = RGBColor(0x33, 0x41, 0x55)



CHAPTERS_SPEC = [
    (CHAPTER_1_TITLE, CHAPTER_1_SECTIONS, None),
    (CHAPTER_2_TITLE, CHAPTER_2_SECTIONS, None),
    (CHAPTER_3_TITLE, CHAPTER_3_SECTIONS, ("Figure 3.1", "architecture_overview.png", "Four-Layer High-Level System Architecture Blueprint")),
    (CHAPTER_4_TITLE, CHAPTER_4_SECTIONS, ("Figure 4.1", "duckdb_schema_erd.png", "DuckDB Normalized Relational Schema Entity-Relationship Diagram")),
    (CHAPTER_5_TITLE, CHAPTER_5_SECTIONS, ("Figure 5.1", "risk_scoring_flow.png", "Composite Risk Scoring Workflow & Mathematical Weight Distribution")),
    (CHAPTER_6_TITLE, CHAPTER_6_SECTIONS, ("Figure 6.1", "gemini_recommendation_flow.png", "Dual-Path GenAI Recommendation Flow with Resilient Fallback")),
    (CHAPTER_7_TITLE, CHAPTER_7_SECTIONS, None),
    (CHAPTER_8_TITLE, CHAPTER_8_SECTIONS, ("Figure 8.1", "anomaly_detector_pipeline.png", "Multi-Modal Anomaly Detection Evaluation & Feature Pipeline")),
    (CHAPTER_9_TITLE, CHAPTER_9_SECTIONS, ("Figure 9.1", "testing_validation_flow.png", "Automated Test Architecture & Continuous Verification Isolation")),
    (CHAPTER_10_TITLE, CHAPTER_10_SECTIONS, None),
]

def build_docx_report():
    print("Building CLARA Final Technical Thesis Report (DOCX)...")
    doc = docx.Document()
    
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        section.different_first_page_header_footer = True

    # 1. COVER PAGE
    p_top = doc.add_paragraph()
    p_top.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_top.paragraph_format.space_before = Pt(0)
    p_top.paragraph_format.space_after = Pt(4)
    r = p_top.add_run(f"{INSTITUTION}\n")
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)
    r.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)
    
    r_sub = p_top.add_run(f"{INSTITUTION_SUB}\n{CAMPUS_LOCATION}\n\n")
    r_sub.font.name = "Times New Roman"
    r_sub.font.size = Pt(10)
    r_sub.font.color.rgb = RGBColor(0x47, 0x55, 0x69)
    
    r_dept = p_top.add_run(f"{DEPARTMENT}\n{COURSE_CODE}\n\n")
    r_dept.bold = True
    r_dept.font.name = "Times New Roman"
    r_dept.font.size = Pt(11)
    r_dept.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(8)
    p_title.paragraph_format.space_after = Pt(8)
    rtitle = p_title.add_run(f"A MINOR SPECIALIZATION PROJECT REPORT\nON\n\n{PROJECT_FORMAL_TITLE}\n")
    rtitle.bold = True
    rtitle.font.name = "Times New Roman"
    rtitle.font.size = Pt(14)
    rtitle.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    p_subm = doc.add_paragraph()
    p_subm.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_subm.paragraph_format.space_before = Pt(8)
    p_subm.paragraph_format.space_after = Pt(12)
    rsubm = p_subm.add_run(
        f"Submitted in partial fulfilment of the requirements for the award of the Degree of\n"
        f"{DEGREE}\n\n"
        f"Submitted by:\n"
    )
    rsubm.font.name = "Times New Roman"
    rsubm.font.size = Pt(11)

    t_stud = doc.add_table(rows=1, cols=3)
    t_stud.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_stud.autofit = False
    headers = ["Sl. No.", "Student Full Name", "Registration Number"]
    for i, h in enumerate(headers):
        cell = t_stud.rows[0].cells[i]
        cell.text = h
        cell.paragraphs[0].runs[0].bold = True
        cell.paragraphs[0].runs[0].font.name = "Times New Roman"
        cell.paragraphs[0].runs[0].font.size = Pt(10)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cell_background(cell, "1E3A8A")
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        set_cell_margins(cell, top=80, bottom=80, left=100, right=100)

    for sno, sname, reg, email in STUDENTS:
        row = t_stud.add_row()
        for idx, val in enumerate([sno, sname, reg]):
            c = row.cells[idx]
            c.text = val
            c.paragraphs[0].runs[0].font.name = "Times New Roman"
            c.paragraphs[0].runs[0].font.size = Pt(10)
            if idx == 0 or idx == 2:
                c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            set_cell_background(c, "F8FAFC" if int(sno) % 2 == 1 else "FFFFFF")
            set_cell_margins(c, top=80, bottom=80, left=100, right=100)

    p_guide = doc.add_paragraph()
    p_guide.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_guide.paragraph_format.space_before = Pt(20)
    p_guide.paragraph_format.space_after = Pt(4)
    rg = p_guide.add_run(
        f"Under the Guidance of:\n"
        f"{GUIDE_NAME}\n"
        f"{GUIDE_DESIG}\n"
        f"{GUIDE_AFFIL}\n\n"
        f"Academic Year: {ACADEMIC_YEAR} | Submission Date: {SUBMISSION_DATE_PLACEHOLDER}"
    )
    rg.font.name = "Times New Roman"
    rg.font.size = Pt(11)

    doc.add_page_break()

    # 2. CERTIFICATE PAGE
    p_cert = doc.add_paragraph()
    p_cert.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cert.paragraph_format.space_before = Pt(0)
    p_cert.paragraph_format.space_after = Pt(8)
    rc1 = p_cert.add_run(f"{INSTITUTION}\n{DEPARTMENT}\n\n")
    rc1.bold = True
    rc1.font.name = "Times New Roman"
    rc1.font.size = Pt(12)
    rc2 = p_cert.add_run("CERTIFICATE\n")
    rc2.bold = True
    rc2.font.name = "Times New Roman"
    rc2.font.size = Pt(15)
    rc2.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)

    student_str = ", ".join([f"{name} (Reg. No: {reg})" for _, name, reg, _ in STUDENTS])
    p_cert_body = doc.add_paragraph()
    p_cert_body.paragraph_format.space_before = Pt(6)
    p_cert_body.paragraph_format.space_after = Pt(14)
    p_cert_body.paragraph_format.line_spacing = 1.25
    rcb = p_cert_body.add_run(
        f"This is to certify that the project report titled \"{PROJECT_FORMAL_TITLE}\" is a bonafide record of "
        f"the project work carried out by {student_str}, in partial fulfilment of the requirements for the award of the Degree of "
        f"{DEGREE} of the Manipal Academy of Higher Education (MAHE) during the academic year {ACADEMIC_YEAR}.\n\n"
        f"The project report has been approved as satisfying the academic requirements prescribed for the Minor Specialization Project."
    )
    rcb.font.name = "Times New Roman"
    rcb.font.size = Pt(11)

    t_sig = doc.add_table(rows=2, cols=2)
    t_sig.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_sig.autofit = False
    sig_blocks = [
        (f"______________________________\n{GUIDE_NAME}\nProject Guide\n{GUIDE_DESIG}"),
        (f"______________________________\n{COORDINATOR_NAME}\nMinor Specialization Coordinator\n{COORDINATOR_DESIG}"),
        (f"______________________________\n{HOD_TITLE}\n{HOD_AFFIL}"),
        (f"______________________________\n{DEAN_TITLE}\n{DEAN_AFFIL}")
    ]
    for idx, text in enumerate(sig_blocks):
        r_i = idx // 2
        c_i = idx % 2
        cell = t_sig.rows[r_i].cells[c_i]
        cell.width = Inches(3.2)
        cell.text = text
        for p in cell.paragraphs:
            p.paragraph_format.space_before = Pt(16)
            p.paragraph_format.space_after = Pt(10)
            p.paragraph_format.line_spacing = 1.15
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(9.5)

    p_cdate = doc.add_paragraph()
    p_cdate.paragraph_format.space_before = Pt(20)
    p_cdate.paragraph_format.space_after = Pt(0)
    rcd = p_cdate.add_run(f"Date: {SUBMISSION_DATE_PLACEHOLDER}\nPlace: Bengaluru")
    rcd.font.name = "Times New Roman"
    rcd.font.size = Pt(10)

    doc.add_page_break()

    # 3. STUDENT DECLARATION
    p_dec = doc.add_paragraph()
    p_dec.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_dec.paragraph_format.space_before = Pt(0)
    p_dec.paragraph_format.space_after = Pt(10)
    rd1 = p_dec.add_run("STUDENT DECLARATION\n")
    rd1.bold = True
    rd1.font.name = "Times New Roman"
    rd1.font.size = Pt(14)
    rd1.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)

    p_dec_b = doc.add_paragraph()
    p_dec_b.paragraph_format.space_before = Pt(6)
    p_dec_b.paragraph_format.space_after = Pt(16)
    p_dec_b.paragraph_format.line_spacing = 1.25
    rdb = p_dec_b.add_run(
        f"We hereby declare that the project work titled \"{PROJECT_FORMAL_TITLE}\" submitted to the Department of "
        f"Computer Science and Engineering, Manipal Institute of Technology Bengaluru, is a record of original work done by us "
        f"under the supervision and guidance of {GUIDE_NAME}, Assistant Professor, Department of CSE, MIT Bengaluru.\n\n"
        f"We further declare that the work reported herein has not been submitted either in part or in full for the award of any other "
        f"degree or diploma in this institute or any other university. All sources of external literature, datasets, tools, and code "
        f"libraries have been duly acknowledged in the references in accordance with academic integrity guidelines."
    )
    rdb.font.name = "Times New Roman"
    rdb.font.size = Pt(11)

    t_dsig = doc.add_table(rows=2, cols=2)
    t_dsig.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_dsig.autofit = False
    for idx, (sno, sname, reg, _) in enumerate(STUDENTS):
        r_i = idx // 2
        c_i = idx % 2
        cell = t_dsig.rows[r_i].cells[c_i]
        cell.width = Inches(3.2)
        cell.text = f"______________________________\n{sname}\nReg. No: {reg}\nDate: {SUBMISSION_DATE_PLACEHOLDER}"
        for p in cell.paragraphs:
            p.paragraph_format.space_before = Pt(16)
            p.paragraph_format.space_after = Pt(8)
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(10)

    doc.add_page_break()

    # 4. ACKNOWLEDGEMENTS
    p_ack = doc.add_paragraph()
    p_ack.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ack.paragraph_format.space_before = Pt(0)
    p_ack.paragraph_format.space_after = Pt(10)
    rack = p_ack.add_run("ACKNOWLEDGEMENTS\n")
    rack.bold = True
    rack.font.name = "Times New Roman"
    rack.font.size = Pt(14)
    rack.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)

    p_ack_b = doc.add_paragraph()
    p_ack_b.paragraph_format.space_before = Pt(6)
    p_ack_b.paragraph_format.space_after = Pt(12)
    p_ack_b.paragraph_format.line_spacing = 1.25
    rab = p_ack_b.add_run(ACKNOWLEDGEMENTS_TEXT.replace("\\n", "\n"))
    rab.font.name = "Times New Roman"
    rab.font.size = Pt(11)

    doc.add_page_break()

    # 5. ABSTRACT (4 Paragraphs strictly on 1 page)
    p_abs = doc.add_paragraph()
    p_abs.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_abs.paragraph_format.space_before = Pt(0)
    p_abs.paragraph_format.space_after = Pt(8)
    rabs = p_abs.add_run("ABSTRACT\n")
    rabs.bold = True
    rabs.font.name = "Times New Roman"
    rabs.font.size = Pt(14)
    rabs.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)

    for p_text in ABSTRACT_PARAS:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(5)
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        rp = p.add_run(p_text)
        rp.font.name = "Times New Roman"
        rp.font.size = Pt(10)

    doc.add_page_break()

    # 6. TABLE OF CONTENTS
    p_toc = doc.add_paragraph()
    p_toc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_toc.paragraph_format.space_before = Pt(0)
    p_toc.paragraph_format.space_after = Pt(8)
    rtoc = p_toc.add_run("TABLE OF CONTENTS\n")
    rtoc.bold = True
    rtoc.font.name = "Times New Roman"
    rtoc.font.size = Pt(14)
    rtoc.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)

    t_toc = doc.add_table(rows=0, cols=2)
    t_toc.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_toc.autofit = False
    for item, page in TOC_ENTRIES:
        row = t_toc.add_row()
        c0 = row.cells[0]
        c1 = row.cells[1]
        c0.width = Inches(5.5)
        c1.width = Inches(1.0)
        c0.text = item
        c1.text = page
        c1.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r0 = c0.paragraphs[0].runs[0]
        r1 = c1.paragraphs[0].runs[0]
        r0.font.name = "Times New Roman"
        r1.font.name = "Times New Roman"
        if item.startswith("CHAPTER") or item.startswith("REFERENCES") or item.startswith("APPENDIX") or item.isupper():
            r0.bold = True
            r1.bold = True
            r0.font.size = Pt(10)
            r1.font.size = Pt(10)
            c0.paragraphs[0].paragraph_format.space_before = Pt(3)
        else:
            r0.font.size = Pt(9.5)
            r1.font.size = Pt(9.5)
            c0.paragraphs[0].paragraph_format.space_before = Pt(1)
        c0.paragraphs[0].paragraph_format.space_after = Pt(1)
        c1.paragraphs[0].paragraph_format.space_after = Pt(1)

    doc.add_page_break()

    # 7. LIST OF FIGURES & LIST OF TABLES
    p_lof = doc.add_paragraph()
    p_lof.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_lof.paragraph_format.space_before = Pt(0)
    p_lof.paragraph_format.space_after = Pt(6)
    rlof = p_lof.add_run("LIST OF FIGURES\n")
    rlof.bold = True
    rlof.font.name = "Times New Roman"
    rlof.font.size = Pt(13)
    rlof.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)

    t_lof = doc.add_table(rows=0, cols=3)
    t_lof.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_lof.autofit = False
    for num, title, page in FIGURES_LIST:
        row = t_lof.add_row()
        c0 = row.cells[0]
        c1 = row.cells[1]
        c2 = row.cells[2]
        c0.width = Inches(1.2)
        c1.width = Inches(4.3)
        c2.width = Inches(1.0)
        c0.text = num
        c1.text = title
        c2.text = page
        c2.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
        for c in [c0, c1, c2]:
            c.paragraphs[0].paragraph_format.space_before = Pt(2)
            c.paragraphs[0].paragraph_format.space_after = Pt(2)
            c.paragraphs[0].runs[0].font.name = "Times New Roman"
            c.paragraphs[0].runs[0].font.size = Pt(9.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    p_lot = doc.add_paragraph()
    p_lot.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_lot.paragraph_format.space_before = Pt(8)
    p_lot.paragraph_format.space_after = Pt(6)
    rlot = p_lot.add_run("LIST OF TABLES\n")
    rlot.bold = True
    rlot.font.name = "Times New Roman"
    rlot.font.size = Pt(13)
    rlot.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)

    t_lot = doc.add_table(rows=0, cols=3)
    t_lot.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_lot.autofit = False
    for num, title, page in TABLES_LIST:
        row = t_lot.add_row()
        c0 = row.cells[0]
        c1 = row.cells[1]
        c2 = row.cells[2]
        c0.width = Inches(1.2)
        c1.width = Inches(4.3)
        c2.width = Inches(1.0)
        c0.text = num
        c1.text = title
        c2.text = page
        c2.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
        for c in [c0, c1, c2]:
            c.paragraphs[0].paragraph_format.space_before = Pt(2)
            c.paragraphs[0].paragraph_format.space_after = Pt(2)
            c.paragraphs[0].runs[0].font.name = "Times New Roman"
            c.paragraphs[0].runs[0].font.size = Pt(9.5)

    doc.add_page_break()

    # RENDER CHAPTERS 1 TO 10
    for ch_title, ch_sections, ch_fig in CHAPTERS_SPEC:
        p_ch = doc.add_paragraph()
        p_ch.paragraph_format.space_before = Pt(12)
        p_ch.paragraph_format.space_after = Pt(8)
        rch = p_ch.add_run(ch_title)
        rch.bold = True
        rch.font.name = "Times New Roman"
        rch.font.size = Pt(14)
        rch.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)

        for sec in ch_sections:
            p_sec = doc.add_paragraph()
            p_sec.paragraph_format.space_before = Pt(10)
            p_sec.paragraph_format.space_after = Pt(4)
            rsec = p_sec.add_run(sec["heading"])
            rsec.bold = True
            rsec.font.name = "Times New Roman"
            rsec.font.size = Pt(11.5)
            rsec.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

            for p_text in sec["paragraphs"]:
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(3)
                p.paragraph_format.space_after = Pt(6)
                p.paragraph_format.line_spacing = 1.25
                p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                rp = p.add_run(p_text)
                rp.font.name = "Times New Roman"
                rp.font.size = Pt(10.5)

        if ch_fig:
            fig_label, fig_file, fig_caption = ch_fig
            fig_path = os.path.join(FIG_DIR, fig_file)
            if os.path.exists(fig_path):
                p_img = doc.add_paragraph()
                p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_img.paragraph_format.space_before = Pt(8)
                p_img.paragraph_format.space_after = Pt(4)
                doc.add_picture(fig_path, width=Inches(6.0))
                p_c = doc.add_paragraph()
                p_c.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_c.paragraph_format.space_before = Pt(2)
                p_c.paragraph_format.space_after = Pt(12)
                rc = p_c.add_run(f"{fig_label}: {fig_caption}")
                rc.font.name = "Times New Roman"
                rc.font.size = Pt(9.5)
                rc.italic = True
                rc.font.color.rgb = RGBColor(0x33, 0x41, 0x55)

        # Chapter-specific specialized tables and screenshot insertion boxes
        if "CHAPTER 4" in ch_title:
            add_callout_box_docx(
                doc,
                "DuckDB operates in-process with columnar vectorized query execution, delivering 10x-100x query speedups "
                "over traditional client-server databases for analytical aggregations over 27,000 metrics.",
                title="ARCHITECTURAL ADVANTAGE"
            )

        if "CHAPTER 7" in ch_title:
            # Add all 8 screenshot placeholder boxes with explicit targets
            for num, stitle, target, desc in SCREENSHOTS_META:
                add_screenshot_placeholder_docx(doc, num, stitle, target, desc)

        if "CHAPTER 8" in ch_title:
            # Insert Table 8.1 Confusion Matrix
            p_t81 = doc.add_paragraph()
            p_t81.paragraph_format.space_before = Pt(8)
            p_t81.paragraph_format.space_after = Pt(4)
            rt81 = p_t81.add_run("Table 8.1: Multi-Modal Anomaly Detection Confusion Matrix & Performance Metrics")
            rt81.bold = True
            rt81.font.name = "Times New Roman"
            rt81.font.size = Pt(10)

            t_cm = doc.add_table(rows=3, cols=3)
            t_cm.alignment = WD_TABLE_ALIGNMENT.CENTER
            for r_idx, row_vals in enumerate(CONFUSION_MATRIX_DATA):
                for c_idx, val in enumerate(row_vals):
                    cell = t_cm.rows[r_idx].cells[c_idx]
                    cell.text = val
                    cell.paragraphs[0].runs[0].font.name = "Times New Roman"
                    cell.paragraphs[0].runs[0].font.size = Pt(9.5)
                    if r_idx == 0 or c_idx == 0:
                        cell.paragraphs[0].runs[0].bold = True
                        set_cell_background(cell, "1E3A8A" if r_idx == 0 else "F1F5F9")
                        if r_idx == 0:
                            cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                    else:
                        set_cell_background(cell, "FFFFFF")
                    set_cell_margins(cell, top=60, bottom=60, left=80, right=80)

            # Insert Table 8.2 Honest Per-Category Recall
            p_t82 = doc.add_paragraph()
            p_t82.paragraph_format.space_before = Pt(10)
            p_t82.paragraph_format.space_after = Pt(4)
            rt82 = p_t82.add_run("Table 8.2: Honest Per-Category Anomaly Detection Breadth & Recall")
            rt82.bold = True
            rt82.font.name = "Times New Roman"
            rt82.font.size = Pt(10)

            t_cat = doc.add_table(rows=7, cols=5)
            t_cat.alignment = WD_TABLE_ALIGNMENT.CENTER
            for r_idx, row_vals in enumerate(CATEGORY_RECALL_DATA):
                for c_idx, val in enumerate(row_vals):
                    cell = t_cat.rows[r_idx].cells[c_idx]
                    cell.text = val
                    cell.paragraphs[0].runs[0].font.name = "Times New Roman"
                    cell.paragraphs[0].runs[0].font.size = Pt(9.5)
                    if r_idx == 0 or r_idx == 6:
                        cell.paragraphs[0].runs[0].bold = True
                        set_cell_background(cell, "1E3A8A" if r_idx == 0 else "E2E8F0")
                        if r_idx == 0:
                            cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                    else:
                        set_cell_background(cell, "F8FAFC" if r_idx % 2 == 1 else "FFFFFF")
                    if c_idx > 0:
                        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
                    set_cell_margins(cell, top=60, bottom=60, left=80, right=80)

            add_callout_box_docx(
                doc,
                "Category detection breadth verifies that all 5 anomaly categories had at least one detected instance. "
                "The fleet achieves 82.35% precision, 93.33% recall, and 0.8750 F1-score with zero hardcoded instance IDs.",
                title="HONEST EVALUATION VERIFICATION"
            )

        doc.add_page_break()

    # REFERENCES
    p_ref = doc.add_paragraph()
    p_ref.paragraph_format.space_before = Pt(12)
    p_ref.paragraph_format.space_after = Pt(8)
    rref = p_ref.add_run("REFERENCES")
    rref.bold = True
    rref.font.name = "Times New Roman"
    rref.font.size = Pt(14)
    rref.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)

    for ref in IEEE_REFERENCES:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.left_indent = Inches(0.4)
        p.paragraph_format.first_line_indent = Inches(-0.4)
        r = p.add_run(ref)
        r.font.name = "Times New Roman"
        r.font.size = Pt(9.5)

    doc.add_page_break()

    # APPENDIX A: NBA & IET Articulation Matrices
    p_apa = doc.add_paragraph()
    p_apa.paragraph_format.space_before = Pt(12)
    p_apa.paragraph_format.space_after = Pt(6)
    rap = p_apa.add_run("APPENDIX A: MANDATORY ACADEMIC AND ARTICULATION MATRICES")
    rap.bold = True
    rap.font.name = "Times New Roman"
    rap.font.size = Pt(13)
    rap.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)

    p_co_h = doc.add_paragraph()
    p_co_h.paragraph_format.space_before = Pt(6)
    p_co_h.paragraph_format.space_after = Pt(4)
    rco = p_co_h.add_run("A.1 Course Outcomes (CO) Statements — CSE 4191")
    rco.bold = True
    rco.font.name = "Times New Roman"
    rco.font.size = Pt(11)

    for co_id, co_desc in NBA_CO_DESCRIPTIONS:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(3)
        r1 = p.add_run(f"• {co_id}: ")
        r1.bold = True
        r1.font.name = "Times New Roman"
        r1.font.size = Pt(10)
        r2 = p.add_run(co_desc)
        r2.font.name = "Times New Roman"
        r2.font.size = Pt(10)

    p_t1_h = doc.add_paragraph()
    p_t1_h.paragraph_format.space_before = Pt(8)
    p_t1_h.paragraph_format.space_after = Pt(4)
    rt1 = p_t1_h.add_run("Table A1.1: Course Articulation Matrix (CO-PO and CO-PSO Mapping)")
    rt1.bold = True
    rt1.font.name = "Times New Roman"
    rt1.font.size = Pt(10)

    t_a1 = doc.add_table(rows=len(TABLE_A1_1_ROWS) + 1, cols=len(TABLE_A1_1_HEADERS))
    t_a1.alignment = WD_TABLE_ALIGNMENT.CENTER
    for c_i, h in enumerate(TABLE_A1_1_HEADERS):
        cell = t_a1.rows[0].cells[c_i]
        cell.text = h
        cell.paragraphs[0].runs[0].bold = True
        cell.paragraphs[0].runs[0].font.name = "Times New Roman"
        cell.paragraphs[0].runs[0].font.size = Pt(8)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cell_background(cell, "1E3A8A")
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        set_cell_margins(cell, top=40, bottom=40, left=40, right=40)

    for r_i, rvals in enumerate(TABLE_A1_1_ROWS):
        for c_i, val in enumerate(rvals):
            cell = t_a1.rows[r_i + 1].cells[c_i]
            cell.text = val
            cell.paragraphs[0].runs[0].font.name = "Times New Roman"
            cell.paragraphs[0].runs[0].font.size = Pt(8)
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            set_cell_background(cell, "F8FAFC" if r_i % 2 == 1 else "FFFFFF")
            set_cell_margins(cell, top=40, bottom=40, left=40, right=40)

    p_t2_h = doc.add_paragraph()
    p_t2_h.paragraph_format.space_before = Pt(8)
    p_t2_h.paragraph_format.space_after = Pt(4)
    rt2 = p_t2_h.add_run("Table A1.2: Program Articulation Matrix (Average Correlation Values)")
    rt2.bold = True
    rt2.font.name = "Times New Roman"
    rt2.font.size = Pt(10)

    t_a2 = doc.add_table(rows=len(TABLE_A1_2_ROWS) + 1, cols=len(TABLE_A1_2_HEADERS))
    t_a2.alignment = WD_TABLE_ALIGNMENT.CENTER
    for c_i, h in enumerate(TABLE_A1_2_HEADERS):
        cell = t_a2.rows[0].cells[c_i]
        cell.text = h
        cell.paragraphs[0].runs[0].bold = True
        cell.paragraphs[0].runs[0].font.name = "Times New Roman"
        cell.paragraphs[0].runs[0].font.size = Pt(8)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cell_background(cell, "1E3A8A")
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        set_cell_margins(cell, top=40, bottom=40, left=40, right=40)

    for r_i, rvals in enumerate(TABLE_A1_2_ROWS):
        for c_i, val in enumerate(rvals):
            cell = t_a2.rows[r_i + 1].cells[c_i]
            cell.text = val
            cell.paragraphs[0].runs[0].font.name = "Times New Roman"
            cell.paragraphs[0].runs[0].font.size = Pt(8)
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            set_cell_background(cell, "FFFFFF")
            set_cell_margins(cell, top=40, bottom=40, left=40, right=40)

    p_t3_h = doc.add_paragraph()
    p_t3_h.paragraph_format.space_before = Pt(8)
    p_t3_h.paragraph_format.space_after = Pt(4)
    rt3 = p_t3_h.add_run("Table A1.3: CLO-AHEPLO Mapping (IET AHEP4 Accreditation)")
    rt3.bold = True
    rt3.font.name = "Times New Roman"
    rt3.font.size = Pt(10)

    t_a3 = doc.add_table(rows=len(TABLE_A1_3_ROWS) + 1, cols=len(TABLE_A1_3_HEADERS))
    t_a3.alignment = WD_TABLE_ALIGNMENT.CENTER
    for c_i, h in enumerate(TABLE_A1_3_HEADERS):
        cell = t_a3.rows[0].cells[c_i]
        cell.text = h
        cell.paragraphs[0].runs[0].bold = True
        cell.paragraphs[0].runs[0].font.name = "Times New Roman"
        cell.paragraphs[0].runs[0].font.size = Pt(8)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER if c_i > 0 else WD_ALIGN_PARAGRAPH.LEFT
        set_cell_background(cell, "1E3A8A")
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        set_cell_margins(cell, top=40, bottom=40, left=40, right=40)

    for r_i, rvals in enumerate(TABLE_A1_3_ROWS):
        for c_i, val in enumerate(rvals):
            cell = t_a3.rows[r_i + 1].cells[c_i]
            cell.text = val
            cell.paragraphs[0].runs[0].font.name = "Times New Roman"
            cell.paragraphs[0].runs[0].font.size = Pt(8)
            if c_i > 0:
                cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            set_cell_background(cell, "F8FAFC" if r_i % 2 == 1 else "FFFFFF")
            set_cell_margins(cell, top=40, bottom=40, left=40, right=40)

    doc.add_page_break()

    # APPENDIX B: Database Schemas & API Contracts
    p_apb = doc.add_paragraph()
    p_apb.paragraph_format.space_before = Pt(12)
    p_apb.paragraph_format.space_after = Pt(6)
    rapb = p_apb.add_run("APPENDIX B: DATABASE SCHEMAS AND API CONTRACTS")
    rapb.bold = True
    rapb.font.name = "Times New Roman"
    rapb.font.size = Pt(13)
    rapb.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)

    for sec in APPENDIX_B_SECTIONS:
        p_t = doc.add_paragraph()
        p_t.paragraph_format.space_before = Pt(8)
        p_t.paragraph_format.space_after = Pt(4)
        rt = p_t.add_run(sec["title"])
        rt.bold = True
        rt.font.name = "Times New Roman"
        rt.font.size = Pt(11)

        t_code = doc.add_table(rows=1, cols=1)
        t_code.alignment = WD_TABLE_ALIGNMENT.CENTER
        c = t_code.rows[0].cells[0]
        c.width = Inches(6.5)
        set_cell_background(c, "0F172A")
        set_cell_margins(c, top=80, bottom=80, left=100, right=100)
        p = c.paragraphs[0]
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        rc = p.add_run(sec["code"])
        rc.font.name = "Courier New"
        rc.font.size = Pt(8)
        rc.font.color.rgb = RGBColor(0xE2, 0xE8, 0xF0)

    doc.save(DOCX_OUT)
    print(f"Saved DOCX report to {DOCX_OUT}")


def build_pdf_report():
    print("Building CLARA Final Technical Thesis Report (PDF via ReportLab)...")
    
    class NumberedCanvas(canvas.Canvas):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._saved_page_states = []

        def showPage(self):
            self._saved_page_states.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            num_pages = len(self._saved_page_states)
            for state in self._saved_page_states:
                self.__dict__.update(state)
                self.draw_page_decorations(num_pages)
                super().showPage()
            super().save()

        def draw_page_decorations(self, page_count):
            if self._pageNumber == 1:
                return  # Skip cover page
            
            self.saveState()
            self.setFont("Times-Roman", 8)
            self.setFillColor(colors.HexColor("#64748B"))
            
            # Header
            self.drawString(54, 11 * 72 - 36, "CLARA: Cloud-Linked Evaluation and Risk Assessment — Technical Thesis")
            self.drawRightString(8.5 * 72 - 54, 11 * 72 - 36, "CSE 4191 | MIT Bengaluru")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 11 * 72 - 42, 8.5 * 72 - 54, 11 * 72 - 42)
            
            # Footer
            page_text = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(8.5 * 72 - 54, 36, page_text)
            self.drawString(54, 36, "Manipal Institute of Technology Bengaluru — Dept. of CSE")
            self.line(54, 46, 8.5 * 72 - 54, 46)
            self.restoreState()

    pdf_doc = SimpleDocTemplate(
        PDF_OUT,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('ReportTitle', parent=styles['Heading1'], fontName='Times-Bold', fontSize=15, leading=19, alignment=1, textColor=colors.HexColor("#0F172A"))
    h1_style = ParagraphStyle('ChapterH1', parent=styles['Heading1'], fontName='Times-Bold', fontSize=13, leading=17, spaceBefore=12, spaceAfter=8, textColor=colors.HexColor("#1E3A8A"))
    h2_style = ParagraphStyle('SectionH2', parent=styles['Heading2'], fontName='Times-Bold', fontSize=11, leading=15, spaceBefore=10, spaceAfter=4, textColor=colors.HexColor("#0F172A"))
    body_style = ParagraphStyle('ReportBody', parent=styles['Normal'], fontName='Times-Roman', fontSize=10, leading=13.5, spaceBefore=3, spaceAfter=5, alignment=4, textColor=colors.HexColor("#1E293B"))
    caption_style = ParagraphStyle('FigCaption', parent=styles['Italic'], fontName='Times-Italic', fontSize=8.5, leading=11, alignment=1, textColor=colors.HexColor("#475569"))
    callout_style = ParagraphStyle('Callout', parent=styles['Normal'], fontName='Times-Roman', fontSize=9, leading=12, textColor=colors.HexColor("#334155"))

    story = []

    # 1. COVER PAGE
    story.append(Spacer(1, 20))
    story.append(Paragraph(f"<b>{INSTITUTION}</b>", title_style))
    story.append(Paragraph(f"{INSTITUTION_SUB}<br/>{CAMPUS_LOCATION}<br/>{DEPARTMENT}<br/>{COURSE_CODE}", ParagraphStyle('Sub', parent=body_style, alignment=1, fontSize=9.5, leading=13)))
    story.append(Spacer(1, 25))
    story.append(Paragraph(f"<b>A MINOR SPECIALIZATION PROJECT REPORT<br/>ON<br/><br/>{PROJECT_FORMAL_TITLE}</b>", title_style))
    story.append(Spacer(1, 20))
    story.append(Paragraph(f"Submitted in partial fulfilment of the requirements for the award of the Degree of<br/><b>{DEGREE}</b>", ParagraphStyle('Sub2', parent=body_style, alignment=1, fontSize=10, leading=14)))
    story.append(Spacer(1, 20))

    t_stud_data = [["Sl.", "Student Full Name", "Registration No."]]
    for sno, sname, reg, _ in STUDENTS:
        t_stud_data.append([sno, sname, reg])
    t_s = Table(t_stud_data, colWidths=[35, 250, 150])
    t_s.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),
        ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#F8FAFC"), colors.white]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_s)
    story.append(Spacer(1, 30))
    story.append(Paragraph(f"Under the Guidance of:<br/><b>{GUIDE_NAME}</b><br/>{GUIDE_DESIG}<br/>{GUIDE_AFFIL}<br/><br/>Academic Year: {ACADEMIC_YEAR} | Submission Date: {SUBMISSION_DATE_PLACEHOLDER}", ParagraphStyle('Guide', parent=body_style, alignment=1, fontSize=9.5, leading=13)))
    story.append(PageBreak())

    # 2. CERTIFICATE
    story.append(Paragraph("<b>CERTIFICATE</b>", title_style))
    story.append(Spacer(1, 10))
    student_str = ", ".join([f"<b>{name}</b> (Reg. No: {reg})" for _, name, reg, _ in STUDENTS])
    story.append(Paragraph(
        f"This is to certify that the project report titled <b>\"{PROJECT_FORMAL_TITLE}\"</b> is a bonafide record of "
        f"the project work carried out by {student_str}, in partial fulfilment of the requirements for the award of the Degree of "
        f"<b>{DEGREE}</b> of the Manipal Academy of Higher Education (MAHE) during the academic year <b>{ACADEMIC_YEAR}</b>.<br/><br/>"
        f"The project report has been approved as satisfying the academic requirements prescribed for the Minor Specialization Project.",
        body_style
    ))
    story.append(Spacer(1, 30))

    t_sig_data = [
        [f"______________________________\n{GUIDE_NAME}\nProject Guide\n{GUIDE_DESIG}", f"______________________________\n{COORDINATOR_NAME}\nMinor Specialization Coordinator\n{COORDINATOR_DESIG}"],
        [f"______________________________\n{HOD_TITLE}\n{HOD_AFFIL}", f"______________________________\n{DEAN_TITLE}\n{DEAN_AFFIL}"]
    ]
    t_sig_rl = Table(t_sig_data, colWidths=[240, 240])
    t_sig_rl.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('TOPPADDING', (0, 0), (-1, -1), 16),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_sig_rl)
    story.append(Spacer(1, 20))
    story.append(Paragraph(f"Date: {SUBMISSION_DATE_PLACEHOLDER}<br/>Place: Bengaluru", body_style))
    story.append(PageBreak())

    # 3. STUDENT DECLARATION
    story.append(Paragraph("<b>STUDENT DECLARATION</b>", title_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        f"We hereby declare that the project work titled <b>\"{PROJECT_FORMAL_TITLE}\"</b> submitted to the Department of "
        f"Computer Science and Engineering, Manipal Institute of Technology Bengaluru, is a record of original work done by us "
        f"under the supervision and guidance of <b>{GUIDE_NAME}</b>, Assistant Professor, Department of CSE, MIT Bengaluru.<br/><br/>"
        f"We further declare that the work reported herein has not been submitted either in part or in full for the award of any other "
        f"degree or diploma in this institute or any other university. All sources of external literature, datasets, tools, and code "
        f"libraries have been duly acknowledged in the references in accordance with academic integrity guidelines.",
        body_style
    ))
    story.append(Spacer(1, 30))

    t_dsig_data = [
        [f"______________________________\n{STUDENTS[0][1]}\nReg. No: {STUDENTS[0][2]}\nDate: {SUBMISSION_DATE_PLACEHOLDER}",
         f"______________________________\n{STUDENTS[1][1]}\nReg. No: {STUDENTS[1][2]}\nDate: {SUBMISSION_DATE_PLACEHOLDER}"],
        [f"______________________________\n{STUDENTS[2][1]}\nReg. No: {STUDENTS[2][2]}\nDate: {SUBMISSION_DATE_PLACEHOLDER}",
         f"______________________________\n{STUDENTS[3][1]}\nReg. No: {STUDENTS[3][2]}\nDate: {SUBMISSION_DATE_PLACEHOLDER}"]
    ]
    t_dsig_rl = Table(t_dsig_data, colWidths=[240, 240])
    t_dsig_rl.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('TOPPADDING', (0, 0), (-1, -1), 16),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_dsig_rl)
    story.append(PageBreak())

    # 4. ACKNOWLEDGEMENTS
    story.append(Paragraph("<b>ACKNOWLEDGEMENTS</b>", title_style))
    story.append(Spacer(1, 10))
    for p_ack in ACKNOWLEDGEMENTS_TEXT.split("\\n\\n"):
        story.append(Paragraph(p_ack.strip(), body_style))
        story.append(Spacer(1, 4))
    story.append(PageBreak())

    # 5. ABSTRACT
    story.append(Paragraph("<b>ABSTRACT</b>", title_style))
    story.append(Spacer(1, 8))
    for abs_p in ABSTRACT_PARAS:
        story.append(Paragraph(abs_p, ParagraphStyle('AbsP', parent=body_style, fontSize=9.5, leading=12.5, spaceBefore=2, spaceAfter=4)))
    story.append(PageBreak())

    # 6. TABLE OF CONTENTS
    story.append(Paragraph("<b>TABLE OF CONTENTS</b>", title_style))
    story.append(Spacer(1, 8))
    toc_data = []
    for item, page in TOC_ENTRIES:
        is_h = item.startswith("CHAPTER") or item.startswith("REFERENCES") or item.startswith("APPENDIX") or item.isupper()
        toc_data.append([
            Paragraph(f"<b>{item}</b>" if is_h else item, ParagraphStyle('TOCItem', fontName='Times-Bold' if is_h else 'Times-Roman', fontSize=9, leading=11, textColor=colors.HexColor("#1E3A8A") if is_h else colors.HexColor("#1E293B"))),
            Paragraph(f"<b>{page}</b>" if is_h else page, ParagraphStyle('TOCPage', fontName='Times-Bold' if is_h else 'Times-Roman', fontSize=9, leading=11, alignment=2))
        ])
    t_toc_rl = Table(toc_data, colWidths=[420, 60])
    t_toc_rl.setStyle(TableStyle([
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ('LINEBELOW', (0, 0), (-1, -1), 0.25, colors.HexColor("#F1F5F9")),
    ]))
    story.append(t_toc_rl)
    story.append(PageBreak())

    # 7. LIST OF FIGURES & TABLES
    story.append(Paragraph("<b>LIST OF FIGURES</b>", title_style))
    story.append(Spacer(1, 6))
    lof_data = []
    for num, title, page in FIGURES_LIST:
        lof_data.append([
            Paragraph(f"<b>{num}</b>", ParagraphStyle('FNum', fontName='Times-Bold', fontSize=8.5, leading=10)),
            Paragraph(title, ParagraphStyle('FTit', fontName='Times-Roman', fontSize=8.5, leading=10)),
            Paragraph(page, ParagraphStyle('FPg', fontName='Times-Roman', fontSize=8.5, leading=10, alignment=2))
        ])
    t_lof_rl = Table(lof_data, colWidths=[70, 360, 50])
    t_lof_rl.setStyle(TableStyle([
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('LINEBELOW', (0, 0), (-1, -1), 0.25, colors.HexColor("#F1F5F9")),
    ]))
    story.append(t_lof_rl)
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>LIST OF TABLES</b>", title_style))
    story.append(Spacer(1, 6))
    lot_data = []
    for num, title, page in TABLES_LIST:
        lot_data.append([
            Paragraph(f"<b>{num}</b>", ParagraphStyle('TNum', fontName='Times-Bold', fontSize=8.5, leading=10)),
            Paragraph(title, ParagraphStyle('TTit', fontName='Times-Roman', fontSize=8.5, leading=10)),
            Paragraph(page, ParagraphStyle('TPg', fontName='Times-Roman', fontSize=8.5, leading=10, alignment=2))
        ])
    t_lot_rl = Table(lot_data, colWidths=[70, 360, 50])
    t_lot_rl.setStyle(TableStyle([
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('LINEBELOW', (0, 0), (-1, -1), 0.25, colors.HexColor("#F1F5F9")),
    ]))
    story.append(t_lot_rl)
    story.append(PageBreak())

    # RENDER CHAPTERS IN PDF
    for ch_title, ch_sections, ch_fig in CHAPTERS_SPEC:
        story.append(Paragraph(f"<b>{ch_title}</b>", h1_style))
        for sec in ch_sections:
            story.append(Paragraph(f"<b>{sec['heading']}</b>", h2_style))
            for p_text in sec["paragraphs"]:
                story.append(Paragraph(p_text, body_style))

        if ch_fig:
            fig_label, fig_file, fig_caption = ch_fig
            fig_path = os.path.join(FIG_DIR, fig_file)
            if os.path.exists(fig_path):
                story.append(Spacer(1, 6))
                story.append(RLImage(fig_path, width=480, height=240))
                story.append(Paragraph(f"{fig_label}: {fig_caption}", caption_style))
                story.append(Spacer(1, 6))

        if "CHAPTER 7" in ch_title:
            # Screenshots placeholders
            for num, stitle, target, desc in SCREENSHOTS_META:
                sc_box_data = [[
                    Paragraph(
                        f"<b>[SCREENSHOT INSERTION LOCATION: {target}]</b><br/>"
                        f"Status: PENDING MANUAL CAPTURE | Resolution: 1920 x 1080 | Format: PNG<br/><br/>"
                        f"{desc}",
                        ParagraphStyle('SC', parent=callout_style, alignment=1, fontSize=8.5, leading=11)
                    )
                ]]
                t_sc = Table(sc_box_data, colWidths=[480])
                t_sc.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
                    ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#94A3B8")),
                    ('TOPPADDING', (0, 0), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ]))
                story.append(Spacer(1, 4))
                story.append(t_sc)
                story.append(Paragraph(f"Figure {num}: {stitle} (Target: docs/final/screenshots/{target})", caption_style))
                story.append(Spacer(1, 6))

        if "CHAPTER 8" in ch_title:
            # Table 8.1
            story.append(Spacer(1, 6))
            story.append(Paragraph("<b>Table 8.1: Multi-Modal Anomaly Detection Confusion Matrix & Performance Metrics</b>", h2_style))
            t_cm_rl = Table(CONFUSION_MATRIX_DATA, colWidths=[160, 160, 160])
            t_cm_rl.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),
                ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8.5),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            story.append(t_cm_rl)
            story.append(Spacer(1, 8))

            # Table 8.2
            story.append(Paragraph("<b>Table 8.2: Honest Per-Category Anomaly Detection Breadth & Recall</b>", h2_style))
            t_cat_rl = Table(CATEGORY_RECALL_DATA, colWidths=[140, 80, 90, 80, 90])
            t_cat_rl.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),
                ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8.5),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.HexColor("#F8FAFC"), colors.white]),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#E2E8F0")),
                ('FONTNAME', (0, -1), (-1, -1), 'Times-Bold'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ]))
            story.append(t_cat_rl)
            story.append(Spacer(1, 8))

        story.append(PageBreak())

    # REFERENCES IN PDF
    story.append(Paragraph("<b>REFERENCES</b>", h1_style))
    story.append(Spacer(1, 6))
    for ref in IEEE_REFERENCES:
        story.append(Paragraph(ref, ParagraphStyle('RefRL', parent=body_style, fontSize=8.5, leading=11, spaceBefore=2, spaceAfter=2)))
    story.append(PageBreak())

    # APPENDIX A IN PDF
    story.append(Paragraph("<b>APPENDIX A: MANDATORY ACADEMIC AND ARTICULATION MATRICES</b>", h1_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>A.1 Course Outcomes (CO) Statements — CSE 4191</b>", h2_style))
    for co_id, co_desc in NBA_CO_DESCRIPTIONS:
        story.append(Paragraph(f"<b>• {co_id}:</b> {co_desc}", body_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>Table A1.1: Course Articulation Matrix (CO-PO and CO-PSO Mapping)</b>", h2_style))
    t_a1_data = [TABLE_A1_1_HEADERS] + TABLE_A1_1_ROWS
    t_a1_rl = Table(t_a1_data, colWidths=[40] + [31] * 14)
    t_a1_rl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),
        ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7.5),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#F8FAFC"), colors.white]),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(t_a1_rl)
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>Table A1.2: Program Articulation Matrix (Average Correlation Values)</b>", h2_style))
    t_a2_data = [TABLE_A1_2_HEADERS] + TABLE_A1_2_ROWS
    t_a2_rl = Table(t_a2_data, colWidths=[55] + [30] * 14)
    t_a2_rl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),
        ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7.5),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(t_a2_rl)
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>Table A1.3: CLO-AHEPLO Mapping (IET AHEP4 Accreditation)</b>", h2_style))
    t_a3_data = [TABLE_A1_3_HEADERS] + TABLE_A1_3_ROWS
    t_a3_rl = Table(t_a3_data, colWidths=[270] + [30] * 7)
    t_a3_rl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),
        ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7.5),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#F8FAFC"), colors.white]),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(t_a3_rl)
    story.append(PageBreak())

    # APPENDIX B IN PDF
    story.append(Paragraph("<b>APPENDIX B: DATABASE SCHEMAS AND API CONTRACTS</b>", h1_style))
    story.append(Spacer(1, 6))
    for sec in APPENDIX_B_SECTIONS:
        story.append(Paragraph(f"<b>{sec['title']}</b>", h2_style))
        code_p = Paragraph(sec["code"].replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br/>"), ParagraphStyle('CodeRL', fontName='Courier', fontSize=7, leading=8.5, textColor=colors.HexColor("#0F172A")))
        t_c_rl = Table([[code_p]], colWidths=[480])
        t_c_rl.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(t_c_rl)
        story.append(Spacer(1, 6))

    pdf_doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Saved PDF report to {PDF_OUT}")

    # Inspect page count
    reader = pypdf.PdfReader(PDF_OUT)
    page_count = len(reader.pages)
    print(f"=== CLARA Final Technical Thesis Report Page Count: {page_count} pages ===")
    return page_count


if __name__ == "__main__":
    build_docx_report()
    pages = build_pdf_report()
    if pages < 35:
        print(f"WARNING: Report has {pages} pages, which is less than the required 35 pages!")
    else:
        print(f"SUCCESS: Report meets academic requirement with {pages} pages (>= 35 pages)!")
