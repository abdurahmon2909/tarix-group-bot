from __future__ import annotations

import os

from datetime import (
    datetime,
    timezone,
)

from zoneinfo import ZoneInfo

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.enums import (
    TA_CENTER,
    TA_LEFT,
)

from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle,
)

from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    Image,
)

tashkent_tz = ZoneInfo(
    "Asia/Tashkent"
)


def _safe(val) -> str:

    return (
        str(val or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def classify_activity_by_percentile(
    users: list,
) -> list:

    if not users:
        return users

    sorted_users = sorted(
        users,
        key=lambda x: x["msg_count"],
        reverse=True,
    )

    total_users = len(
        sorted_users
    )

    faol_limit = max(
        1,
        int(total_users * 0.1)
    )

    yaxshi_limit = (
        faol_limit
        + max(
            1,
            int(total_users * 0.2)
        )
    )

    ortacha_limit = (
        yaxshi_limit
        + max(
            1,
            int(total_users * 0.3)
        )
    )

    for idx, user in enumerate(
        sorted_users
    ):

        if idx < faol_limit:

            user["category"] = (
                "Faol"
            )

        elif idx < yaxshi_limit:

            user["category"] = (
                "Yaxshi"
            )

        elif idx < ortacha_limit:

            user["category"] = (
                "O'rtacha"
            )

        else:

            user["category"] = (
                "Qoniqarli"
            )

    return sorted_users


def get_category_color(
    category: str,
):

    if category == "Faol":

        return colors.HexColor(
            "#d9f2e3"
        )

    elif category == "Yaxshi":

        return colors.HexColor(
            "#dbeafe"
        )

    elif category == "O'rtacha":

        return colors.HexColor(
            "#fff4cc"
        )

    return colors.HexColor(
        "#f3e5dc"
    )


def build_pdf_report(
    stats: dict,
    period_label: str,
    file_path: str,
):

    os.makedirs(
        os.path.dirname(file_path),
        exist_ok=True,
    )

    doc = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        leftMargin=12 * mm,
        rightMargin=12 * mm,
        topMargin=10 * mm,
        bottomMargin=10 * mm,
    )

    styles = getSampleStyleSheet()

    style_link = ParagraphStyle(
        "Link",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
        fontSize=12,
        textColor=colors.HexColor(
            "#0f7fa8"
        ),
        leading=16,
        spaceAfter=4,
    )

    style_ad = ParagraphStyle(
        "Ad",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
        fontSize=11,
        textColor=colors.HexColor(
            "#c62828"
        ),
        leading=15,
        spaceAfter=6,
    )

    style_title = ParagraphStyle(
        "TitleCenter",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
        fontSize=18,
        textColor=colors.HexColor(
            "#123b5d"
        ),
        leading=22,
        spaceAfter=8,
    )

    style_group_title = ParagraphStyle(
        "GroupTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
        fontSize=16,
        textColor=colors.HexColor(
            "#1a5490"
        ),
        leading=20,
        spaceAfter=6,
    )

    style_info = ParagraphStyle(
        "Info",
        parent=styles["Normal"],
        alignment=TA_LEFT,
        fontName="Helvetica",
        fontSize=10,
        textColor=colors.black,
        leading=14,
    )

    style_box_title = ParagraphStyle(
        "BoxTitle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
        fontSize=11,
        textColor=colors.white,
        leading=14,
    )

    style_box_value = ParagraphStyle(
        "BoxValue",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
        fontSize=14,
        textColor=colors.white,
        leading=18,
    )

    story = []

    possible_logo_paths = [
        "assets/logo.png",
        "assets/logo.jpg",
        "assets/logo.jpeg",
        "assets/banner.png",
        "assets/banner.jpg",
        "assets/banner.jpeg",
    ]

    logo_path = next(
        (
            p
            for p in possible_logo_paths
            if os.path.exists(p)
        ),
        None,
    )

    if logo_path:

        page_width = A4[0]

        usable_width = (
            page_width
            - doc.leftMargin
            - doc.rightMargin
        )

        img = Image(
            logo_path,
            width=usable_width,
            height=95 * mm,
        )

        img.preserveAspectRatio = True

        img.hAlign = "CENTER"

        story.append(img)

        story.append(
            Spacer(1, 6)
        )

    story.append(
        Paragraph(
            "https://t.me/Tarixaudiokurs",
            style_link,
        )
    )

    story.append(
        Paragraph(
            (
                "Natija kerak bo‘lsa, "
                "bugunoq kursimizga qo‘shiling! "
                "Murojaat uchun: "
                "@Fazliddin_Burxonov"
            ),
            style_ad,
        )
    )

    group_name = stats.get(
        "group_name",
        "Guruh",
    )

    story.append(
        Paragraph(
            f"🏢 {group_name} guruhi",
            style_group_title,
        )
    )

    story.append(
        Paragraph(
            (
                f"So‘nggi "
                f"{period_label} "
                f"bo‘yicha faollik natijalari"
            ),
            style_title,
        )
    )

    start_text = (
        stats["start_dt"]
        .replace(tzinfo=timezone.utc)
        .astimezone(
            tashkent_tz
        )
        .strftime(
            "%Y-%m-%d %H:%M:%S UTC+5"
        )
    )

    end_text = (
        stats["end_dt"]
        .replace(tzinfo=timezone.utc)
        .astimezone(
            tashkent_tz
        )
        .strftime(
            "%Y-%m-%d %H:%M:%S UTC+5"
        )
    )

    total_messages = stats[
        "total_messages"
    ]

    users = classify_activity_by_percentile(
        stats["users"]
    )

    story.append(
        Paragraph(
            (
                "Boshlanish vaqti: "
                f"<b>{start_text}</b>"
            ),
            style_info,
        )
    )

    story.append(
        Paragraph(
            (
                "Tugash vaqti: "
                f"<b>{end_text}</b>"
            ),
            style_info,
        )
    )

    story.append(
        Paragraph(
            (
                "Jami xabarlar soni: "
                f"<b>{total_messages}</b>"
            ),
            style_info,
        )
    )

    story.append(
        Paragraph(
            (
                "Faol foydalanuvchilar soni: "
                f"<b>{len(users)}</b>"
            ),
            style_info,
        )
    )

    story.append(
        Spacer(1, 8)
    )

    # =========================
    # CATEGORY SUMMARY
    # =========================

    category_counts = {
        "Faol": 0,
        "Yaxshi": 0,
        "O'rtacha": 0,
        "Qoniqarli": 0,
    }

    for u in users:

        cat = u.get(
            "category",
            "Qoniqarli",
        )

        if cat in category_counts:
            category_counts[cat] += 1

    total_users = len(users)

    faol_percent = (
        category_counts["Faol"]
        / total_users
        * 100
    ) if total_users else 0

    yaxshi_percent = (
        category_counts["Yaxshi"]
        / total_users
        * 100
    ) if total_users else 0

    ortacha_percent = (
        category_counts["O'rtacha"]
        / total_users
        * 100
    ) if total_users else 0

    qoniqarli_percent = (
        category_counts["Qoniqarli"]
        / total_users
        * 100
    ) if total_users else 0

    summary_data = [
        [
            Paragraph(
                "Faol",
                style_box_title,
            ),
            Paragraph(
                "Yaxshi",
                style_box_title,
            ),
            Paragraph(
                "O'rtacha",
                style_box_title,
            ),
            Paragraph(
                "Qoniqarli",
                style_box_title,
            ),
        ],
        [
            Paragraph(
                (
                    f"{category_counts['Faol']} "
                    f"({faol_percent:.1f}%)"
                ),
                style_box_value,
            ),

            Paragraph(
                (
                    f"{category_counts['Yaxshi']} "
                    f"({yaxshi_percent:.1f}%)"
                ),
                style_box_value,
            ),

            Paragraph(
                (
                        str(
                            category_counts["O'rtacha"]
                        )
                        + f" ({ortacha_percent:.1f}%)"
                ),
                style_box_value,
            ),

            Paragraph(
                (
                    f"{category_counts['Qoniqarli']} "
                    f"({qoniqarli_percent:.1f}%)"
                ),
                style_box_value,
            ),
        ],
    ]

    summary_table = Table(
        summary_data,
        colWidths=[
            43 * mm,
            43 * mm,
            43 * mm,
            43 * mm,
        ],
    )

    summary_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (0, 1),
                colors.HexColor(
                    "#0b8f55"
                ),
            ),
            (
                "BACKGROUND",
                (1, 0),
                (1, 1),
                colors.HexColor(
                    "#1e88e5"
                ),
            ),
            (
                "BACKGROUND",
                (2, 0),
                (2, 1),
                colors.HexColor(
                    "#f9a825"
                ),
            ),
            (
                "BACKGROUND",
                (3, 0),
                (3, 1),
                colors.HexColor(
                    "#8d6e63"
                ),
            ),
            (
                "BOX",
                (0, 0),
                (-1, -1),
                0.8,
                colors.white,
            ),
            (
                "INNERGRID",
                (0, 0),
                (-1, -1),
                0.8,
                colors.white,
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE",
            ),
            (
                "ALIGN",
                (0, 0),
                (-1, -1),
                "CENTER",
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                8,
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                8,
            ),
        ])
    )

    story.append(
        summary_table
    )

    story.append(
        Spacer(1, 10)
    )

    # =========================
    # TOP 3 USERS
    # =========================

    if users:

        top3 = users[:3]

        top3_rows = [[
            Paragraph(
                "<b>TOP</b>",
                styles["Normal"],
            ),
            Paragraph(
                "<b>Ism</b>",
                styles["Normal"],
            ),
            Paragraph(
                "<b>Xabarlar</b>",
                styles["Normal"],
            ),
            Paragraph(
                "<b>Ulush %</b>",
                styles["Normal"],
            ),
            Paragraph(
                "<b>Toifa</b>",
                styles["Normal"],
            ),
        ]]

        medals = [
            "🥇 1",
            "🥈 2",
            "🥉 3",
        ]

        for i, u in enumerate(top3):

            top3_rows.append([
                medals[i],
                _safe(
                    u["full_name"]
                ),
                str(
                    u["msg_count"]
                ),
                str(
                    u["share_percent"]
                ),
                _safe(
                    u["category"]
                ),
            ])

        top3_table = Table(
            top3_rows,
            colWidths=[
                18 * mm,
                90 * mm,
                28 * mm,
                28 * mm,
                32 * mm,
            ],
        )

        top3_style = [
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor(
                    "#123b5d"
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
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                9,
            ),
        ]

        for row_idx, u in enumerate(
            top3,
            start=1,
        ):

            bg = get_category_color(
                u["category"]
            )

            top3_style.append(
                (
                    "BACKGROUND",
                    (0, row_idx),
                    (-1, row_idx),
                    bg,
                )
            )

        top3_table.setStyle(
            TableStyle(
                top3_style
            )
        )

        story.append(
            Paragraph(
                "<b>Eng faol 3 ishtirokchi</b>",
                styles["Heading3"],
            )
        )

        story.append(
            top3_table
        )

        story.append(
            Spacer(1, 10)
        )

    # =========================
    # TABLE TITLE
    # =========================

    story.append(
        Paragraph(
            "<b>Batafsil jadval</b>",
            styles["Heading3"],
        )
    )

    story.append(
        Spacer(1, 5)
    )

    data = [[
        "No",
        "Ism",
        "Xabarlar",
        "Ulush %",
        "Toifa",
    ]]

    for idx, user in enumerate(
        users,
        start=1,
    ):

        data.append([
            str(idx),
            _safe(
                user["full_name"]
            ),
            str(
                user["msg_count"]
            ),
            str(
                user["share_percent"]
            ),
            _safe(
                user["category"]
            ),
        ])

    table = Table(
        data,
        repeatRows=1,
        colWidths=[
            12 * mm,
            90 * mm,
            28 * mm,
            28 * mm,
            32 * mm,
        ],
    )

    table_style = [
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
            "Helvetica-Bold",
        ),
        (
            "GRID",
            (0, 0),
            (-1, -1),
            0.4,
            colors.grey,
        ),
        (
            "FONTSIZE",
            (0, 0),
            (-1, -1),
            8.8,
        ),
    ]

    for row_idx, user in enumerate(
        users,
        start=1,
    ):

        bg = get_category_color(
            user["category"]
        )

        table_style.append(
            (
                "BACKGROUND",
                (4, row_idx),
                (4, row_idx),
                bg,
            )
        )

    table.setStyle(
        TableStyle(
            table_style
        )
    )

    story.append(table)

    story.append(
        Spacer(1, 10)
    )

    story.append(
        Paragraph(
            (
                "PDF yaratilgan vaqt: "
                f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}"
            ),
            styles["Italic"],
        )
    )

    doc.build(story)
