from __future__ import annotations

import re
import asyncio

from aiogram import (
    Router,
)

from aiogram.enums import (
    ChatType,
    ChatMemberStatus,
)

from aiogram.types import (
    Message,
)

from app.database.repositories.groups import (
    create_group_if_not_exists,
    is_group_active,
)

from app.database.repositories.messages import (
    save_group_message,
)

router = Router()

# =========================
# LINK REGEX
# =========================

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

        # TEXT LINK

        if (
            message.text
            and LINK_REGEX.search(
                message.text
            )
        ):
            has_link = True

        # CAPTION LINK

        if (
            message.caption
            and LINK_REGEX.search(
                message.caption
            )
        ):
            has_link = True

        # ENTITIES

        if message.entities:

            for entity in message.entities:

                if entity.type in [
                    "url",
                    "text_link",
                ]:

                    has_link = True

                    break

        # CAPTION ENTITIES

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

        # DELETE LINK

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

    await create_group_if_not_exists(
        telegram_chat_id=message.chat.id,
        title=(
            message.chat.title
            or "Noma'lum"
        ),
    )

    # =========================
    # CHECK ACTIVE
    # =========================

    active = await is_group_active(
        message.chat.id
    )

    print(
        "GROUP ACTIVE:",
        active,
    )

    if not active:
        return

    # =========================
    # SAVE MESSAGE
    # =========================

    text = (
        message.text
        or message.caption
        or ""
    )

    try:

        await save_group_message(
            chat_id=message.chat.id,
            telegram_message_id=(
                message.message_id
            ),
            telegram_user_id=(
                message.from_user.id
            ),
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

        print(
            "MESSAGE SAVED"
        )

    except Exception as e:

        print(
            "SAVE ERROR:",
            repr(e),
        )