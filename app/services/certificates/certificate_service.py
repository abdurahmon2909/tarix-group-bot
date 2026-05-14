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

    # =====================
    # FONTS
    # =====================

    try:

        title_font = ImageFont.truetype(
            "DejaVuSans-Bold.ttf",
            70,
        )

        text_font = ImageFont.truetype(
            "DejaVuSans.ttf",
            32,
        )

        small_font = ImageFont.truetype(
            "DejaVuSans.ttf",
            24,
        )

    except Exception:

        title_font = ImageFont.load_default()

        text_font = ImageFont.load_default()

        small_font = ImageFont.load_default()

    # =====================
    # FULLNAME
    # =====================

    draw.text(
        (420, 420),
        fullname,
        fill="#0A1D45",
        font=title_font,
    )

    # =====================
    # TEST NAME
    # =====================

    draw.text(
        (350, 680),
        test_name,
        fill="#111111",
        font=text_font,
    )

    # =====================
    # SCORE
    # =====================

    draw.text(
        (760, 680),
        f"{score_percent}%",
        fill="#B8860B",
        font=text_font,
    )

    # =====================
    # CORRECT ANSWERS
    # =====================

    draw.text(
        (1040, 680),
        (
            f"{correct_answers}"
            f"/{question_count}"
        ),
        fill="#111111",
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
        (1320, 680),
        f"{minutes}:{seconds:02}",
        fill="#111111",
        font=text_font,
    )

    # =====================
    # DATE
    # =====================

    draw.text(
        (1290, 120),
        datetime.now().strftime(
            "%d.%m.%Y"
        ),
        fill="#111111",
        font=small_font,
    )

    # =====================
    # CERTIFICATE ID
    # =====================

    draw.text(
        (1260, 170),
        certificate_id,
        fill="#111111",
        font=small_font,
    )

    # =====================
    # QR CODE
    # =====================

    qr = qrcode.make(
        (
            "https://t.me/"
            "your_bot_username"
        )
    )

    qr = qr.resize(
        (180, 180)
    )

    image.paste(
        qr,
        (230, 840),
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