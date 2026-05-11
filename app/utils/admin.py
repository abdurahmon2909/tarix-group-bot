def is_admin(
    telegram_id: int,
) -> bool:

    from app.config import settings

    return telegram_id in settings.ADMINS