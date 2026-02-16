# SortMail — System Architecture

> AI Intelligence Layer for Gmail & Outlook

---

## High-Level Architecture

```mermaid
graph TB
    subgraph External["External Services"]
        Gmail["Gmail API"]
        Outlook["Outlook API"]
        LLM["LLM Provider (Gemini/OpenAI)"]
        Storage["Cloud Storage"]
    end

    subgraph Ingestion["Ingestion Layer"]
        OAuth["OAuth Handler"]
        EmailFetcher["Email Fetcher"]
        AttachmentExtractor["Attachment Extractor"]
    end

    subgraph Intelligence["Intelligence Engines"]
        EmailIntel["Email Intelligence Engine"]
        AttachIntel["Attachment Intelligence Engine"]
        WorkflowEngine["Workflow & Action Engine"]
    end

    subgraph Core["Core Services"]
        API["REST API Layer"]
        TaskMgr["Task Manager"]
        DraftGen["Draft Generator"]
        ReminderSvc["Reminder Service"]
        DeadlineExtractor["Deadline Extractor"]
    end

    subgraph Data["Data Layer"]
        Postgres["PostgreSQL"]
        VectorDB["Vector Store (Chroma)"]
        Cache["Redis Cache"]
    end

    subgraph Frontend["Web Frontend"]
        NextJS["Next.js App"]
        Dashboard["Dashboard"]
        ThreadView["Thread View"]
        TaskView["Task View"]
    end

    Gmail --> OAuth
    Outlook --> OAuth
    OAuth --> EmailFetcher
    EmailFetcher --> AttachmentExtractor
    
    AttachmentExtractor --> EmailIntel
    EmailIntel --> AttachIntel
    AttachIntel --> WorkflowEngine
    
    WorkflowEngine --> TaskMgr
    WorkflowEngine --> DraftGen
    WorkflowEngine --> ReminderSvc
    WorkflowEngine --> DeadlineExtractor
    
    EmailIntel --> LLM
    AttachIntel --> LLM
    DraftGen --> LLM
    
    TaskMgr --> Postgres
    EmailIntel --> Postgres
    AttachIntel --> VectorDB
    
    API --> NextJS
    DraftGen --> Gmail
    DraftGen --> Outlook
```

---

## Engine Architecture

### 1. Email Intelligence Engine

```mermaid
graph LR
    subgraph Input
        RawEmail["Raw Email"]
        Thread["Thread Context"]
    end

    subgraph Processing
        Parser["Email Parser"]
        IntentClassifier["Intent Classifier"]
        UrgencyDetector["Urgency Detector"]
        EntityExtractor["Entity Extractor"]
    end

    subgraph Output
        Summary["Executive Summary"]
        Intent["Intent Label"]
        Urgency["Urgency Score"]
        Entities["Named Entities"]
    end

    RawEmail --> Parser
    Thread --> Parser
    Parser --> IntentClassifier
    Parser --> UrgencyDetector
    Parser --> EntityExtractor
    IntentClassifier --> Intent
    UrgencyDetector --> Urgency
    EntityExtractor --> Entities
    Parser --> Summary
```

**Responsibilities:**
- Parse email threads into structured data
- Classify intent: `ACTION_REQUIRED` | `FYI` | `SCHEDULING` | `URGENT`
- Extract urgency signals and deadlines
- Generate executive-style briefings

---

### 2. Attachment Intelligence Engine

```mermaid
graph LR
    subgraph Input
        Attachment["Attachment File"]
        EmailContext["Email Context"]
    end

    subgraph Processing
        FileDetector["File Type Detector"]
        TextExtractor["Text Extractor"]
        Summarizer["Document Summarizer"]
        Indexer["Vector Indexer"]
    end

    subgraph Output
        DocSummary["Document Summary"]
        KeyPoints["Key Points"]
        VectorIndex["Vector Embeddings"]
        SmartName["Contextual Filename"]
    end

    Attachment --> FileDetector
    FileDetector --> TextExtractor
    TextExtractor --> Summarizer
    EmailContext --> Summarizer
    Summarizer --> DocSummary
    Summarizer --> KeyPoints
    TextExtractor --> Indexer
    Indexer --> VectorIndex
    EmailContext --> SmartName
```

**Supported Formats (v1):** PDF, DOCX, PPTX

**Responsibilities:**
- Extract text from documents
- Generate summaries and key points
- Create contextual filenames
- Index for RAG retrieval

---

### 3. Workflow & Action Engine

```mermaid
graph TB
    subgraph Inputs
        EmailData["Email Intelligence"]
        AttachData["Attachment Intelligence"]
        UserPrefs["User Preferences"]
    end

    subgraph Core
        TaskGen["Task Generator"]
        PriorityCalc["Priority Calculator"]
        DeadlineParser["Deadline Parser"]
        DraftEngine["Draft Engine"]
        FollowUpTracker["Follow-Up Tracker"]
    end

    subgraph Outputs
        Tasks["Prioritized Tasks"]
        Drafts["Draft Replies"]
        Reminders["Reminders"]
        CalendarSuggestions["Calendar Suggestions"]
    end

    EmailData --> TaskGen
    AttachData --> TaskGen
    UserPrefs --> PriorityCalc
    TaskGen --> PriorityCalc
    EmailData --> DeadlineParser
    DeadlineParser --> PriorityCalc
    PriorityCalc --> Tasks
    
    EmailData --> DraftEngine
    AttachData --> DraftEngine
    DeadlineParser --> DraftEngine
    DraftEngine --> Drafts
    
    EmailData --> FollowUpTracker
    FollowUpTracker --> Reminders
    DeadlineParser --> CalendarSuggestions
```

**Responsibilities:**
- Convert emails → actionable tasks
- Score priority with explainability
- Extract deadlines and suggest calendar events
- Generate contextual draft replies
- Track follow-ups and waiting threads

---

## Data Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant Ingestion
    participant EmailIntel
    participant AttachIntel
    participant Workflow
    participant DB
    participant LLM

    User->>Frontend: Connect Gmail
    Frontend->>API: OAuth Request
    API->>Ingestion: Fetch Emails
    Ingestion->>DB: Store Raw Emails
    
    Ingestion->>EmailIntel: Process Thread
    EmailIntel->>LLM: Summarize + Classify
    LLM-->>EmailIntel: Summary + Intent
    EmailIntel->>DB: Store Intelligence
    
    Ingestion->>AttachIntel: Process Attachments
    AttachIntel->>LLM: Extract + Summarize
    LLM-->>AttachIntel: Doc Summary
    AttachIntel->>DB: Store + Index
    
    EmailIntel->>Workflow: Generate Tasks
    Workflow->>DB: Store Tasks
    
    User->>Frontend: View Dashboard
    Frontend->>API: Get Priority List
    API->>DB: Query Tasks
    DB-->>Frontend: Ranked Tasks
    
    User->>Frontend: Generate Draft
    Frontend->>API: Request Draft
    API->>Workflow: Generate Draft
    Workflow->>LLM: Create Reply
    LLM-->>Frontend: Draft Response
```

---

## Tech Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| **Backend** | Python (FastAPI) | Rapid development, LLM ecosystem |
| **Frontend** | Next.js 14 | SSR, App Router, great DX |
| **Database** | PostgreSQL | Reliable, JSONB support |
| **Vector DB** | Chroma | Simple, embedded, good for MVP |
| **Cache** | Redis | Sessions, rate limiting |
| **Auth** | OAuth 2.0 | Gmail/Outlook native |
| **LLM** | Gemini / OpenAI | Summarization, classification |
| **Styling** | Tailwind + shadcn/ui | Fast, consistent UI |
| **Deployment** | Docker + Railway/Fly.io | Simple, scalable |

---

## API Contracts

### Core Endpoints

```
POST   /api/auth/google          # OAuth flow
POST   /api/auth/outlook         # OAuth flow
GET    /api/emails               # List emails
GET    /api/emails/:id           # Get email details
GET    /api/threads/:id          # Get thread with summary
GET    /api/tasks                # Get prioritized tasks
PATCH  /api/tasks/:id            # Update task status
POST   /api/drafts               # Generate draft reply
GET    /api/reminders            # Get pending reminders
POST   /api/calendar/suggest     # Suggest calendar event
```

---

## Security Considerations

| Concern | Mitigation |
|---------|------------|
| Token Storage | Encrypted at rest, short-lived access tokens |
| Data Privacy | User data isolated, no cross-tenant access |
| LLM Data | No training on user data, minimal context |
| API Security | Rate limiting, JWT auth, CORS |
| Attachments | Virus scan before processing |
