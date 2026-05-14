from __future__ import annotations

from pathlib import Path

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from reportlab.lib import colors

from reportlab.lib.styles import (
    getSampleStyleSheet,
)

from reportlab.lib.pagesizes import (
    A4,
)

from reportlab.pdfbase import pdfmetrics

from reportlab.pdfbase.ttfonts import (
    TTFont,
)

from reportlab.platypus.flowables import (
    PageBreak,
)

from reportlab.pdfbase.pdfmetrics import (
    stringWidth,
)


BASE_DIR = Path(
    "assets/reports"
)

BASE_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


def build_test_results_pdf(
    test_title: str,
    results: list,
):

    output_path = (
        BASE_DIR
        / "test_results.pdf"
    )

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
    )

    styles = getSampleStyleSheet()

    story = []

    # =====================
    # TITLE
    # =====================

    story.append(
        Paragraph(
            (
                f"<b>Test natijalari</b><br/>"
                f"{test_title}"
            ),
            styles["Title"],
        )
    )

    story.append(
        Spacer(1, 20)
    )

    # =====================
    # TABLE
    # =====================

    data = [[
        "№",
        "Ism",
        "%",
        "To‘g‘ri",
        "Noto‘g‘ri",
        "Urinish",
        "Sertifikat",
    ]]

    for idx, attempt in enumerate(
        results,
        start=1,
    ):

        fullname = (
            getattr(
                attempt.user,
                "full_name",
                "Unknown",
            )
            or "Unknown"
        )

        certificate = (
            "✅"
            if (
                attempt.certificate_generated
            )
            else "❌"
        )

        data.append([
            str(idx),
            fullname,
            f"{attempt.score_percent}%",
            str(
                attempt.correct_answers
            ),
            str(
                attempt.wrong_answers
            ),
            str(
                attempt.attempt_number
            ),
            certificate,
        ])

    table = Table(
        data,
        repeatRows=1,
    )

    table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.darkblue,
            ),

            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white,
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                1,
                colors.black,
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold",
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, 0),
                10,
            ),
        ])
    )

    story.append(
        table
    )

    doc.build(
        story
    )

    return output_path