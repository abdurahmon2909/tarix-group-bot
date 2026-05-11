from aiogram.fsm.state import (
    StatesGroup,
    State,
)


class RegisterStates(
    StatesGroup
):

    waiting_for_fullname = State()