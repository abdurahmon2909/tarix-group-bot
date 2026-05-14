from app.handlers.admin.panel import (
    router as panel_router,
)

from app.handlers.admin.groups import (
    router as groups_router,
)
from app.filters.admin import (
    AdminFilter,
)
from app.handlers.admin.reports import (
    router as reports_router,
)

from app.handlers.admin.broadcast import (
    router as broadcast_router,
)


# =========================
# ADMIN FILTER
# =========================

panel_router.message.filter(
    AdminFilter()
)

groups_router.message.filter(
    AdminFilter()
)

reports_router.message.filter(
    AdminFilter()
)

broadcast_router.message.filter(
    AdminFilter()
)

panel_router.callback_query.filter(
    AdminFilter()
)

groups_router.callback_query.filter(
    AdminFilter()
)

reports_router.callback_query.filter(
    AdminFilter()
)

broadcast_router.callback_query.filter(
    AdminFilter()
)
