"""
utils.py
========
Helper utilities:
  - parse_answer_key   : parse text/CSV/JSON answer key input
  - generate_pdf       : create a PDF result report using ReportLab
"""

import io
import json
import csv
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                Paragraph, Spacer, HRFlowable)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER


# ─────────────────────────────────────────────
# Answer key parsers
# ─────────────────────────────────────────────

def parse_answer_key(raw: str, fmt: str = 'auto') -> dict:
    """
    Parse an answer key from various formats.

    Supported formats
    -----------------
    - text/auto : "1=A, 2=B, 3=C"  OR  "1:A 2:B 3:C"
    - json      : '{"1":"A","2":"B"}'
    - csv       : "1,A\\n2,B\\n3,C"

    Returns {question_number(str): answer(str)} dict.
    """
    raw = raw.strip()
    if not raw:
        return {}

    # JSON
    if fmt == 'json' or (fmt == 'auto' and raw.startswith('{')):
        data = json.loads(raw)
        return {str(k): str(v).upper() for k, v in data.items()}

    # CSV
    if fmt == 'csv' or (fmt == 'auto' and ',' in raw and '=' not in raw and ':' not in raw):
        reader = csv.reader(io.StringIO(raw))
        result = {}
        for row in reader:
            if len(row) >= 2:
                result[row[0].strip()] = row[1].strip().upper()
        return result

    # Text "1=A, 2=B" or "1:A 2:B"
    result = {}
    # Normalise separators
    cleaned = raw.replace(':', '=').replace(';', ',').replace('\n', ',')
    for token in cleaned.split(','):
        token = token.strip()
        if '=' in token:
            parts = token.split('=', 1)
            if len(parts) == 2:
                q, a = parts
                result[q.strip()] = a.strip().upper()
    return result


# ─────────────────────────────────────────────
# PDF report generator
# ─────────────────────────────────────────────

def generate_pdf(result_data: dict, student_name: str = 'Student') -> bytes:
    """
    Generate a PDF result report.

    Parameters
    ----------
    result_data  : full result dict returned by process_omr()
    student_name : optional name for the header

    Returns
    -------
    bytes : PDF file content
    """
    buf    = io.BytesIO()
    doc    = SimpleDocTemplate(buf, pagesize=A4,
                               leftMargin=2*cm, rightMargin=2*cm,
                               topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle('Title2', parent=styles['Title'],
                                 fontSize=22, textColor=colors.HexColor('#4F46E5'),
                                 alignment=TA_CENTER, spaceAfter=6)
    sub_style   = ParagraphStyle('Sub', parent=styles['Normal'],
                                 fontSize=11, textColor=colors.grey,
                                 alignment=TA_CENTER, spaceAfter=12)
    heading_style = ParagraphStyle('Heading', parent=styles['Heading2'],
                                   textColor=colors.HexColor('#1E1B4B'), spaceAfter=6)

    elements = []

    # ── Header ──────────────────────────────
    elements.append(Paragraph('OMR Result Report', title_style))
    elements.append(Paragraph(f'Student: {student_name}', sub_style))
    elements.append(HRFlowable(width='100%', thickness=1,
                               color=colors.HexColor('#C7D2FE')))
    elements.append(Spacer(1, 0.4*cm))

    # ── Score Summary ────────────────────────
    elements.append(Paragraph('Score Summary', heading_style))
    summary_data = [
        ['Metric', 'Value'],
        ['Score', f"{result_data.get('score', 0)} / {result_data.get('total', 0)}"],
        ['Percentage', f"{result_data.get('percentage', 0)}%"],
        ['Correct Answers', str(result_data.get('correct', 0))],
        ['Wrong Answers', str(result_data.get('wrong', 0))],
        ['Unattempted', str(result_data.get('unattempted', 0))],
    ]
    summary_table = Table(summary_data, colWidths=[8*cm, 8*cm])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND',   (0, 0), (-1, 0), colors.HexColor('#4F46E5')),
        ('TEXTCOLOR',    (0, 0), (-1, 0), colors.white),
        ('FONTNAME',     (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',     (0, 0), (-1, 0), 12),
        ('ALIGN',        (0, 0), (-1, -1), 'CENTER'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1),
         [colors.HexColor('#EEF2FF'), colors.white]),
        ('GRID',         (0, 0), (-1, -1), 0.5, colors.HexColor('#C7D2FE')),
        ('TOPPADDING',   (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 6),
        ('FONTSIZE',     (0, 1), (-1, -1), 11),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 0.6*cm))

    # ── Per-question table ───────────────────
    elements.append(Paragraph('Detailed Answers', heading_style))
    table_data = [['Q#', 'Correct Answer', 'Student Answer', 'Result']]
    for row in result_data.get('questions_table', []):
        result_label = {
            'correct':     '✓ Correct',
            'wrong':       '✗ Wrong',
            'unattempted': '– Skipped',
        }.get(row['result'], row['result'])
        table_data.append([
            str(row['q']),
            row['correct'],
            row['student'],
            result_label,
        ])

    q_table = Table(table_data, colWidths=[2.5*cm, 4.5*cm, 4.5*cm, 4.5*cm])
    row_colors = []
    for i, row in enumerate(result_data.get('questions_table', []), start=1):
        if row['result'] == 'correct':
            row_colors.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#D1FAE5')))
        elif row['result'] == 'wrong':
            row_colors.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#FEE2E2')))
        else:
            row_colors.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#F3F4F6')))

    q_table.setStyle(TableStyle([
        ('BACKGROUND',   (0, 0), (-1, 0), colors.HexColor('#4F46E5')),
        ('TEXTCOLOR',    (0, 0), (-1, 0), colors.white),
        ('FONTNAME',     (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN',        (0, 0), (-1, -1), 'CENTER'),
        ('GRID',         (0, 0), (-1, -1), 0.5, colors.HexColor('#C7D2FE')),
        ('TOPPADDING',   (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 5),
        ('FONTSIZE',     (0, 1), (-1, -1), 10),
    ] + row_colors))
    elements.append(q_table)

    doc.build(elements)
    return buf.getvalue()
