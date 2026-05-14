from __future__ import annotations

import re


ANSWER_PATTERN = re.compile(
    r"(\d+)\s*[-:=]?\s*([A-Ea-e])"
)


def parse_answer_key(
    text: str,
) -> dict[str, str]:

    matches = ANSWER_PATTERN.findall(
        text
    )

    result = {}

    for number, answer in matches:

        result[number] = (
            answer.lower()
        )

    return result