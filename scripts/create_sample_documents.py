"""Script to generate realistic sample documents covering all 10 test scenarios."""

import os
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak


def setup_directories():
    base_dir = Path(__file__).resolve().parent.parent
    sample_docs_dir = base_dir / "sample_documents"
    sample_outputs_dir = base_dir / "sample_outputs"
    sample_docs_dir.mkdir(parents=True, exist_ok=True)
    sample_outputs_dir.mkdir(parents=True, exist_ok=True)
    return sample_docs_dir, sample_outputs_dir


def create_clean_digital_pdf(output_path: Path):
    """1. Clean digital PDF with MCQs, True/False, and Fill-in-the-blank."""
    doc = SimpleDocTemplate(str(output_path), pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle("TitleStyle", parent=styles["Heading1"], alignment=1, spaceAfter=20)
    q_style = ParagraphStyle("QuestionStyle", parent=styles["Normal"], fontSize=11, leading=14, spaceBefore=10)
    opt_style = ParagraphStyle("OptionStyle", parent=styles["Normal"], fontSize=10, leading=13, leftIndent=20)

    story.append(Paragraph("Computer Science Examination 2026", title_style))
    story.append(Spacer(1, 10))

    # Q1: MCQ
    story.append(Paragraph("1. Which data structure operates on a First-In-First-Out (FIFO) basis?", q_style))
    story.append(Paragraph("A. Stack", opt_style))
    story.append(Paragraph("B. Queue", opt_style))
    story.append(Paragraph("C. Binary Tree", opt_style))
    story.append(Paragraph("D. Graph", opt_style))

    # Q2: True/False
    story.append(Paragraph("2. In Python, tuples are immutable data types. True or False?", q_style))
    story.append(Paragraph("A. True", opt_style))
    story.append(Paragraph("B. False", opt_style))

    # Q3: Fill in the blank
    story.append(Paragraph("3. The time complexity of accessing an element in an array by index is _____ in big-O notation.", q_style))
    story.append(Paragraph("A. O(1)", opt_style))
    story.append(Paragraph("B. O(n)", opt_style))
    story.append(Paragraph("C. O(log n)", opt_style))
    story.append(Paragraph("D. O(n^2)", opt_style))

    # Q4: Short Answer
    story.append(Paragraph("4. Define what an IP address is and explain its purpose.", q_style))

    doc.build(story)


def create_multipage_question_pdf(output_path: Path):
    """6. Multi-page question where Question 15 starts on page 1 and options are on page 2."""
    doc = SimpleDocTemplate(str(output_path), pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle("TitleStyle", parent=styles["Heading1"], alignment=1, spaceAfter=20)
    q_style = ParagraphStyle("QuestionStyle", parent=styles["Normal"], fontSize=11, leading=14, spaceBefore=10)
    opt_style = ParagraphStyle("OptionStyle", parent=styles["Normal"], fontSize=10, leading=13, leftIndent=20)

    story.append(Paragraph("Advanced Computer Networks - Part I", title_style))
    story.append(Paragraph("14. What protocol is primarily used for secure web browsing?", q_style))
    story.append(Paragraph("A. HTTP", opt_style))
    story.append(Paragraph("B. HTTPS", opt_style))
    story.append(Paragraph("C. FTP", opt_style))
    story.append(Paragraph("D. SMTP", opt_style))
    story.append(Spacer(1, 20))

    # Question 15 begins on page 1
    story.append(Paragraph("15. Which of the following statements is correct regarding Transport Layer Security (TLS) and handshake negotiation", q_style))

    story.append(PageBreak())

    # Question 15 continues on page 2 with options
    story.append(Paragraph("in modern cryptographic communication protocols?", q_style))
    story.append(Paragraph("A. TLS 1.3 requires more round trips than TLS 1.2.", opt_style))
    story.append(Paragraph("B. TLS 1.3 reduces the handshake latency to 1-RTT or 0-RTT.", opt_style))
    story.append(Paragraph("C. TLS operates at the Data Link Layer.", opt_style))
    story.append(Paragraph("D. RSA key exchange is mandatory in TLS 1.3.", opt_style))

    story.append(Paragraph("16. Which port is the standard default for DNS service queries?", q_style))
    story.append(Paragraph("A. 22", opt_style))
    story.append(Paragraph("B. 53", opt_style))
    story.append(Paragraph("C. 80", opt_style))
    story.append(Paragraph("D. 443", opt_style))

    doc.build(story)


def create_exam_with_inline_answers_pdf(output_path: Path):
    """7. Exam with Answer Key section at the end."""
    doc = SimpleDocTemplate(str(output_path), pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle("TitleStyle", parent=styles["Heading1"], alignment=1, spaceAfter=20)
    q_style = ParagraphStyle("QuestionStyle", parent=styles["Normal"], fontSize=11, leading=14, spaceBefore=10)
    opt_style = ParagraphStyle("OptionStyle", parent=styles["Normal"], fontSize=10, leading=13, leftIndent=20)

    story.append(Paragraph("General Science Quiz", title_style))
    story.append(Paragraph("1. What is the chemical symbol for Gold?", q_style))
    story.append(Paragraph("A. Ag", opt_style))
    story.append(Paragraph("B. Au", opt_style))
    story.append(Paragraph("C. Fe", opt_style))
    story.append(Paragraph("D. Cu", opt_style))

    story.append(Paragraph("2. Which planet is known as the Red Planet?", q_style))
    story.append(Paragraph("A. Venus", opt_style))
    story.append(Paragraph("B. Mars", opt_style))
    story.append(Paragraph("C. Jupiter", opt_style))
    story.append(Paragraph("D. Saturn", opt_style))

    story.append(Paragraph("3. What gas do plants absorb during photosynthesis?", q_style))
    story.append(Paragraph("A. Oxygen", opt_style))
    story.append(Paragraph("B. Carbon Dioxide", opt_style))
    story.append(Paragraph("C. Nitrogen", opt_style))
    story.append(Paragraph("D. Hydrogen", opt_style))

    story.append(Spacer(1, 40))
    story.append(Paragraph("Answer Key", ParagraphStyle("Header", parent=styles["Heading2"], spaceBefore=20)))
    story.append(Paragraph("1. B", opt_style))
    story.append(Paragraph("2. B", opt_style))
    story.append(Paragraph("3. B", opt_style))

    doc.build(story)


def create_separate_answer_key_pdf(output_path: Path):
    """8. Standalone Answer Key document."""
    doc = SimpleDocTemplate(str(output_path), pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle("TitleStyle", parent=styles["Heading1"], alignment=1, spaceAfter=20)
    entry_style = ParagraphStyle("EntryStyle", parent=styles["Normal"], fontSize=11, leading=15)

    story.append(Paragraph("Official Answer Key - Computer Science 2026", title_style))
    story.append(Spacer(1, 20))
    story.append(Paragraph("1. B", entry_style))
    story.append(Paragraph("2. A", entry_style))
    story.append(Paragraph("3. A", entry_style))
    story.append(Paragraph("4. An IP address is a unique numerical label assigned to each device connected to a computer network.", entry_style))

    doc.build(story)


def create_unclear_question_pdf(output_path: Path):
    """10. Unclear question with missing option numbers and ambiguity."""
    doc = SimpleDocTemplate(str(output_path), pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle("TitleStyle", parent=styles["Heading1"], alignment=1, spaceAfter=20)
    q_style = ParagraphStyle("QuestionStyle", parent=styles["Normal"], fontSize=11, leading=14, spaceBefore=10)

    story.append(Paragraph("Draft Examination - Needs Review", title_style))
    story.append(Paragraph("Q1. What is the capital of Australia?", q_style))
    story.append(Paragraph("Sydney or Canberra or Melbourne", q_style))
    story.append(Paragraph("99. Incomplete prompt without question mark or choices", q_style))

    doc.build(story)


def create_image_question_paper(output_path: Path, format: str = "PNG"):
    """4 & 5. JPG / PNG question paper image."""
    img = Image.new("RGB", (1600, 1200), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Render text onto image
    draw.text((600, 60), "Mathematics Diagnostic Test", fill=(0, 0, 0))

    y = 150
    draw.text((100, y), "1. What is the value of 2^8?", fill=(0, 0, 0))
    y += 40
    draw.text((150, y), "A. 128", fill=(0, 0, 0))
    y += 35
    draw.text((150, y), "B. 256", fill=(0, 0, 0))
    y += 35
    draw.text((150, y), "C. 512", fill=(0, 0, 0))
    y += 35
    draw.text((150, y), "D. 1024", fill=(0, 0, 0))

    y += 70
    draw.text((100, y), "2. Solve for x: 3x + 9 = 24", fill=(0, 0, 0))
    y += 40
    draw.text((150, y), "A. 3", fill=(0, 0, 0))
    y += 35
    draw.text((150, y), "B. 5", fill=(0, 0, 0))
    y += 35
    draw.text((150, y), "C. 7", fill=(0, 0, 0))
    y += 35
    draw.text((150, y), "D. 9", fill=(0, 0, 0))

    img.save(str(output_path), format=format)


def create_scanned_pdf(output_path: Path, low_quality: bool = False):
    """2 & 3. Scanned PDF with simulated blur, noise, and rotation."""
    img = Image.new("RGB", (1240, 1754), color=(245, 245, 240))
    draw = ImageDraw.Draw(img)

    draw.text((450, 100), "Physics Scanned Test Paper", fill=(20, 20, 20))

    y = 250
    draw.text((120, y), "1. What is the acceleration due to gravity on Earth?", fill=(30, 30, 30))
    y += 50
    draw.text((180, y), "A. 9.8 m/s^2", fill=(30, 30, 30))
    y += 45
    draw.text((180, y), "B. 8.9 m/s^2", fill=(30, 30, 30))
    y += 45
    draw.text((180, y), "C. 10.8 m/s^2", fill=(30, 30, 30))
    y += 45
    draw.text((180, y), "D. 12.0 m/s^2", fill=(30, 30, 30))

    if low_quality:
        # Add blur and noise
        img = img.filter(ImageFilter.GaussianBlur(radius=1.5))
        # Slight rotation
        img = img.rotate(2.5, resample=Image.BICUBIC, fillcolor=(240, 240, 240))
    else:
        img = img.rotate(0.8, resample=Image.BICUBIC, fillcolor=(245, 245, 240))

    img.save(str(output_path), "PDF", resolution=150.0)


def create_invalid_file(output_path: Path):
    """9. Invalid corrupted file disguised as PDF."""
    with open(output_path, "wb") as f:
        f.write(b"This is a corrupted text file that is not a valid PDF document at all.")


def generate_sample_outputs(output_dir: Path):
    """Generates sample output JSONs matching the Section 17 schema."""
    sample_q1 = {
        "id": "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
        "document_id": "d1e2f3a4-b5c6-4d7e-8f9a-0b1c2d3e4f5a",
        "question_number": "1",
        "question": "Which data structure operates on a First-In-First-Out (FIFO) basis?",
        "question_type": "MCQ",
        "options": [
            {"key": "A", "text": "Stack", "confidence": 1.0},
            {"key": "B", "text": "Queue", "confidence": 1.0},
            {"key": "C", "text": "Binary Tree", "confidence": 1.0},
            {"key": "D", "text": "Graph", "confidence": 1.0},
        ],
        "answer": {
            "value": "B",
            "confidence": 0.95,
            "matching_status": "MATCHED",
            "source_document_id": "d1e2f3a4-b5c6-4d7e-8f9a-0b1c2d3e4f5a",
            "source_page": 1,
        },
        "source": {
            "document_id": "d1e2f3a4-b5c6-4d7e-8f9a-0b1c2d3e4f5a",
            "pages": [1],
        },
        "confidence": 0.94,
        "extraction_status": "SUCCESS",
    }

    sample_multipage = {
        "id": "b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e",
        "document_id": "e2f3a4b5-c6d7-4e8f-9a0b-1c2d3e4f5a6b",
        "question_number": "15",
        "question": "Which of the following statements is correct regarding Transport Layer Security (TLS) and handshake negotiation in modern cryptographic communication protocols?",
        "question_type": "MCQ",
        "options": [
            {"key": "A", "text": "TLS 1.3 requires more round trips than TLS 1.2.", "confidence": 0.95},
            {"key": "B", "text": "TLS 1.3 reduces the handshake latency to 1-RTT or 0-RTT.", "confidence": 0.95},
            {"key": "C", "text": "TLS operates at the Data Link Layer.", "confidence": 0.95},
            {"key": "D", "text": "RSA key exchange is mandatory in TLS 1.3.", "confidence": 0.95},
        ],
        "answer": None,
        "source": {
            "document_id": "e2f3a4b5-c6d7-4e8f-9a0b-1c2d3e4f5a6b",
            "pages": [1, 2],
        },
        "confidence": 0.88,
        "extraction_status": "SUCCESS",
    }

    sample_review = {
        "id": "c3d4e5f6-a7b8-4c9d-0e1f-2a3b4c5d6e7f",
        "document_id": "f3a4b5c6-d7e8-4f9a-0b1c-2d3e4f5a6b7c",
        "question_id": "d4e5f6a7-b8c9-4d0e-1f2a-3b4c5d6e7f8a",
        "issue_type": "OPTIONS_UNCERTAIN",
        "description": "Question options could not be cleanly identified.",
        "severity": "MEDIUM",
        "resolved": False,
        "created_at": "2026-09-19T22:00:00Z",
    }

    with open(output_dir / "clean_digital_extracted.json", "w") as f:
        json.dump([sample_q1], f, indent=2)

    with open(output_dir / "multipage_extracted.json", "w") as f:
        json.dump([sample_multipage], f, indent=2)

    with open(output_dir / "sample_review_items.json", "w") as f:
        json.dump([sample_review], f, indent=2)


def main():
    docs_dir, outputs_dir = setup_directories()
    print(f"Generating sample documents in {docs_dir}...")

    # 1. Clean digital PDF
    create_clean_digital_pdf(docs_dir / "clean_digital.pdf")

    # 2. Scanned PDF
    create_scanned_pdf(docs_dir / "scanned_exam.pdf", low_quality=False)

    # 3. Low-quality scan
    create_scanned_pdf(docs_dir / "low_quality_scan.pdf", low_quality=True)

    # 4. JPG question paper
    create_image_question_paper(docs_dir / "question_paper.jpg", format="JPEG")

    # 5. PNG question paper
    create_image_question_paper(docs_dir / "question_paper.png", format="PNG")

    # 6. Multi-page question PDF
    create_multipage_question_pdf(docs_dir / "multipage_question.pdf")

    # 7. Exam with inline answer key
    create_exam_with_inline_answers_pdf(docs_dir / "exam_with_inline_answers.pdf")

    # 8. Separate answer key PDF
    create_separate_answer_key_pdf(docs_dir / "separate_answer_key.pdf")

    # 9. Invalid file
    create_invalid_file(docs_dir / "invalid_document.pdf")

    # 10. Unclear question PDF
    create_unclear_question_pdf(docs_dir / "unclear_question.pdf")

    # Generate sample output JSONs
    generate_sample_outputs(outputs_dir)

    print("All 10 sample documents and expected JSON outputs successfully created.")


if __name__ == "__main__":
    main()
