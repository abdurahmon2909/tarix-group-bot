from __future__ import annotations

import re
import asyncio

from aiogram import (
    Router,
)
from aiogram import F
from aiogram.enums import (
    ChatType,
    ChatMemberStatus,
)

from aiogram.types import (
    Message,
)
from app.config import settings

from app.services.moderation.fullname_filter import (
    detect_nsfw_fullname,
    is_fullname_cached,
    update_fullname_cache,
    detect_nsfw_text,
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
    # STRICT FULLNAME FILTER
    # =========================

    user = message.from_user

    if user.id not in settings.ADMINS:
        member = await message.bot.get_chat_member(
            chat_id=message.chat.id,
            user_id=user.id,
        )

        if member.status in [
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.CREATOR,
        ]:
            return

        fullname = (
            user.full_name or ""
        ).strip()

        if fullname:

            # CACHE CHECK

            if not is_fullname_cached(
                user.id,
                fullname,
            ):

                reason = (
                    detect_nsfw_fullname(
                        fullname
                    )
                )

                # UPDATE CACHE

                update_fullname_cache(
                    user.id,
                    fullname,
                )

                if reason:

                    # DELETE MESSAGE

                    try:
                        await message.delete()
                    except:
                        pass

                    # BAN USER

                    try:
                        await message.bot.ban_chat_member(
                            chat_id=message.chat.id,
                            user_id=user.id,
                        )
                    except:
                        return

                    username = (
                        f"@{user.username}"
                        if user.username
                        else "USERNAME YO'Q"
                    )

                    log_text = (
                        "🚨 FOYDALANUVCHI "
                        "AVTOMATIK BAN QILINDI 🚨\n\n"

                        f"👤 ISM:\n"
                        f"{fullname}\n\n"

                        f"🔗 USERNAME:\n"
                        f"{username}\n\n"

                        f"🆔 USER ID:\n"
                        f"{user.id}\n\n"
                        f"🏘 GURUH:\n"
                        f"{message.chat.title}\n\n"
                        
                        f"📛 SABAB:\n"
                        f"{reason}\n\n"

                        "🤖 AMAL:\n"
                        "XABAR O'CHIRILDI "
                        "VA FOYDALANUVCHI "
                        "BANGA YUBORILDI"
                    )

                    # SEND ADMINS

                    for admin_id in settings.ADMINS:

                        try:
                            await message.bot.send_message(
                                chat_id=admin_id,
                                text=log_text,
                            )
                        except:
                            pass

                    return
                # =========================
                # STRICT MESSAGE FILTER
                # =========================

                text_to_check = (
                        message.text
                        or message.caption
                        or ""
                ).strip()

                if text_to_check:

                    reason = (
                        detect_nsfw_text(
                            text_to_check
                        )
                    )

                    if reason:

                        # DELETE MESSAGE

                        try:
                            await message.delete()

                            await asyncio.sleep(0.7)

                        except:
                            pass

                        # BAN USER

                        try:
                            await message.bot.ban_chat_member(
                                chat_id=message.chat.id,
                                user_id=user.id,
                            )
                        except:
                            return

                        username = (
                            f"@{user.username}"
                            if user.username
                            else "USERNAME YO'Q"
                        )

                        log_text = (
                            "🚨 NSFW XABAR ANIQLANDI 🚨\n\n"

                            f"👤 ISM:\n"
                            f"{fullname}\n\n"

                            f"🔗 USERNAME:\n"
                            f"{username}\n\n"

                            f"🆔 USER ID:\n"
                            f"{user.id}\n\n"

                            f"🏘 GURUH:\n"
                            f"{message.chat.title}\n\n"

                            f"📛 SABAB:\n"
                            f"{reason}\n\n"

                            f"💬 XABAR:\n"
                            f"{text_to_check[:300]}\n\n"

                            "🤖 AMAL:\n"
                            "XABAR O'CHIRILDI "
                            "VA FOYDALANUVCHI "
                            "BANGA YUBORILDI"
                        )

                        for admin_id in settings.ADMINS:

                            try:
                                await message.bot.send_message(
                                    chat_id=admin_id,
                                    text=log_text,
                                )
                            except:
                                pass

                        return


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

        if message.text:

            print(
                "TEXT:",
                repr(message.text)
            )

            if LINK_REGEX.search(
                    message.text.strip()
            ):
                print(
                    "TEXT LINK DETECTED"
                )

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

        import traceback

        traceback.print_exc()

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

