from __future__ import annotations

from aiogram import (
    Router,
    F,
)

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
        solving_test_id=test.id
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

    await message.answer(
        (
            f"📄 {test.title}\n\n"

            f"✅ To‘g‘ri: "
            f"{result['correct']}\n"

            f"❌ Noto‘g‘ri: "
            f"{result['wrong']}\n"

            f"📊 Natija: "
            f"{result['percent']}%\n\n"

            f"{certificate_text}"
        )
    )