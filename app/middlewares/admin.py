@router.message(
    ManualReportStates.waiting_for_end_date
)
async def receive_end_date(
    message: Message,
    state: FSMContext,
):

    if not message.text:
        return

    end_dt = parse_datetime(
        message.text
    )

    if not end_dt:

        await message.answer(
            "❌ Format noto'g'ri"
        )

        return

    data = await state.get_data()

    start_dt = datetime.fromisoformat(
        data["start_dt"]
    )

    group_id = data["report_group_id"]

    groups = await get_active_groups()

    group_name = "Noma'lum guruh"

    for group in groups:

        if (
            group.telegram_chat_id
            == group_id
        ):

            group_name = group.title

            break

    await message.answer(
        "📊 Hisobot tayyorlanmoqda..."
    )

    stats = await get_stats_for_range(
        chat_id=group_id,
        start_dt=start_dt,
        end_dt=end_dt,
    )

    stats["group_name"] = (
        group_name
    )

    stats["group_id"] = (
        group_id
    )

    period_label = (
        f"{start_dt.strftime('%d.%m.%Y %H:%M')}"
        f" - "
        f"{end_dt.strftime('%d.%m.%Y %H:%M')}"
    )

    os.makedirs(
        "reports",
        exist_ok=True,
    )

    filename = (
        f"reports/"
        f"{group_name}_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    )

    await asyncio.to_thread(
        build_pdf_report,
        stats,
        period_label,
        filename,
    )

    await message.answer_document(
        FSInputFile(
            filename,
            filename=(
                f"HISOBOT - "
                f"{group_name}.pdf"
            ),
        ),
        caption=(
            f"📊 {group_name}\n"
            f"📅 {period_label}"
        ),
    )

    await state.clear()