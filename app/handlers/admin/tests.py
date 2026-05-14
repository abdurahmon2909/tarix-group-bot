from __future__ import annotations

from aiogram import (
    Router,
    F,
)
from app.database.repositories.tests import (
    count_test_attempts,
)
from aiogram.types import (
    CallbackQuery,
    Message,
    FSInputFile,
)

from aiogram.fsm.context import (
    FSMContext,
)

from aiogram.utils.keyboard import (
    InlineKeyboardBuilder,
)

from app.states.tests import (
    CreateTestStates,
)

from app.utils.test_parser import (
    parse_answer_key,
)

from app.database.repositories.tests import (
    create_test_folder,
    get_root_test_folders,
    get_child_folders,
    get_folder_by_id,
    get_tests_by_folder,
    get_test_by_id,
    create_test,
    get_test_results,
    delete_test_by_id,
)

from app.services.reports.test_results_pdf import (
    build_test_results_pdf,
)

router = Router()


# =========================
# TESTS MENU
# =========================

@router.callback_query(
    F.data == "tests_menu"
)
async def tests_menu(
    callback: CallbackQuery,
):

    kb = InlineKeyboardBuilder()

    kb.button(
        text="➕ Test yaratish",
        callback_data="create_test",
    )

    kb.button(
        text="📂 Mavjud testlar",
        callback_data="existing_tests",
    )

    kb.button(
        text="🗑 Testni o‘chirish",
        callback_data="delete_test_menu",
    )

    kb.button(
        text="📊 Natijalar",
        callback_data="tests_results",
    )

    kb.button(
        text="🏆 Sertifikatlar",
        callback_data="certificate_templates",
    )

    kb.button(
        text="⬅️ Orqaga",
        callback_data="admin_panel",
    )

    kb.adjust(1)

    await callback.message.edit_text(
        "📚 Testlar bo‘limi",
        reply_markup=kb.as_markup(),
    )

    await callback.answer()

# =========================
# CREATE TEST
# =========================

@router.callback_query(
    F.data == "create_test"
)
async def create_test_menu(
    callback: CallbackQuery,
    state: FSMContext,
):

    await state.clear()

    folders = await get_root_test_folders()

    kb = InlineKeyboardBuilder()

    for folder in folders:

        kb.button(
            text=f"📂 {folder.name}",
            callback_data=(
                f"select_folder:{folder.id}"
            ),
        )

    kb.button(
        text="➕ Yangi papka yaratish",
        callback_data="create_folder",
    )

    kb.button(
        text="⬅️ Orqaga",
        callback_data="tests_menu",
    )

    kb.adjust(1)

    await callback.message.edit_text(
        (
            "📂 Test uchun papkani tanlang"
        ),
        reply_markup=kb.as_markup(),
    )

    await callback.answer()


# =========================
# CREATE FOLDER
# =========================

@router.callback_query(
    F.data == "create_folder"
)
async def create_folder_callback(
    callback: CallbackQuery,
    state: FSMContext,
):

    await state.set_state(
        CreateTestStates.waiting_for_folder_name
    )

    await callback.message.edit_text(
        (
            "📂 Yangi papka nomini yuboring"
        )
    )

    await callback.answer()


# =========================
# SAVE FOLDER
# =========================

@router.message(
    CreateTestStates.waiting_for_folder_name
)
async def save_folder_handler(
    message: Message,
    state: FSMContext,
):

    text = (
        message.text or ""
    ).strip()

    if len(text) < 2:

        await message.answer(
            "❌ Papka nomi juda qisqa"
        )

        return

    folder = await create_test_folder(
        name=text
    )

    await state.clear()

    kb = InlineKeyboardBuilder()

    kb.button(
        text="➕ Test yaratish",
        callback_data=(
            f"select_folder:{folder.id}"
        ),
    )

    kb.button(
        text="📚 Testlarim",
        callback_data="tests_menu",
    )

    kb.adjust(1)

    await message.answer(
        (
            f"✅ Papka yaratildi:\n\n"
            f"{folder.name}"
        ),
        reply_markup=kb.as_markup(),
    )
# =========================
# SELECT FOLDER
# =========================

@router.callback_query(
    F.data.startswith(
        "select_folder:"
    )
)
async def select_folder_handler(
    callback: CallbackQuery,
    state: FSMContext,
):

    folder_id = int(
        callback.data.split(":")[1]
    )

    folder = await get_folder_by_id(
        folder_id
    )

    if not folder:

        await callback.answer(
            "Papka topilmadi",
            show_alert=True,
        )

        return

    await state.update_data(
        folder_id=folder.id
    )

    await state.set_state(
        CreateTestStates.waiting_for_test_title
    )

    await callback.message.edit_text(
        (
            f"📂 Papka: {folder.name}\n\n"
            f"✍️ Test nomini yuboring"
        )
    )

    await callback.answer()


# =========================
# SAVE TEST TITLE
# =========================

@router.message(
    CreateTestStates.waiting_for_test_title
)
async def save_test_title_handler(
    message: Message,
    state: FSMContext,
):

    text = (
        message.text or ""
    ).strip()

    if len(text) < 2:

        await message.answer(
            "❌ Test nomi juda qisqa"
        )

        return

    await state.update_data(
        test_title=text
    )

    await state.set_state(
        CreateTestStates.waiting_for_pdf
    )

    await message.answer(
        (
            "📄 Endi PDF faylni yuboring"
        )
    )


# =========================
# SAVE PDF
# =========================

@router.message(
    CreateTestStates.waiting_for_pdf,
    F.document
)
async def save_pdf_handler(
    message: Message,
    state: FSMContext,
):

    document = message.document

    if not document:

        return

    mime = (
        document.mime_type or ""
    )

    if mime != "application/pdf":

        await message.answer(
            "❌ Faqat PDF yuboring"
        )

        return

    await state.update_data(
        telegram_file_id=document.file_id
    )

    await state.set_state(
        CreateTestStates.waiting_for_answer_key
    )

    await message.answer(
        (
            "🔑 Javoblar kalitini yuboring\n\n"
            "Masalan:\n"
            "1A2D3C4E5B"
        )
    )
# =========================
# SAVE ANSWER KEY
# =========================

@router.message(
    CreateTestStates.waiting_for_answer_key
)
async def save_answer_key_handler(
    message: Message,
    state: FSMContext,
):

    text = (
        message.text or ""
    ).strip()

    parsed = parse_answer_key(
        text
    )

    if not parsed:

        await message.answer(
            (
                "❌ Javoblar topilmadi\n\n"
                "Misol:\n"
                "1A2D3C4E5B"
            )
        )

        return

    data = await state.get_data()

    folder_id = data["folder_id"]

    test_title = data["test_title"]

    telegram_file_id = data[
        "telegram_file_id"
    ]

    question_count = len(
        parsed
    )

    # TEMP TEMPLATE ID
    certificate_template_id = 1

    test = await create_test(
        folder_id=folder_id,
        certificate_template_id=(
            certificate_template_id
        ),
        title=test_title,
        telegram_file_id=(
            telegram_file_id
        ),
        answer_key_json=parsed,
        question_count=question_count,
    )

    await state.clear()

    kb = InlineKeyboardBuilder()

    kb.button(
        text="📚 Testlarim",
        callback_data="tests_menu",
    )

    kb.adjust(1)

    await message.answer(
        (
            "✅ Test yuklandi\n\n"

            f"📄 {test.title}\n"
            f"📊 Savollar: "
            f"{question_count}"
        ),
        reply_markup=kb.as_markup(),
    )

# =========================
# RESULTS MENU
# =========================

@router.callback_query(
    F.data == "tests_results"
)
async def tests_results_menu(
    callback: CallbackQuery,
):

    folders = await get_root_test_folders()

    kb = InlineKeyboardBuilder()

    for folder in folders:

        kb.button(
            text=f"📂 {folder.name}",
            callback_data=(
                f"results_folder:{folder.id}"
            ),
        )

    kb.adjust(1)

    await callback.message.edit_text(
        "📊 Natijalar bo‘limi",
        reply_markup=kb.as_markup(),
    )

    await callback.answer()


# =========================
# RESULTS FOLDER
# =========================

@router.callback_query(
    F.data.startswith(
        "results_folder:"
    )
)
async def results_folder_handler(
    callback: CallbackQuery,
):

    folder_id = int(
        callback.data.split(":")[1]
    )

    tests = await get_tests_by_folder(
        folder_id
    )

    kb = InlineKeyboardBuilder()

    for test in tests:

        kb.button(
            text=f"📄 {test.title}",
            callback_data=(
                f"results_test:{test.id}"
            ),
        )

    kb.adjust(1)

    await callback.message.edit_text(
        "📄 Testni tanlang",
        reply_markup=kb.as_markup(),
    )

    await callback.answer()


# =========================
# GENERATE RESULTS PDF
# =========================

@router.callback_query(
    F.data.startswith(
        "results_test:"
    )
)
async def generate_results_pdf(
    callback: CallbackQuery,
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

    results = await get_test_results(
        test_id
    )

    pdf_path = (
        build_test_results_pdf(
            test_title=test.title,
            results=results,
        )
    )

    await callback.message.answer_document(
        document=FSInputFile(
            str(pdf_path)
        ),
        caption=(
            f"📊 {test.title}"
        ),
    )

    await callback.answer()

# =========================
# DELETE TEST MENU
# =========================

@router.callback_query(
    F.data == "delete_test_menu"
)
async def delete_test_menu(
    callback: CallbackQuery,
):

    folders = await get_root_test_folders()

    kb = InlineKeyboardBuilder()

    for folder in folders:

        kb.button(
            text=f"📂 {folder.name}",
            callback_data=(
                f"delete_folder:{folder.id}"
            ),
        )

    kb.button(
        text="⬅️ Orqaga",
        callback_data="tests_menu",
    )

    kb.adjust(1)

    await callback.message.edit_text(
        "🗑 O‘chirish uchun papkani tanlang",
        reply_markup=kb.as_markup(),
    )

    await callback.answer()


# =========================
# DELETE FOLDER
# =========================

@router.callback_query(
    F.data.startswith(
        "delete_folder:"
    )
)
async def delete_folder_handler(
    callback: CallbackQuery,
):

    folder_id = int(
        callback.data.split(":")[1]
    )

    tests = await get_tests_by_folder(
        folder_id
    )

    kb = InlineKeyboardBuilder()

    for test in tests:

        kb.button(
            text=f"❌ {test.title}",
            callback_data=(
                f"delete_test:{test.id}"
            ),
        )

    kb.button(
        text="⬅️ Orqaga",
        callback_data="delete_test_menu",
    )

    kb.adjust(1)

    await callback.message.edit_text(
        "❌ O‘chiriladigan testni tanlang",
        reply_markup=kb.as_markup(),
    )

    await callback.answer()


# =========================
# DELETE TEST
# =========================

@router.callback_query(
    F.data.startswith(
        "delete_test:"
    )
)
async def delete_test_handler(
    callback: CallbackQuery,
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

    await delete_test_by_id(
        test_id
    )

    kb = InlineKeyboardBuilder()

    kb.button(
        text="📚 Testlarim",
        callback_data="tests_menu",
    )

    kb.adjust(1)

    await callback.message.edit_text(
        (
            f"✅ Test o‘chirildi\n\n"
            f"{test.title}"
        ),
        reply_markup=kb.as_markup(),
    )

    await callback.answer()

# =========================
# EXISTING TESTS
# =========================

@router.callback_query(
    F.data == "existing_tests"
)
async def existing_tests_menu(
    callback: CallbackQuery,
):

    folders = await get_root_test_folders()

    kb = InlineKeyboardBuilder()

    for folder in folders:

        kb.button(
            text=f"📂 {folder.name}",
            callback_data=(
                f"existing_folder:{folder.id}"
            ),
        )

    kb.button(
        text="⬅️ Orqaga",
        callback_data="tests_menu",
    )

    kb.adjust(1)

    await callback.message.edit_text(
        "📂 Mavjud testlar",
        reply_markup=kb.as_markup(),
    )

    await callback.answer()


# =========================
# EXISTING FOLDER
# =========================

@router.callback_query(
    F.data.startswith(
        "existing_folder:"
    )
)
async def existing_folder_handler(
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
                f"existing_folder:{folder.id}"
            ),
        )

    for test in tests:

        attempts = (
            await count_test_attempts(
                test.id
            )
        )

        kb.button(
            text=(
                f"📄 {test.title}"
                f" ({attempts})"
            ),
            callback_data=(
                f"show_test:{test.id}"
            ),
        )

    kb.button(
        text="⬅️ Orqaga",
        callback_data="existing_tests",
    )

    kb.adjust(1)

    await callback.message.edit_text(
        "📂 Papka ichidagi testlar",
        reply_markup=kb.as_markup(),
    )

    await callback.answer()


# =========================
# SHOW TEST
# =========================

@router.callback_query(
    F.data.startswith(
        "show_test:"
    )
)
async def show_test_handler(
    callback: CallbackQuery,
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

    attempts = (
        await count_test_attempts(
            test.id
        )
    )

    kb = InlineKeyboardBuilder()

    kb.button(
        text="📊 Natijalar",
        callback_data=(
            f"results_test:{test.id}"
        ),
    )

    kb.button(
        text="🗑 O‘chirish",
        callback_data=(
            f"delete_test:{test.id}"
        ),
    )

    kb.button(
        text="⬅️ Orqaga",
        callback_data=(
            f"existing_folder:{test.folder_id}"
        ),
    )

    kb.adjust(1)

    await callback.message.edit_text(
        (
            f"📄 {test.title}\n\n"

            f"📊 Savollar: "
            f"{test.question_count}\n"

            f"📝 Urinishlar: "
            f"{attempts}\n"

            f"🟢 Aktiv: "
            f"{'Ha' if test.is_active else 'Yo‘q'}"
        ),
        reply_markup=kb.as_markup(),
    )

    await callback.answer()