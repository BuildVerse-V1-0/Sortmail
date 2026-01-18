# API Routes Package
from .auth import router as auth_router
from .tasks import router as tasks_router
from .threads import router as threads_router
from .drafts import router as drafts_router
from .emails import router as emails_router
from .reminders import router as reminders_router

__all__ = [
    "auth_router",
    "tasks_router", 
    "threads_router",
    "drafts_router",
    "emails_router",
    "reminders_router",
]
