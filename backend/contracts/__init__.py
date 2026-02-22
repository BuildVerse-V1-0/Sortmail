"""
SortMail Contracts
==================

This module defines ALL inter-module data transfer objects.

BOUNDARY CONTRACTS (cross module boundaries):
- EmailThreadV1: Ingestion → Intelligence
- ThreadIntelV1: Intelligence → Workflow  
- TaskDTOv1, DraftDTOv1, CalendarSuggestionV1, WaitingForDTOv1: Workflow → API/UI

INTERNAL TYPES (embedded within boundary contracts):
- EmailMessage, AttachmentRef (inside EmailThreadV1)
- ExtractedDeadline, ExtractedEntity, AttachmentIntel (inside ThreadIntelV1)
- Placeholder (inside DraftDTOv1)

All modules MUST import contracts from here. No exceptions.
"""

# =============================================================================
# BOUNDARY CONTRACT #1: Ingestion → Intelligence
# =============================================================================
from .ingestion import (
    EmailThreadV1,
    # Internal types (for reference, embedded in EmailThreadV1)
    AttachmentRef,
    EmailMessage,
)

# =============================================================================
# BOUNDARY CONTRACT #2: Intelligence → Workflow
# =============================================================================
from .intelligence import (
    ThreadIntelV1,
    # Enums
    IntentType,
    # Internal types (for reference, embedded in ThreadIntelV1)
    ExtractedDeadline,
    ExtractedEntity,
    AttachmentIntel,
)

# =============================================================================
# BOUNDARY CONTRACTS #3: Workflow → API/UI
# =============================================================================
from .workflow import (
    # Main DTOs
    TaskDTOv1,
    DraftDTOv1,
    CalendarSuggestionV1,
    WaitingForDTOv1,
    # Enums
    PriorityLevel,
    EffortLevel,
    TaskType,
    TaskStatus,
    ToneType,
    # Internal types
    Placeholder,
)
from .dashboard import (
    BriefingDTO,
    DashboardStats,
    DashboardData,
)
from .user import (
    UserDTO,
    UpdateProfileRequest,
)

# =============================================================================
# EXPORTS
# =============================================================================

# Boundary Contracts (what modules should primarily use)
BOUNDARY_CONTRACTS = [
    "EmailThreadV1",
    "ThreadIntelV1",
    "TaskDTOv1",
    "DraftDTOv1",
    "CalendarSuggestionV1",
    "WaitingForDTOv1",
]

__all__ = [
    # === BOUNDARY CONTRACTS ===
    # Ingestion → Intelligence
    "EmailThreadV1",
    # Intelligence → Workflow
    "ThreadIntelV1",
    # Workflow → API
    "TaskDTOv1",
    "DraftDTOv1",
    "CalendarSuggestionV1",
    "WaitingForDTOv1",
    "BriefingDTO",
    "DashboardStats",
    "DashboardData",
    
    # === ENUMS ===
    "IntentType",
    "PriorityLevel",
    "EffortLevel",
    "TaskType",
    "TaskStatus",
    "ToneType",
    
    # === INTERNAL TYPES (exported for testing/mocking) ===
    "AttachmentRef",
    "EmailMessage",
    "ExtractedDeadline",
    "ExtractedEntity",
    "AttachmentIntel",
    "Placeholder",
    
    # === META ===
    "BOUNDARY_CONTRACTS",
]
