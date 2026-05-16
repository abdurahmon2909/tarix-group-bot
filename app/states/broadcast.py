from aiogram.fsm.state import (
    StatesGroup,
    State,
)


class BroadcastStates(
    StatesGroup
):

    # GROUPS

    selecting_groups = State()

    waiting_for_post = State()

    # USERS

    waiting_for_user_broadcast = (
        State()
    )
