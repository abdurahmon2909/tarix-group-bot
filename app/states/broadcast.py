from aiogram.fsm.state import (
    StatesGroup,
    State,
)


class BroadcastStates(
    StatesGroup
):

    selecting_groups = State()

    waiting_for_post = State()