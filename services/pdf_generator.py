from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
import json
import os


def generate_pdf(resume):
    data = json.loads(resume.resume_data)

    if resume.template_id == 1:
        return generate_standard(data, resume.id)
    elif resume.template_id == 2:
        return generate_modern(data, resume.id)
    elif resume.template_id == 3:
        return generate_minimal(data, resume.id)
    else:
        return generate_academic(data, resume.id)


def generate_standard(data, resume_id):
    os.makedirs("generated_pdfs", exist_ok=True)
    file_path = f"generated_pdfs/standard_{resume_id}.pdf"

    doc = SimpleDocTemplate(file_path)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph(f"<b>{data.get('name','')}</b>", styles["Title"]))
    elements.append(Spacer(1, 0.3 * inch))

    for key, value in data.items():
        if key != "name":
            elements.append(Paragraph(f"<b>{key.capitalize()}:</b>", styles["Heading3"]))
            elements.append(Paragraph(str(value), styles["Normal"]))
            elements.append(Spacer(1, 0.2 * inch))

    doc.build(elements)
    return file_path


def generate_modern(data, resume_id):
    os.makedirs("generated_pdfs", exist_ok=True)
    file_path = f"generated_pdfs/modern_{resume_id}.pdf"

    doc = SimpleDocTemplate(file_path)
    elements = []
    styles = getSampleStyleSheet()

    name_style = ParagraphStyle(
        'NameStyle',
        parent=styles['Title'],
        textColor=colors.HexColor("#1E88E5")
    )

    section_style = ParagraphStyle(
        'SectionStyle',
        parent=styles['Heading2'],
        textColor=colors.HexColor("#43A047")
    )

    elements.append(Paragraph(data.get("name",""), name_style))
    elements.append(Spacer(1, 0.4 * inch))

    for key, value in data.items():
        if key != "name":
            elements.append(Paragraph(key.upper(), section_style))
            elements.append(Paragraph(str(value), styles["Normal"]))
            elements.append(Spacer(1, 0.3 * inch))

    doc.build(elements)
    return file_path


def generate_minimal(data, resume_id):
    os.makedirs("generated_pdfs", exist_ok=True)
    file_path = f"generated_pdfs/minimal_{resume_id}.pdf"

    doc = SimpleDocTemplate(file_path)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph(f"<b>{data.get('name','')}</b>", styles["Title"]))
    elements.append(Spacer(1, 0.4 * inch))

    for key, value in data.items():
        if key != "name":
            elements.append(Paragraph(key.capitalize(), styles["Heading4"]))
            elements.append(Paragraph(str(value), styles["Normal"]))
            elements.append(Spacer(1, 0.2 * inch))

    doc.build(elements)
    return file_path


def generate_academic(data, resume_id):
    os.makedirs("generated_pdfs", exist_ok=True)
    file_path = f"generated_pdfs/academic_{resume_id}.pdf"

    doc = SimpleDocTemplate(file_path)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph(f"<b>{data.get('name','')}</b>", styles["Title"]))
    elements.append(Spacer(1, 0.3 * inch))

    for key, value in data.items():
        if key != "name":
            elements.append(Paragraph(key.capitalize(), styles["Heading2"]))
            elements.append(Paragraph(str(value), styles["Normal"]))
            elements.append(Spacer(1, 0.25 * inch))

    doc.build(elements)
    return file_path