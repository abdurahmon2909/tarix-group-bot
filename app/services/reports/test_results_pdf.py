from __future__ import annotations

from pathlib import Path
from statistics import mean

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
    landscape,
    A4,
)

from reportlab.platypus.tables import (
    Table,
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
        pagesize=landscape(A4),
        leftMargin=25,
        rightMargin=25,
        topMargin=30,
        bottomMargin=30,
    )

    styles = getSampleStyleSheet()

    story = []

    # =====================
    # ANALYTICS
    # =====================

    total_attempts = len(
        results
    )

    average_score = round(
        mean([
            r.score_percent
            for r in results
        ]),
        2,
    ) if results else 0

    certificates = len([
        r for r in results
        if r.certificate_generated
    ])

    # =====================
    # HEADER
    # =====================

    story.append(
        Paragraph(
            (
                f"<font size=22>"
                f"<b>📊 TEST NATIJALARI</b>"
                f"</font><br/><br/>"

                f"<font size=16>"
                f"<b>Test:</b> "
                f"{test_title}<br/>"

                f"<b>Urinishlar:</b> "
                f"{total_attempts}<br/>"

                f"<b>O‘rtacha natija:</b> "
                f"{average_score}%<br/>"

                f"<b>Sertifikat olganlar:</b> "
                f"{certificates}"
                f"</font>"
            ),
            styles["Normal"],
        )
    )

    story.append(
        Spacer(1, 24)
    )

    # =====================
    # TABLE
    # =====================

    data = [[
        "№",
        "F.I.SH",
        "Natija",
        "To‘g‘ri",
        "Noto‘g‘ri",
        "Urinish",
        "Vaqt",
        "Sertifikat",
    ]]

    sorted_results = sorted(
        results,
        key=lambda x: x.score_percent,
        reverse=True,
    )

    for idx, attempt in enumerate(
        sorted_results,
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

        minutes = (
            attempt.duration_seconds // 60
        )

        seconds = (
            attempt.duration_seconds % 60
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
            f"{minutes}:{seconds:02}",
            certificate,
        ])

    table = Table(
        data,
        repeatRows=1,
        colWidths=[
            35,
            180,
            80,
            70,
            80,
            70,
            80,
            80,
        ],
    )

    style = TableStyle([

        # HEADER
        (
            "BACKGROUND",
            (0, 0),
            (-1, 0),
            colors.HexColor(
                "#102542"
            ),
        ),

        (
            "TEXTCOLOR",
            (0, 0),
            (-1, 0),
            colors.white,
        ),

        (
            "FONTNAME",
            (0, 0),
            (-1, 0),
            "Helvetica-Bold",
        ),

        (
            "FONTSIZE",
            (0, 0),
            (-1, -1),
            11,
        ),

        (
            "BOTTOMPADDING",
            (0, 0),
            (-1, 0),
            12,
        ),

        (
            "TOPPADDING",
            (0, 0),
            (-1, -1),
            8,
        ),

        # GRID
        (
            "GRID",
            (0, 0),
            (-1, -1),
            1,
            colors.HexColor(
                "#D6D6D6"
            ),
        ),

        # ALIGN
        (
            "ALIGN",
            (0, 0),
            (-1, -1),
            "CENTER",
        ),

        (
            "VALIGN",
            (0, 0),
            (-1, -1),
            "MIDDLE",
        ),

        # NAME ALIGN
        (
            "ALIGN",
            (1, 1),
            (1, -1),
            "LEFT",
        ),

    ])

    # Zebra rows
    for i in range(
        1,
        len(data),
    ):

        bg = (
            colors.whitesmoke
            if i % 2 == 0
            else colors.beige
        )

        style.add(
            "BACKGROUND",
            (0, i),
            (-1, i),
            bg,
        )

    table.setStyle(
        style
    )

    story.append(
        table
    )

    doc.build(
        story
    )

    return output_path