# Models Package - All 13 tables from database_schema.md
from .user import User, EmailProvider
from .task import Task, TaskType, TaskStatus, PriorityLevel, EffortLevel
from .thread import Thread, Message
from .email import Email
from .attachment import Attachment
from .draft import Draft, ToneType
from .connected_account import ConnectedAccount, ProviderType
from .document import Document
from .reminder import Reminder
from .vip_domain import VIPDomain
from .calendar_suggestion import CalendarSuggestion
from .credits import UserCredits, CreditTransaction, CreditPricing, CreditPackage

__all__ = [
    # Users & Auth
    "User",
    "EmailProvider",
    "ConnectedAccount",
    "ProviderType",
    # Threads & Emails
    "Thread",
    "Message",
    "Email",
    "Attachment",
    "Document",
    # Tasks & Workflow
    "Task",
    "TaskType",
    "TaskStatus",
    "PriorityLevel",
    "EffortLevel",
    "Draft",
    "ToneType",
    # Follow-ups
    "Reminder",
    "VIPDomain",
    "CalendarSuggestion",
    # Credits
    "UserCredits",
    "CreditTransaction",
    "CreditPricing",
    "CreditPackage",
]
