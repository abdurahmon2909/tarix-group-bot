from aiogram.fsm.state import (
    StatesGroup,
    State,
)


class CreateTestStates(
    StatesGroup
):

    waiting_for_folder_name = State()

    waiting_for_test_title = State()

    waiting_for_pdf = State()

    waiting_for_answer_key = State()

    waiting_for_certificate_template = State()

class SolveTestStates(
    StatesGroup
):

    waiting_for_answers = State()

class CertificateTemplateStates(
    StatesGroup
):

    waiting_for_template_name = State()

    waiting_for_background = State()

    waiting_for_signature = State()