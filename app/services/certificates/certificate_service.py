from __future__ import annotations

from pathlib import Path

from datetime import datetime

from PIL import (
    Image,
    ImageDraw,
    ImageFont,
)

import qrcode


BASE_DIR = Path(
    "assets/certificates"
)

TEMPLATE_PATH = (
    BASE_DIR / "template_1.png"
)

OUTPUT_DIR = (
    BASE_DIR / "generated"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


def generate_certificate(
    fullname: str,
    test_name: str,
    score_percent: float,
    correct_answers: int,
    question_count: int,
    duration_seconds: int,
    certificate_id: str,
):

    image = Image.open(
        TEMPLATE_PATH
    ).convert("RGB")

    draw = ImageDraw.Draw(
        image
    )

    width, height = image.size

    # =====================
    # FONTS
    # =====================

    FONT_PATH = (
            BASE_DIR / "NotoSans-Regular.ttf"
    )

    title_font = ImageFont.truetype(
        str(FONT_PATH),
        64,
    )

    subtitle_font = ImageFont.truetype(
        str(FONT_PATH),
        32,
    )

    text_font = ImageFont.truetype(
        str(FONT_PATH),
        28,
    )

    small_font = ImageFont.truetype(
        str(FONT_PATH),
        28,
    )

    # =====================
    # DATE
    # =====================

    draw.text(
        (1320, 118),
        datetime.now().strftime(
            "%d.%m.%Y"
        ),
        fill="#0A1D45",
        font=small_font,
    )

    # =====================
    # CERTIFICATE ID
    # =====================

    draw.text(
        (1290, 174),
        certificate_id,
        fill="#0A1D45",
        font=small_font,
    )

    # =====================
    # FULLNAME
    # =====================

    bbox = draw.textbbox(
        (0, 0),
        fullname,
        font=title_font,
    )

    text_width = (
        bbox[2] - bbox[0]
    )

    x = (
        width - text_width
    ) // 2

    draw.text(
        (x, 430),
        fullname,
        fill="#091C43",
        font=title_font,
    )

    # =====================
    # TEST NAME
    # =====================

    draw.text(
        (315, 660),
        test_name[:28],
        fill="#091C43",
        font=small_font,
    )

    # =====================
    # SCORE
    # =====================

    draw.text(
        (645, 660),
        f"{score_percent}%",
        fill="#B8860B",
        font=subtitle_font,
    )

    # =====================
    # CORRECT ANSWERS
    # =====================

    draw.text(
        (930, 660),
        (
            f"{correct_answers}"
            f"/{question_count}"
        ),
        fill="#091C43",
        font=text_font,
    )

    # =====================
    # TIME
    # =====================

    minutes = (
        duration_seconds // 60
    )

    seconds = (
        duration_seconds % 60
    )

    draw.text(
        (1220, 660),
        f"{minutes}:{seconds:02}",
        fill="#B8860B",
        font=text_font,
    )

    # =====================
    # QR CODE
    # =====================

    qr = qrcode.make(
        certificate_id
    )

    qr = qr.resize(
        (160, 160)
    )

    image.paste(
        qr,
        (205, 765),
    )

    # =====================
    # SAVE
    # =====================

    output_path = (
        OUTPUT_DIR
        / f"{certificate_id}.png"
    )

    image.save(
        output_path
    )

    return output_path