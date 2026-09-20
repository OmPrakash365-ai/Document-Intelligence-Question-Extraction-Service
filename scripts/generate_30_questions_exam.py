"""Script to generate a comprehensive 30-question exam paper PDF."""

from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, HRFlowable


def generate_30_questions_pdf(output_path: Path):
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle(
        "ExamTitle",
        parent=styles["Heading1"],
        fontSize=18,
        leading=22,
        alignment=1,
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "ExamSubtitle",
        parent=styles["Normal"],
        fontSize=11,
        leading=14,
        alignment=1,
        textColor="#555555",
        spaceAfter=15,
    )
    section_style = ParagraphStyle(
        "SectionHeader",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        spaceBefore=12,
        spaceAfter=8,
        textColor="#1a365d",
    )
    q_style = ParagraphStyle(
        "QuestionText",
        parent=styles["Normal"],
        fontSize=10,
        leading=13,
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True,
    )
    opt_style = ParagraphStyle(
        "OptionText",
        parent=styles["Normal"],
        fontSize=9.5,
        leading=12,
        leftIndent=15,
        spaceAfter=2,
    )
    key_style = ParagraphStyle(
        "KeyText",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        spaceAfter=4,
    )

    # Header
    story.append(Paragraph("National Science & Technology Examination 2026", title_style))
    story.append(Paragraph("Standard Multiple Choice Assessment — Total Questions: 30 | Time: 45 Minutes", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color="#1a365d", spaceAfter=15))

    questions = [
        # Section A: Computer Science & Programming (1-10)
        ("1. Which data structure operates on a First-In-First-Out (FIFO) basis?",
         ["A. Stack", "B. Queue", "C. Binary Tree", "D. Hash Table"]),
        ("2. In computer architecture, what does ALU stand for?",
         ["A. Arithmetic Logic Unit", "B. Advanced Link Unit", "C. Array Logic Universal", "D. Application Level Utility"]),
        ("3. Which memory management scheme allows non-contiguous physical address space allocation?",
         ["A. Contiguous Allocation", "B. Paging", "C. Swapping", "D. Fixed Partitioning"]),
        ("4. What is the standard default port used for HTTP communication?",
         ["A. 21", "B. 80", "C. 443", "D. 8080"]),
        ("5. Which SQL clause is used to retrieve unique records from a database table?",
         ["A. DISTINCT", "B. UNIQUE", "C. GROUP BY", "D. DIFFERENT"]),
        ("6. In Python, which of the following built-in collection types is immutable?",
         ["A. List", "B. Dictionary", "C. Tuple", "D. Set"]),
        ("7. Which cryptographic algorithm is an example of asymmetric key cryptography?",
         ["A. AES", "B. RSA", "C. DES", "D. Blowfish"]),
        ("8. What is the average time complexity of searching an element using Binary Search?",
         ["A. O(1)", "B. O(log n)", "C. O(n)", "D. O(n log n)"]),
        ("9. In web development, what does CSS stand for?",
         ["A. Cascading Style Sheets", "B. Creative System Sheets", "C. Computer Styled Syntax", "D. Central Styling Server"]),
        ("10. Which type of RAM requires periodic electrical refreshing to retain stored data?",
         ["A. Dynamic RAM (DRAM)", "B. Static RAM (SRAM)", "C. ROM", "D. Flash EEPROM"]),

        # Section B: Software Engineering & Systems (11-20)
        ("11. What condition is essential in a recursive function to prevent an infinite call stack?",
         ["A. Loop counter", "B. Base case", "C. Global variable", "D. Exception handler"]),
        ("12. Which Unix/Linux terminal command is used to display the current working directory path?",
         ["A. pwd", "B. cwd", "C. dir", "D. path"]),
        ("13. In Git version control, which command saves staged changes into the local repository history?",
         ["A. git push", "B. git stage", "C. git commit", "D. git record"]),
        ("14. What is the standard default port number used by the HTTPS protocol?",
         ["A. 22", "B. 53", "C. 80", "D. 443"]),
        ("15. Which protocol resolves human-readable domain names into numerical IP addresses?",
         ["A. DHCP", "B. DNS", "C. ARP", "D. ICMP"]),
        ("16. Which machine learning paradigm learns patterns strictly from labeled training examples?",
         ["A. Supervised Learning", "B. Unsupervised Learning", "C. Reinforcement Learning", "D. Self-Supervised Learning"]),
        ("17. What cloud service delivery model provides virtualized hardware, storage, and networking on demand?",
         ["A. SaaS", "B. IaaS", "C. PaaS", "D. FaaS"]),
        ("18. Which logic gate produces an output of 0 only when all its inputs are 1?",
         ["A. AND", "B. OR", "C. NAND", "D. XOR"]),
        ("19. What is the exact value of 2 raised to the power of 10 (2^10)?",
         ["A. 512", "B. 1000", "C. 1024", "D. 2048"]),
        ("20. What is the chemical formula for water?",
         ["A. CO2", "B. H2O", "C. NaCl", "D. CH4"]),

        # Section C: General Science & Modern Tech (21-30)
        ("21. What is the approximate speed of light in a vacuum?",
         ["A. 150,000 km/s", "B. 300,000 km/s", "C. 450,000 km/s", "D. 600,000 km/s"]),
        ("22. Which greenhouse gas is released in significant quantities through human fossil fuel combustion?",
         ["A. Argon", "B. Helium", "C. Carbon Dioxide", "D. Neon"]),
        ("23. Which phase of the Software Development Life Cycle (SDLC) directly follows Requirement Analysis?",
         ["A. Deployment", "B. System Design", "C. Maintenance", "D. User Testing"]),
        ("24. In data analysis with Python, which library provides high-performance DataFrame structures?",
         ["A. Pandas", "B. Matplotlib", "C. Scikit-learn", "D. PyTorch"]),
        ("25. Which software tool is primarily used for creating and running lightweight containerized applications?",
         ["A. VirtualBox", "B. Docker", "C. VMware ESXi", "D. Wine"]),
        ("26. In RESTful API design, which HTTP method is considered both idempotent and safe for reading resources?",
         ["A. POST", "B. PATCH", "C. GET", "D. DELETE"]),
        ("27. What typically causes a Stack Overflow runtime error in executing programs?",
         ["A. Deep or infinite recursion", "B. Heap memory fragmentation", "C. Null pointer dereference", "D. Disk space exhaustion"]),
        ("28. What is the first compilation phase that breaks source code into tokens?",
         ["A. Syntax Analysis", "B. Lexical Analysis", "C. Semantic Analysis", "D. Code Optimization"]),
        ("29. In modern microprocessors, what unit is most commonly used to measure CPU clock frequency?",
         ["A. Megabytes (MB)", "B. Gigahertz (GHz)", "C. Terabytes (TB)", "D. Milliseconds (ms)"]),
        ("30. What type of cyber attack tricks individuals into disclosing confidential credentials via fraudulent emails?",
         ["A. Phishing", "B. SQL Injection", "C. Denial of Service (DoS)", "D. Buffer Overflow"]),
    ]

    # Render questions with section headers and clean layout
    for idx, (q_text, options) in enumerate(questions, 1):
        if idx == 1:
            story.append(Paragraph("Section A: Computer Science & Architecture", section_style))
        elif idx == 11:
            story.append(Spacer(1, 10))
            story.append(PageBreak())
            story.append(Paragraph("Section B: Software Engineering & Systems", section_style))
        elif idx == 21:
            story.append(Spacer(1, 10))
            story.append(PageBreak())
            story.append(Paragraph("Section C: General Science & Modern Technologies", section_style))

        story.append(Paragraph(q_text, q_style))
        for opt in options:
            story.append(Paragraph(opt, opt_style))
        story.append(Spacer(1, 4))

    # Add Answer Key on final page
    story.append(PageBreak())
    story.append(Paragraph("Official Answer Key", title_style))
    story.append(Paragraph("Section-by-section correct option reference for automated scoring validation.", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color="#1a365d", spaceAfter=15))

    answer_keys = [
        "1. B", "2. A", "3. B", "4. B", "5. A", "6. C", "7. B", "8. B", "9. A", "10. A",
        "11. B", "12. A", "13. C", "14. D", "15. B", "16. A", "17. B", "18. C", "19. C", "20. B",
        "21. B", "22. C", "23. B", "24. A", "25. B", "26. C", "27. A", "28. B", "29. B", "30. A"
    ]

    # Render answers in 3 neat columns of 10
    col1 = "<br/>".join(answer_keys[:10])
    col2 = "<br/>".join(answer_keys[10:20])
    col3 = "<br/>".join(answer_keys[20:])

    from reportlab.platypus import Table, TableStyle
    from reportlab.lib import colors

    table_data = [
        [
            Paragraph("<b>Questions 1 - 10</b>", section_style),
            Paragraph("<b>Questions 11 - 20</b>", section_style),
            Paragraph("<b>Questions 21 - 30</b>", section_style),
        ],
        [
            Paragraph(col1, key_style),
            Paragraph(col2, key_style),
            Paragraph(col3, key_style),
        ]
    ]

    t = Table(table_data, colWidths=[170, 170, 170])
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f4f8')),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor('#1a365d')),
    ]))
    story.append(t)

    doc.build(story)
    print(f"Successfully generated 30-question PDF at: {output_path}")


if __name__ == "__main__":
    out_dir = Path(__file__).resolve().parent.parent / "sample_documents"
    out_dir.mkdir(parents=True, exist_ok=True)
    generate_30_questions_pdf(out_dir / "30_questions_exam_paper.pdf")
