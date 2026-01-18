# SortMail — Module Contracts

> The Constitution of Your System

---

## ⚠️ Critical Design Principle

**There are exactly 3 BOUNDARY CONTRACTS in this system:**

```
┌──────────────┐         ┌───────────────┐         ┌────────────────┐
│  Ingestion   │────────▶│  Intelligence │────────▶│    Workflow    │
└──────────────┘         └───────────────┘         └────────────────┘
       │                        │                         │
  EmailThreadV1           ThreadIntelV1           TaskDTOv1
       │                        │                 DraftDTOv1
       ▼                        ▼                 CalendarSuggestionV1
   Normalized              Interpreted               │
     Data                   Meaning                  ▼
                                                  Actionable
                                                  Decisions
```

**Everything else (AttachmentIntel, ExtractedDeadline, etc.) is INTERNAL to a module.**

---

## Contract Boundaries

| Boundary | Contract | Producer | Consumer |
|----------|----------|----------|----------|
| Ingestion → Intelligence | `EmailThreadV1` | Ingestion | All Intelligence Engines |
| Intelligence → Workflow | `ThreadIntelV1` | Email + Attachment Intelligence | All Workflow Engines |
| Workflow → API/UI | `TaskDTOv1`, `DraftDTOv1`, `CalendarSuggestionV1`, `WaitingForDTOv1` | Workflow Engines | API / Frontend |

---

## How the 5 Product Modules Use Contracts

| Module | Input | Output |
|--------|-------|--------|
| **Email Context Engine** | `EmailThreadV1` | *contributes to* `ThreadIntelV1` |
| **Attachment Intelligence** | `EmailThreadV1` | *contributes to* `ThreadIntelV1` |
| **Smart Reply Engine** | `ThreadIntelV1` | `DraftDTOv1` |
| **Task & Priority Engine** | `ThreadIntelV1` | `TaskDTOv1` |
| **Follow-up Engine** | `ThreadIntelV1` | `WaitingForDTOv1`, `CalendarSuggestionV1` |

> **Key Insight**: Email and Attachment Intelligence engines both produce **parts of** `ThreadIntelV1`. There is ONE coherent intelligence output, not multiple.

---

## Golden Rules

| Rule | Meaning |
|------|---------|
| **Contracts are Data, not Code** | Never pass ORM objects, DB rows, or random dicts |
| **Append-only** | Add new optional fields, never remove or change existing |
| **Single Source** | All contracts live in `backend/contracts/` |
| **Versioned** | `ThreadIntelV1`, `ThreadIntelV2`, etc. |
| **One Intelligence Output** | All intelligence flows through `ThreadIntelV1` |

---

## Boundary Contract 1: `EmailThreadV1`

**Purpose**: Clean, normalized, provider-agnostic email data

```python
class EmailThreadV1(BaseModel):
    thread_id: str
    external_id: str
    subject: str
    participants: List[str]
    messages: List[EmailMessage]     # Internal type
    attachments: List[AttachmentRef] # Internal type
    last_updated: datetime
    provider: str                    # "gmail" | "outlook"
```

**Guarantees**:
- No Gmail/Outlook specific junk
- Messages are ordered chronologically
- Attachments are extracted and stored

---

## Boundary Contract 2: `ThreadIntelV1`

**Purpose**: ALL interpreted meaning from intelligence layer

```python
class ThreadIntelV1(BaseModel):
    thread_id: str
    
    # Core Intelligence
    summary: str
    intent: IntentType
    urgency_score: int               # 0-100
    
    # Extracted Data  
    main_ask: Optional[str]
    decision_needed: Optional[str]
    extracted_deadlines: List[ExtractedDeadline]  # Internal type
    entities: List[ExtractedEntity]               # Internal type
    
    # Attachment Intelligence (EMBEDDED, not separate contract)
    attachment_summaries: List[AttachmentIntel]   # Internal type
    
    # Suggestions
    suggested_action: Optional[str]
    suggested_reply_points: List[str]
    
    # Metadata
    model_version: str
    processed_at: datetime
```

**Why embed AttachmentIntel?**
- Workflow consumes thread-level intelligence, not individual attachments
- Single coherent "understanding" object
- LLM provider can be swapped without breaking workflow

---

## Boundary Contracts 3: Workflow → API/UI

### `TaskDTOv1`
```python
class TaskDTOv1(BaseModel):
    task_id: str
    thread_id: str
    title: str
    priority: PriorityLevel
    priority_score: int
    priority_explanation: str
    effort: EffortLevel
    deadline: Optional[datetime]
    status: TaskStatus
```

### `DraftDTOv1`
```python
class DraftDTOv1(BaseModel):
    draft_id: str
    thread_id: str
    content: str
    tone: ToneType
    placeholders: List[Placeholder]
    has_unresolved_placeholders: bool
```

### `CalendarSuggestionV1`
```python
class CalendarSuggestionV1(BaseModel):
    suggestion_id: str
    thread_id: str
    title: str
    suggested_time: datetime
    confidence: float
    is_accepted: bool  # Always starts False
```

### `WaitingForDTOv1`
```python
class WaitingForDTOv1(BaseModel):
    waiting_id: str
    thread_id: str
    days_waiting: int
    recipient: str
    reminded: bool
```

---

## Internal Types (NOT Boundary Contracts)

These are **embedded within** boundary contracts:

| Type | Embedded In |
|------|-------------|
| `EmailMessage` | `EmailThreadV1.messages` |
| `AttachmentRef` | `EmailThreadV1.attachments` |
| `ExtractedDeadline` | `ThreadIntelV1.extracted_deadlines` |
| `ExtractedEntity` | `ThreadIntelV1.entities` |
| `AttachmentIntel` | `ThreadIntelV1.attachment_summaries` |
| `Placeholder` | `DraftDTOv1.placeholders` |

---

## Team Ownership

| Team | Module | Consumes | Produces |
|------|--------|----------|----------|
| **Team A** | Ingestion | Gmail/Outlook API | `EmailThreadV1` |
| **Team B** | Intelligence | `EmailThreadV1` | `ThreadIntelV1` |
| **Team C** | Workflow | `ThreadIntelV1` | `TaskDTOv1`, `DraftDTOv1`, etc. |
| **Team D** | Frontend | Workflow DTOs | UI |

---

## Enforcement Rules

1. **No module imports another module's internal code**
2. **Only import from `backend/contracts/`**
3. **No passing raw dicts or ORM objects**
4. **Contract changes require Platform Lead approval**

---

## How to Add Features in Future

**Example**: Add "Compliance Analysis"

1. Add `compliance_flags: List[str]` to `ThreadIntelV1` (optional field)
2. Add `ComplianceAlert` type if needed (internal to intelligence)
3. Workflow can now read `thread_intel.compliance_flags`
4. **Nothing else breaks**

---

## Quick Reference

```
Gmail/Outlook API Response
        │
        ▼
   EmailThreadV1  ←── Boundary Contract #1
        │
        ▼
   ThreadIntelV1  ←── Boundary Contract #2 (includes attachment intel)
        │
        ▼
   TaskDTOv1      ←── Boundary Contract #3a
   DraftDTOv1     ←── Boundary Contract #3b
   CalendarSuggestionV1  ←── Boundary Contract #3c
   WaitingForDTOv1       ←── Boundary Contract #3d
        │
        ▼
     Frontend
```
