from __future__ import annotations
import re
import asyncio
from aiogram.enums import (
    ChatMemberStatus,
)
from aiogram import (
    Router,
)
from aiogram.enums import (
    ChatType,
)
from aiogram.types import (
    Message,
)
from app.database.repositories.groups import (
    get_group_by_chat_id,
    create_group,
)
from app.database.repositories.groups import (
    create_group_if_not_exists,
    is_group_active,
)

from app.database.repositories.messages import (
    save_group_message,
)

router = Router()

LINK_REGEX = re.compile(
    r"(https?://\S+|www\.\S+|t\.me/\S+|telegram\.me/\S+)",
    re.IGNORECASE,
)
@router.message()
async def track_group_messages(
    message: Message,
):

    print("TRACKER HIT")

    # =========================
    # ONLY GROUPS
    # =========================

    if message.chat.type not in [
        ChatType.GROUP,
        ChatType.SUPERGROUP,
    ]:
        return

    # =========================
    # IGNORE BOTS
    # =========================

    if (
        not message.from_user
        or message.from_user.is_bot
    ):
        return

    print(
        "GROUP MESSAGE:",
        message.text,
    )

    # =========================
    # AUTO DELETE JOIN/LEFT
    # =========================

    try:

        if message.new_chat_members:

            is_bot_join = any(
                user.is_bot
                and user.id == message.bot.id
                for user in message.new_chat_members
            )

            if not is_bot_join:

                await message.delete()

                print(
                    "JOIN MESSAGE DELETED"
                )

                return

        if message.left_chat_member:

            is_bot_leave = (
                message.left_chat_member.is_bot
                and (
                    message.left_chat_member.id
                    == message.bot.id
                )
            )

            if not is_bot_leave:

                await message.delete()

                print(
                    "LEFT MESSAGE DELETED"
                )

                return

    except Exception as e:

        print(
            "JOIN/LEFT DELETE ERROR:",
            repr(e),
        )

    # =========================
    # LINK BLOCKER
    # =========================

    try:

        print("LINK BLOCK CHECK")

        member = await message.bot.get_chat_member(
            chat_id=message.chat.id,
            user_id=message.from_user.id,
        )

        is_admin = member.status in [
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.CREATOR,
        ]

        has_link = False

        if (
            message.text
            and LINK_REGEX.search(
                message.text
            )
        ):
            has_link = True

        if (
            message.caption
            and LINK_REGEX.search(
                message.caption
            )
        ):
            has_link = True

        if message.entities:

            for entity in message.entities:

                if entity.type in [
                    "url",
                    "text_link",
                ]:

                    has_link = True

                    break

        if message.caption_entities:

            for entity in (
                message.caption_entities
            ):

                if entity.type in [
                    "url",
                    "text_link",
                ]:

                    has_link = True

                    break

        if has_link and not is_admin:

            await message.delete()

            warning = await message.answer(
                (
                    f"{message.from_user.full_name}, "
                    f"guruhga link tashlamang!"
                )
            )

            print("LINK DELETED")

            await asyncio.sleep(5)

            try:
                await warning.delete()
            except:
                pass

            return

    except Exception as e:

        print(
            "LINK BLOCK ERROR:",
            repr(e),
        )

    # =========================
    # AUTO CREATE GROUP
    # =========================

    group = await get_group_by_chat_id(
        message.chat.id
    )

    if not group:

        print(
            "AUTO DETECT HIT"
        )

        await create_group(
            telegram_chat_id=message.chat.id,
            title=message.chat.title,
            is_active=True,
        )

        print(
            "NEW GROUP:",
            message.chat.title,
        )

        return

    # =========================
    # CHECK ACTIVE
    # =========================

    print(
        "GROUP ACTIVE:",
        group.is_active,
    )

    if not group.is_active:
        return

    # =========================
    # SAVE MESSAGE
    # =========================

    text = (
        message.text
        or message.caption
        or ""
    )

    await save_message(
        chat_id=message.chat.id,
        user_id=message.from_user.id,
        full_name=(
            message.from_user.full_name
        ),
        username=(
            message.from_user.username
        ),
        text=text,
        sent_at=message.date.replace(
            tzinfo=None
        ),
    )

    print("MESSAGE SAVED")
