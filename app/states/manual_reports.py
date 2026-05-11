from aiogram.fsm.state import (
    StatesGroup,
    State,
)


class ManualReportStates(
    StatesGroup
):

    waiting_for_start_date = State()

    waiting_for_end_date = State()