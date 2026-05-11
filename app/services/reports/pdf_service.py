from __future__ import annotations

from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
)

from reportlab.lib import colors

from reportlab.lib.pagesizes import A4

from reportlab.lib.styles import (
    getSampleStyleSheet,
)

from reportlab.lib.units import mm

from reportlab.pdfbase import pdfmetrics

from reportlab.pdfbase.ttfonts import (
    TTFont,
)

from reportlab.platypus.flowables import (
    Image,
)

from reportlab.lib.enums import (
    TA_CENTER,
)

from reportlab.lib.styles import (
    ParagraphStyle,
)

from datetime import datetime


# =========================
# FONT
# =========================

pdfmetrics.registerFont(
    TTFont(
        "DejaVu",
        "DejaVuSans.ttf",
    )
)

pdfmetrics.registerFont(
    TTFont(
        "DejaVu-Bold",
        "DejaVuSans.ttf",
    )
)


# =========================
# HELPERS
# =========================

def safe_text(
    text: str | None,
) -> str:

    if not text:
        return "Ism kiritilmagan"

    return (
        text
        .replace("■", "")
        .replace("\x00", "")
        .strip()
    )


# =========================
# PDF
# =========================

def build_pdf_report(
    stats: dict,
    period_label: str,
    filename: str,
):

    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        topMargin=15 * mm,
        leftMargin=10 * mm,
        rightMargin=10 * mm,
        bottomMargin=10 * mm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Heading1"],
        fontName="DejaVu-Bold",
        fontSize=20,
        leading=24,
        alignment=TA_CENTER,
        textColor=colors.HexColor(
            "#0b3f75"
        ),
    )

    normal_style = ParagraphStyle(
        "NormalStyle",
        parent=styles["BodyText"],
        fontName="DejaVu",
        fontSize=11,
        leading=14,
    )

    elements = []

    # =========================
    # TITLE
    # =========================

    title = Paragraph(
        f"{stats['group_name']}<br/>"
        f"Faollik Hisoboti",
        title_style,
    )

    elements.append(title)

    elements.append(
        Spacer(1, 8)
    )

    # =========================
    # PERIOD
    # =========================

    period_text = Paragraph(
        f"<b>Davr:</b> {period_label}",
        normal_style,
    )

    elements.append(period_text)

    elements.append(
        Spacer(1, 6)
    )

    # =========================
    # TOTAL
    # =========================

    total_text = Paragraph(
        f"<b>Jami xabarlar:</b> "
        f"{stats['total_messages']}",
        normal_style,
    )

    elements.append(total_text)

    elements.append(
        Spacer(1, 12)
    )

    # =========================
    # TOP 3
    # =========================

    top3 = stats["users"][:3]

    if top3:

        top_title = Paragraph(
            "Eng faol 3 ishtirokchi",
            ParagraphStyle(
                "TopTitle",
                parent=styles["Heading2"],
                fontName="DejaVu-Bold",
                fontSize=15,
                textColor=colors.black,
            ),
        )

        elements.append(top_title)

        elements.append(
            Spacer(1, 6)
        )

        top_rows = [
            [
                "TOP",
                "Ism",
                "Xabarlar",
                "Ulush %",
                "Toifa",
            ]
        ]

        for idx, user in enumerate(
            top3,
            start=1,
        ):

            top_rows.append([
                f"■ {idx}",
                safe_text(
                    user["full_name"]
                ),
                str(
                    user["msg_count"]
                ),
                str(
                    user["share_percent"]
                ),
                safe_text(
                    user["category"]
                ),
            ])

        top_table = Table(
            top_rows,
            colWidths=[
                20 * mm,
                90 * mm,
                30 * mm,
                30 * mm,
                35 * mm,
            ],
        )

        top_table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor(
                        "#1f4e78"
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
                    "DejaVu-Bold",
                ),
                (
                    "FONTNAME",
                    (0, 1),
                    (-1, -1),
                    "DejaVu",
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
            ])
        )

        elements.append(top_table)

        elements.append(
            Spacer(1, 15)
        )

    # =========================
    # FULL TABLE
    # =========================

    table_title = Paragraph(
        "Batafsil jadval",
        ParagraphStyle(
            "TableTitle",
            parent=styles["Heading2"],
            fontName="DejaVu-Bold",
            fontSize=14,
        ),
    )

    elements.append(table_title)

    elements.append(
        Spacer(1, 6)
    )

    rows = [
        [
            "No",
            "Ism",
            "Xabarlar",
            "Ulush %",
            "Toifa",
        ]
    ]

    for idx, user in enumerate(
        stats["users"],
        start=1,
    ):

        rows.append([
            str(idx),
            safe_text(
                user["full_name"]
            ),
            str(
                user["msg_count"]
            ),
            str(
                user["share_percent"]
            ),
            safe_text(
                user["category"]
            ),
        ])

    table = Table(
        rows,
        colWidths=[
            15 * mm,
            95 * mm,
            30 * mm,
            30 * mm,
            35 * mm,
        ],
    )

    style = [
        (
            "BACKGROUND",
            (0, 0),
            (-1, 0),
            colors.HexColor(
                "#1f4e78"
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
            "DejaVu-Bold",
        ),
        (
            "FONTNAME",
            (0, 1),
            (-1, -1),
            "DejaVu",
        ),
        (
            "GRID",
            (0, 0),
            (-1, -1),
            0.5,
            colors.grey,
        ),
        (
            "VALIGN",
            (0, 0),
            (-1, -1),
            "MIDDLE",
        ),
    ]

    for row_idx, user in enumerate(
        stats["users"],
        start=1,
    ):

        category = user["category"]

        bg = colors.white

        if category == "Faol":

            bg = colors.HexColor(
                "#d9ead3"
            )

        elif category == "Yaxshi":

            bg = colors.HexColor(
                "#d0e0ff"
            )

        elif category == "O'rtacha":

            bg = colors.HexColor(
                "#fff2cc"
            )

        style.append((
            "BACKGROUND",
            (4, row_idx),
            (4, row_idx),
            bg,
        ))

    table.setStyle(
        TableStyle(style)
    )

    elements.append(table)

    elements.append(
        Spacer(1, 10)
    )

    # =========================
    # FOOTER
    # =========================

    footer = Paragraph(
        f"Hisobot yaratilgan vaqt: "
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        ParagraphStyle(
            "Footer",
            parent=styles["BodyText"],
            fontName="DejaVu",
            fontSize=9,
            textColor=colors.grey,
        ),
    )

    elements.append(footer)

    # =========================
    # BUILD
    # =========================

    doc.build(elements)