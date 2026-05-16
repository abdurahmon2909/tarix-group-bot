from __future__ import annotations

from aiogram import (
    Router,
    F,
)
from aiogram.types import (
    CallbackQuery,
    Message,
    FSInputFile,
)
from app.states.tests import (
    CertificateTemplateStates,
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
    update_test_answer_key,
    delete_folder_by_id,

    count_test_attempts,

    create_certificate_template,
    get_certificate_templates,
    get_certificate_template_by_id,
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
        text="🗑 Papkani o‘chirish",
        callback_data="delete_test_folder_menu",
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

    await state.update_data(
        parsed_answers=parsed,
        question_count=question_count,
    )

    templates = (
        await get_certificate_templates()
    )

    if not templates:
        await message.answer(
            (
                "❌ Template topilmadi\n\n"
                "Avval sertifikat "
                "template yarating"
            )
        )

        return

    kb = InlineKeyboardBuilder()

    for template in templates:
        kb.button(
            text=f"🏆 {template.name}",
            callback_data=(
                f"select_template:{template.id}"
            ),
        )

    kb.adjust(1)

    await state.set_state(
        CreateTestStates.waiting_for_certificate_template
    )

    await message.answer(
        "🏆 Sertifikat template tanlang",
        reply_markup=kb.as_markup(),
    )

    return

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

    kb = InlineKeyboardBuilder()

    kb.button(
        text="📊 Natijalar",
        callback_data="tests_results",
    )

    kb.button(
        text="🏠 Admin panel",
        callback_data="admin_panel",
    )

    kb.adjust(1)

    await callback.message.answer_document(
        document=FSInputFile(
            str(pdf_path)
        ),
        caption=(
            f"📊 {test.title}"
        ),
        reply_markup=kb.as_markup(),
    )

# =========================
# DELETE TEST FOLDER MENU
# =========================

@router.callback_query(
    F.data == "delete_test_folder_menu"
)
async def delete_test_folder_menu(
    callback: CallbackQuery,
):

    folders = await get_root_test_folders()

    if not folders:

        await callback.answer(
            "Papkalar topilmadi",
            show_alert=True,
        )

        return

    kb = InlineKeyboardBuilder()

    for folder in folders:

        kb.button(
            text=f"🗑 📂 {folder.name}",
            callback_data=(
                f"delete_test_folder:"
                f"{folder.id}"
            ),
        )

    kb.button(
        text="⬅️ Orqaga",
        callback_data="tests_menu",
    )

    kb.adjust(1)

    await callback.message.edit_text(
        (
            "🗑 O‘chiriladigan "
            "papkani tanlang"
        ),
        reply_markup=kb.as_markup(),
    )

    await callback.answer()

# =========================
# CONFIRM DELETE FOLDER
# =========================

@router.callback_query(
    F.data.startswith(
        "delete_test_folder:"
    )
)
async def confirm_delete_test_folder(
    callback: CallbackQuery,
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

    kb = InlineKeyboardBuilder()

    kb.button(
        text="✅ Ha, o‘chirish",
        callback_data=(
            f"confirm_delete_test_folder:"
            f"{folder.id}"
        ),
    )

    kb.button(
        text="❌ Bekor qilish",
        callback_data=(
            "delete_test_folder_menu"
        ),
    )

    kb.adjust(1)

    await callback.message.edit_text(
        (
            "⚠️ DIQQAT\n\n"

            f"📂 {folder.name}\n\n"

            "Bu papka ichidagi:\n"
            "• barcha testlar\n"
            "• child papkalar\n"
            "• natijalar\n\n"

            "o‘chiriladi.\n\n"

            "Davom etilsinmi?"
        ),
        reply_markup=kb.as_markup(),
    )

    await callback.answer()

# =========================
# FINAL DELETE FOLDER
# =========================

@router.callback_query(
    F.data.startswith(
        "confirm_delete_test_folder:"
    )
)
async def final_delete_test_folder(
    callback: CallbackQuery,
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

    folder_name = folder.name

    await delete_folder_by_id(
        folder_id
    )

    kb = InlineKeyboardBuilder()

    kb.button(
        text="📚 Testlar",
        callback_data="tests_menu",
    )

    kb.adjust(1)

    await callback.message.edit_text(
        (
            "✅ Papka o‘chirildi\n\n"

            f"📂 {folder_name}"
        ),
        reply_markup=kb.as_markup(),
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

# =========================
# CONFIRM DELETE TEST
# =========================

@router.callback_query(
    F.data.startswith(
        "delete_test:"
    )
)
async def confirm_delete_test_handler(
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

    kb = InlineKeyboardBuilder()

    kb.button(
        text="✅ Ha, o‘chirish",
        callback_data=(
            f"confirm_delete_test:"
            f"{test.id}"
        ),
    )

    kb.button(
        text="❌ Bekor qilish",
        callback_data=(
            f"show_test:{test.id}"
        ),
    )

    kb.adjust(1)

    await callback.message.edit_text(
        (
            "⚠️ TESTNI O‘CHIRISH\n\n"

            f"📄 {test.title}\n\n"

            "Bu test:\n"
            "• natijalari\n"
            "• urinishlari\n"
            "• sertifikatlari\n\n"

            "bilan birga o‘chiriladi.\n\n"

            "Davom etilsinmi?"
        ),
        reply_markup=kb.as_markup(),
    )

    await callback.answer()


# =========================
# FINAL DELETE TEST
# =========================

@router.callback_query(
    F.data.startswith(
        "confirm_delete_test:"
    )
)
async def final_delete_test_handler(
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

    test_title = test.title

    await delete_test_by_id(
        test_id
    )

    kb = InlineKeyboardBuilder()

    kb.button(
        text="📚 Testlar",
        callback_data="tests_menu",
    )

    kb.adjust(1)

    await callback.message.edit_text(
        (
            "✅ Test o‘chirildi\n\n"

            f"📄 {test_title}"
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
        text="✏️ Kalitni tahrirlash",
        callback_data=(
            f"edit_answer_key:{test.id}"
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


# =========================
# EDIT ANSWER KEY
# =========================

@router.callback_query(
    F.data.startswith(
        "edit_answer_key:"
    )
)
async def edit_answer_key_handler(
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

    current_answers = []

    for number, answer in sorted(
        test.answer_key_json.items(),
        key=lambda x: int(x[0])
    ):

        current_answers.append(
            f"{number}.{answer.upper()}"
        )

    formatted_answers = " ".join(
        current_answers
    )

    await state.update_data(
        edit_test_id=test.id
    )

    await state.set_state(
        CreateTestStates.waiting_for_edit_answer_key
    )

    kb = InlineKeyboardBuilder()

    kb.button(
        text="❌ Bekor qilish",
        callback_data=(
            f"show_test:{test.id}"
        ),
    )

    kb.adjust(1)

    await callback.message.edit_text(
        (
            f"✏️ {test.title}\n\n"

            f"📌 Hozirgi kalit:\n\n"

            f"<code>{formatted_answers}</code>\n\n"

            f"📝 Yangi javoblar kalitini yuboring\n\n"

            f"Misol:\n"
            f"<code>1A2D3C4E5B</code>"
        ),
        parse_mode="HTML",
        reply_markup=kb.as_markup(),
    )

    await callback.answer()
# =========================
# CERTIFICATE MENU
# =========================

@router.callback_query(
    F.data == "certificate_templates"
)
async def certificate_templates_menu(
    callback: CallbackQuery,
):

    templates = (
        await get_certificate_templates()
    )

    kb = InlineKeyboardBuilder()

    kb.button(
        text="➕ Template qo‘shish",
        callback_data="add_certificate_template",
    )

    for template in templates:

        kb.button(
            text=f"🏆 {template.name}",
            callback_data=(
                f"show_template:{template.id}"
            ),
        )

    kb.button(
        text="⬅️ Orqaga",
        callback_data="tests_menu",
    )

    kb.adjust(1)

    await callback.message.edit_text(
        "🏆 Sertifikat shablonlari",
        reply_markup=kb.as_markup(),
    )

    await callback.answer()


# =========================
# ADD TEMPLATE
# =========================

@router.callback_query(
    F.data == "add_certificate_template"
)
async def add_template_callback(
    callback: CallbackQuery,
    state: FSMContext,
):

    await state.set_state(
        CertificateTemplateStates.waiting_for_template_name
    )

    await callback.message.edit_text(
        "✍️ Template nomini yuboring"
    )

    await callback.answer()


# =========================
# SAVE TEMPLATE NAME
# =========================

@router.message(
    CertificateTemplateStates.waiting_for_template_name
)
async def save_template_name(
    message: Message,
    state: FSMContext,
):

    text = (
        message.text or ""
    ).strip()

    if len(text) < 2:

        await message.answer(
            "❌ Nomi juda qisqa"
        )

        return

    await state.update_data(
        template_name=text
    )

    await state.set_state(
        CertificateTemplateStates.waiting_for_background
    )

    await message.answer(
        "🖼 Background image yuboring"
    )


# =========================
# SAVE EDITED ANSWER KEY
# =========================

@router.message(
    CreateTestStates.waiting_for_edit_answer_key
)
async def save_edited_answer_key_handler(
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
                "❌ Javoblar formati noto‘g‘ri\n\n"
                "Misol:\n"
                "1A2D3C4E5B"
            )
        )

        return

    data = await state.get_data()

    test_id = data.get(
        "edit_test_id"
    )

    test = await update_test_answer_key(
        test_id=test_id,
        answer_key_json=parsed,
        question_count=len(parsed),
    )

    await state.clear()

    kb = InlineKeyboardBuilder()

    kb.button(
        text="📄 Testga qaytish",
        callback_data=(
            f"show_test:{test.id}"
        ),
    )

    kb.adjust(1)

    await message.answer(
        (
            "✅ Test javoblar kaliti yangilandi\n\n"

            f"📊 Savollar soni: "
            f"{len(parsed)}"
        ),
        reply_markup=kb.as_markup(),
    )
# =========================
# SAVE BACKGROUND
# =========================

@router.message(
    CertificateTemplateStates.waiting_for_background,
    F.photo
)
async def save_background(
    message: Message,
    state: FSMContext,
):

    photo = message.photo[-1]

    await state.update_data(
        background_file_id=photo.file_id
    )

    await state.set_state(
        CertificateTemplateStates.waiting_for_signature
    )

    await message.answer(
        "✍️ Signature image yuboring"
    )


# =========================
# SAVE SIGNATURE
# =========================

@router.message(
    CertificateTemplateStates.waiting_for_signature,
    F.photo
)
async def save_signature(
    message: Message,
    state: FSMContext,
):

    photo = message.photo[-1]

    data = await state.get_data()

    template = (
        await create_certificate_template(
            name=data["template_name"],
            background_image_file_id=(
                data["background_file_id"]
            ),
            signature_image_file_id=(
                photo.file_id
            ),
        )
    )

    await state.clear()

    kb = InlineKeyboardBuilder()

    kb.button(
        text="🏆 Sertifikatlar",
        callback_data=(
            "certificate_templates"
        ),
    )

    kb.adjust(1)

    await message.answer(
        (
            f"✅ Template yaratildi\n\n"
            f"{template.name}"
        ),
        reply_markup=kb.as_markup(),
    )

# =========================
# SELECT TEMPLATE
# =========================

@router.callback_query(
    CreateTestStates.waiting_for_certificate_template,
    F.data.startswith(
        "select_template:"
    )
)
async def select_template_handler(
    callback: CallbackQuery,
    state: FSMContext,
):

    template_id = int(
        callback.data.split(":")[1]
    )

    template = (
        await get_certificate_template_by_id(
            template_id
        )
    )

    if not template:

        await callback.answer(
            "Template topilmadi",
            show_alert=True,
        )

        return

    data = await state.get_data()

    test = await create_test(
        folder_id=data["folder_id"],
        certificate_template_id=(
            template.id
        ),
        title=data["test_title"],
        telegram_file_id=(
            data["telegram_file_id"]
        ),
        answer_key_json=(
            data["parsed_answers"]
        ),
        question_count=(
            data["question_count"]
        ),
    )

    await state.clear()

    kb = InlineKeyboardBuilder()

    kb.button(
        text="📚 Testlarim",
        callback_data="tests_menu",
    )

    kb.adjust(1)

    await callback.message.edit_text(
        (
            "✅ Test yaratildi\n\n"

            f"📄 {test.title}\n"
            f"🏆 Template: "
            f"{template.name}"
        ),
        reply_markup=kb.as_markup(),
    )

    await callback.answer()