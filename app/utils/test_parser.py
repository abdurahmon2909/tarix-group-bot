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

def compare_answers(
    correct_answers: dict,
    user_answers: dict,
):

    correct_count = 0

    wrong_count = 0

    for question, answer in (
        correct_answers.items()
    ):

        user_answer = user_answers.get(
            question
        )

        if user_answer == answer:

            correct_count += 1

        else:

            wrong_count += 1

    total = len(correct_answers)

    percent = round(
        (
            correct_count / total
        ) * 100,
        2,
    )

    return {
        "correct": correct_count,
        "wrong": wrong_count,
        "percent": percent,
    }