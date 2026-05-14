from __future__ import annotations

from aiogram import (
    Router,
    F,
)
from aiogram.types import (
    FSInputFile,
)
from app.database.repositories.tests import (
    create_certificate,
)
from app.services.certificates.certificate_service import (
    generate_certificate,
)

import uuid
from datetime import datetime
from aiogram.types import (
    CallbackQuery,
    Message,
)
from aiogram.fsm.context import (
    FSMContext,
)

from app.states.tests import (
    SolveTestStates,
)

from app.utils.test_parser import (
    parse_answer_key,
    compare_answers,
)
from aiogram.utils.keyboard import (
    InlineKeyboardBuilder,
)

from app.database.repositories.tests import (
    get_root_test_folders,
    get_child_folders,
    get_tests_by_folder,
    get_test_by_id,
    get_user_db_id,
    get_attempts_count,
    create_test_attempt,
)

router = Router()


# =========================
# TESTS MENU
# =========================

@router.callback_query(
    F.data == "check_test"
)
async def tests_menu(
    callback: CallbackQuery,
):

    folders = await get_root_test_folders()

    kb = InlineKeyboardBuilder()

    for folder in folders:

        kb.button(
            text=f"📂 {folder.name}",
            callback_data=(
                f"user_folder:{folder.id}"
            ),
        )

    kb.adjust(1)

    await callback.message.edit_text(
        "📚 Testlar bo‘limi",
        reply_markup=kb.as_markup(),
    )

    await callback.answer()


# =========================
# OPEN FOLDER
# =========================

@router.callback_query(
    F.data.startswith(
        "user_folder:"
    )
)
async def open_folder(
    callback: CallbackQuery,
):

    folder_id = int(
        callback.data.split(":")[1]
    )

    child_folders = (
        await get_child_folders(
            folder_id
        )
    )

    tests = await get_tests_by_folder(
        folder_id
    )

    kb = InlineKeyboardBuilder()

    for folder in child_folders:

        kb.button(
            text=f"📂 {folder.name}",
            callback_data=(
                f"user_folder:{folder.id}"
            ),
        )

    for test in tests:

        kb.button(
            text=f"📄 {test.title}",
            callback_data=(
                f"open_test:{test.id}"
            ),
        )

    kb.button(
        text="⬅️ Orqaga",
        callback_data="check_test",
    )

    kb.adjust(1)

    await callback.message.edit_text(
        "📚 Papka ichidagi testlar",
        reply_markup=kb.as_markup(),
    )

    await callback.answer()


# =========================
# OPEN TEST
# =========================

@router.callback_query(
    F.data.startswith(
        "open_test:"
    )
)
async def open_test(
    callback: CallbackQuery,
    state: FSMContext,
):

    test_id = int(
        callback.data.split(":")[1]
    )

    test = await get_test_by_id(
        test_id
    )

    if not test:

        await callback.answer(
            "Test topilmadi",
            show_alert=True,
        )

        return
    await state.clear()

    await state.update_data(
        solving_test_id=test.id,
        started_at=datetime.utcnow().isoformat(),
    )

    await state.set_state(
        SolveTestStates.waiting_for_answers
    )
    await callback.message.answer_document(
        document=test.telegram_file_id,
        caption=(
            "📝 Javoblarni quyidagi "
            "formatda yuboring:\n\n"
            "1A2D3C4E5B"
        ),
    )

    await callback.answer()

# =========================
# CHECK ANSWERS
# =========================

@router.message(
    SolveTestStates.waiting_for_answers
)
async def check_answers_handler(
    message: Message,
    state: FSMContext,
):

    text = (
        message.text or ""
    ).strip()

    parsed_answers = parse_answer_key(
        text
    )

    if not parsed_answers:

        await message.answer(
            (
                "❌ Javoblar topilmadi\n\n"
                "Misol:\n"
                "1A2D3C4E5B"
            )
        )

        return

    data = await state.get_data()

    test_id = data[
        "solving_test_id"
    ]

    test = await get_test_by_id(
        test_id
    )

    if not test:

        await state.clear()

        await message.answer(
            "❌ Test topilmadi"
        )

        return

    result = compare_answers(
        correct_answers=(
            test.answer_key_json
        ),
        user_answers=parsed_answers,
    )

    await state.clear()

    certificate_text = (
        "🏆 Sertifikat beriladi"
        if result["percent"] >= 70
        else "❌ Sertifikat yo‘q"
    )
    started_at = datetime.fromisoformat(
        data["started_at"]
    )

    duration_seconds = int(
        (
                datetime.utcnow()
                - started_at
        ).total_seconds()
    )

    user_db_id = await get_user_db_id(
        message.from_user.id
    )

    if not user_db_id:
        await message.answer(
            "❌ User topilmadi"
        )

        return

    attempts_count = (
        await get_attempts_count(
            user_id=user_db_id,
            test_id=test.id,
        )
    )

    attempt_number = (
            attempts_count + 1
    )

    certificate_generated = (
            result["percent"] >= 70
    )
    certificate_file = None

    if certificate_generated:
        certificate_id = (
            str(uuid.uuid4())[:8]
            .upper()
        )

        certificate_file = (
            generate_certificate(
                fullname=(
                    message.from_user.full_name
                ),
                test_name=test.title,
                score_percent=(
                    result["percent"]
                ),
                correct_answers=(
                    result["correct"]
                ),
                question_count=(
                    test.question_count
                ),
                duration_seconds=(
                    duration_seconds
                ),
                certificate_id=(
                    certificate_id
                ),
            )
        )
    attempt = await create_test_attempt(
        user_id=user_db_id,
        test_id=test.id,
        submitted_answers=(
            parsed_answers
        ),
        correct_answers=(
            result["correct"]
        ),
        wrong_answers=(
            result["wrong"]
        ),
        score_percent=(
            result["percent"]
        ),
        duration_seconds=(
            duration_seconds
        ),
        attempt_number=(
            attempt_number
        ),
        certificate_generated=(
            certificate_generated
        ),
    )
    await message.answer(
        (
            f"📄 {test.title}\n\n"

            f"✅ To‘g‘ri: "
            f"{result['correct']}\n"

            f"❌ Noto‘g‘ri: "
            f"{result['wrong']}\n"

            f"📊 Natija: "
            f"{result['percent']}%\n\n"

            f"🔁 Urinish: "
            f"{attempt_number}\n"

            f"⏱ Vaqt: "
            f"{duration_seconds} sec\n\n"

            f"{certificate_text}"
        )
    )

    if certificate_file:

        telegram_message = (
            await message.answer_document(
                document=FSInputFile(
                    path=str(
                        certificate_file
                    )
                ),
                caption=(
                    "🏆 Sertifikatingiz tayyor!"
                ),
            )
        )

        document = (
            telegram_message.document
        )

        if document:
            await create_certificate(
                attempt_id=attempt.id,
                certificate_number=(
                    certificate_id
                ),
                telegram_file_id=(
                    document.file_id
                ),
            )