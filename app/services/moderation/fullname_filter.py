from __future__ import annotations

import hashlib


# =========================
# CACHE
# =========================

FULLNAME_CACHE: dict[
    int,
    str,
] = {}


# =========================
# STRICT EMOJIS
# =========================

NSFW_EMOJIS = {
    "🍑",
    "🍆",
    "👅",
    "🔞",
    "🥵",
    "🍌",
    "💦",
    "😈",
}

# =========================
# STRICT KEYWORDS
# =========================

NSFW_KEYWORDS = {
    "porn",
    "sex",
    "nsfw",
    "onlyfans",
    "escort",
    "18+",
    "xnxx",
    "xvideos",
    "hentai",
}


# =========================
# HASH
# =========================

def build_fullname_hash(
    text: str,
) -> str:

    return hashlib.md5(
        text.lower().strip().encode()
    ).hexdigest()


# =========================
# CHECK CACHE
# =========================

def is_fullname_cached(
    user_id: int,
    fullname: str,
) -> bool:

    fullname_hash = (
        build_fullname_hash(
            fullname
        )
    )

    cached = FULLNAME_CACHE.get(
        user_id
    )

    return cached == fullname_hash


# =========================
# UPDATE CACHE
# =========================

def update_fullname_cache(
    user_id: int,
    fullname: str,
):

    FULLNAME_CACHE[user_id] = (
        build_fullname_hash(
            fullname
        )
    )


# =========================
# DETECT FULLNAME
# =========================

def detect_nsfw_fullname(
    fullname: str,
) -> str | None:

    lowered = (
        fullname.lower()
    )

    for emoji in NSFW_EMOJIS:

        if emoji in fullname:

            return (
                f"TAQIQLANGAN EMOJI: "
                f"{emoji}"
            )

    for keyword in NSFW_KEYWORDS:

        if keyword in lowered:

            return (
                f"TAQIQLANGAN SO'Z: "
                f"{keyword.upper()}"
            )

    return None


# =========================
# DETECT MESSAGE TEXT
# =========================

def detect_nsfw_text(
    text: str,
) -> str | None:

    lowered = (
        text.lower()
    )

    for emoji in NSFW_EMOJIS:

        if emoji in text:

            return (
                f"TAQIQLANGAN EMOJI: "
                f"{emoji}"
            )

    for keyword in NSFW_KEYWORDS:

        if keyword in lowered:

            return (
                f"TAQIQLANGAN SO'Z: "
                f"{keyword.upper()}"
            )

    return None