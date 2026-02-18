/**
 * SortMail Type Definitions
 * =========================
 * Mirrors backend contracts (contracts/__init__.py) exactly.
 * When backend is ready, just swap mock data for fetch() calls.
 *
 * Backend contracts:
 *   EmailThreadV1   → ingestion.py
 *   ThreadIntelV1   → intelligence.py
 *   TaskDTOv1       → workflow.py
 *   DraftDTOv1      → workflow.py
 *   WaitingForDTOv1 → workflow.py
 *   CalendarSuggestionV1 → workflow.py
 */

// ─── Enums (match backend exactly) ───────────────────────────

export type IntentType = 'action_required' | 'fyi' | 'scheduling' | 'urgent' | 'unknown';
export type PriorityLevel = 'do_now' | 'do_today' | 'can_wait';
export type EffortLevel = 'quick' | 'deep_work';
export type TaskType = 'reply' | 'review' | 'schedule' | 'followup' | 'other';
export type TaskStatus = 'pending' | 'in_progress' | 'completed' | 'dismissed';
export type ToneType = 'brief' | 'normal' | 'formal';

export type FilterTab = 'all' | 'urgent' | 'action_required' | 'fyi';

// ─── Ingestion Contracts ─────────────────────────────────────

/** Mirrors backend: contracts/ingestion.py → AttachmentRef */
export interface AttachmentRef {
    attachment_id: string;
    filename: string;
    original_filename: string;
    mime_type: string;
    storage_path: string;
    size_bytes: number;
}

/** Mirrors backend: contracts/ingestion.py → EmailMessage */
export interface EmailMessage {
    message_id: string;
    from_address: string;
    to_addresses: string[];
    cc_addresses: string[];
    subject: string;
    body_text: string;
    sent_at: string;
    is_from_user: boolean;
}

/** Mirrors backend: contracts/ingestion.py → EmailThreadV1 */
export interface EmailThreadV1 {
    thread_id: string;
    external_id: string;
    subject: string;
    participants: string[];
    messages: EmailMessage[];
    attachments: AttachmentRef[];
    last_updated: string;
    provider: 'gmail' | 'outlook';
}

// ─── Intelligence Contracts ──────────────────────────────────

/** Mirrors backend: contracts/intelligence.py → ExtractedDeadline */
export interface ExtractedDeadline {
    raw_text: string;
    normalized: string | null;
    confidence: number;
    source: string;
}

/** Mirrors backend: contracts/intelligence.py → ExtractedEntity */
export interface ExtractedEntity {
    entity_type: string;
    value: string;
    confidence: number;
}

/** Mirrors backend: contracts/intelligence.py → AttachmentIntel */
export interface AttachmentIntel {
    attachment_id: string;
    summary: string;
    key_points: string[];
    document_type: string;
    importance: string;
}

/** Mirrors backend: contracts/intelligence.py → ThreadIntelV1 */
export interface ThreadIntelV1 {
    thread_id: string;
    summary: string;
    intent: IntentType;
    urgency_score: number;
    main_ask: string | null;
    decision_needed: string | null;
    extracted_deadlines: ExtractedDeadline[];
    entities: ExtractedEntity[];
    attachment_summaries: AttachmentIntel[];
    suggested_action: string | null;
    suggested_reply_points: string[];
    model_version: string;
    processed_at: string;
}

// ─── Workflow Contracts ──────────────────────────────────────

/** Mirrors backend: contracts/workflow.py → Placeholder */
export interface Placeholder {
    key: string;
    description: string;
    suggested_value: string | null;
}

/** Mirrors backend: contracts/workflow.py → TaskDTOv1 */
export interface TaskDTOv1 {
    task_id: string;
    thread_id: string;
    user_id: string;
    title: string;
    description: string | null;
    task_type: TaskType;
    priority: PriorityLevel;
    priority_score: number;
    priority_explanation: string;
    effort: EffortLevel;
    deadline: string | null;
    deadline_source: string | null;
    status: TaskStatus;
    created_at: string;
    updated_at: string;
}

/** Mirrors backend: contracts/workflow.py → DraftDTOv1 */
export interface DraftDTOv1 {
    draft_id: string;
    thread_id: string;
    user_id: string;
    content: string;
    tone: ToneType;
    placeholders: Placeholder[];
    has_unresolved_placeholders: boolean;
    references_attachments: boolean;
    references_deadlines: boolean;
    created_at: string;
    model_version: string;
}

/** Mirrors backend: contracts/workflow.py → CalendarSuggestionV1 */
export interface CalendarSuggestionV1 {
    suggestion_id: string;
    thread_id: string;
    user_id: string;
    title: string;
    suggested_time: string;
    duration_minutes: number;
    location: string | null;
    extracted_from: string;
    confidence: number;
    is_accepted: boolean;
    is_dismissed: boolean;
    created_at: string;
}

/** Mirrors backend: contracts/workflow.py → WaitingForDTOv1 */
export interface WaitingForDTOv1 {
    waiting_id: string;
    thread_id: string;
    user_id: string;
    last_sent_at: string;
    days_waiting: number;
    recipient: string;
    reminded: boolean;
    last_reminded_at: string | null;
    thread_subject: string;
    thread_summary: string;
}

// ─── API Route Response Types ────────────────────────────────

/** Mirrors backend: api/routes/threads.py → ThreadListItem */
export interface ThreadListItem {
    thread_id: string;
    subject: string;
    summary: string;
    intent: string;
    urgency_score: number;
    last_updated: string;
    has_attachments: boolean;
    days_waiting: number;
    is_read: boolean;
}

/** Dashboard aggregate (to be added as backend endpoint) */
export interface DashboardData {
    briefing: {
        summary: string;
        suggested_actions: string[];
        urgent_count: number;
        date: string;
    };
    stats: {
        unread: number;
        urgent: number;
        tasks_due: number;
        awaiting_reply: number;
        unread_delta: string;
    };
    recent_threads: ThreadListItem[];
    priority_tasks: TaskDTOv1[];
}

// ─── Frontend-Only Helpers ───────────────────────────────────

/** Sender display info derived from EmailMessage */
export interface SenderInfo {
    name: string;
    email: string;
    initials: string;
}

// ─── Legacy Compat (for old dashboard components) ────────────

export enum View {
    DASHBOARD = 'Dashboard',
    PRIORITY = 'Priority',
    STATS = 'Stats',
    WAITING = 'Waiting',
    INBOX = 'Inbox',
}

export enum Urgency {
    HIGH = 'High',
    MEDIUM = 'Medium',
    LOW = 'Low',
}

export interface LegacyEmail {
    id: string;
    sender: string;
    avatar: string;
    subject: string;
    preview: string;
    body: string;
    timestamp: string;
    urgency: Urgency;
    isRead: boolean;
    hasAttachment?: boolean;
    attachments?: Array<{ id: string; name: string; type: string; size: string }>;
    aiTldr?: string;
}

export interface LegacyTask {
    id: string;
    title: string;
    description: string;
    sourceEmailId?: string;
    status?: string;
    priority?: PriorityLevel;
    isAIGenerated?: boolean;
    createdAt?: string;
}

export interface WaitingItem {
    id: string;
    recipient: string;
    subject: string;
    sentDate: string;
    daysPending: number;
    avatar: string;
}

export interface LegacyAttachment {
    id: string;
    name: string;
    type: string;
    size: string;
    aiSummary?: string;
}

// ─── Legacy Types (used by Phase 1 components) ───────────────
// These keep old components compiling. New pages use API-shaped types above.

export type Priority = 'urgent' | 'high' | 'medium' | 'low';

export interface Email {
    id: string;
    threadId: string;
    sender: { name: string; email: string; initials: string };
    subject: string;
    snippet: string;
    receivedAt: string;
    priority: Priority;
    isRead: boolean;
    aiReady: boolean;
    attachments: LegacyAttachment[];
}

export interface Message {
    id: string;
    sender: { name: string; email: string; initials: string };
    bodyText: string;
    timestamp: string;
    isFromUser: boolean;
    attachments?: Array<{
        id: string;
        filename: string;
        sizeBytes: number;
        aiSummary?: string;
        keyPoints?: string[];
    }>;
}

export interface QuickStats {
    unread: number;
    urgent: number;
    tasksDue: number;
    awaitingReply: number;
    unreadDelta?: string;
}

export interface Task {
    id: string;
    title: string;
    priority: Priority;
    status: 'todo' | 'in_progress' | 'done';
    dueDate?: string;
    sourceSender?: string;
    isAIGenerated?: boolean;
}

export interface Briefing {
    summary: string;
    suggestedActions: string[];
    date: string;
}

export interface ThreadDetail {
    thread: {
        id: string;
        subject: string;
        participants: string[];
    };
    messages: Message[];
    intel: {
        summary: string;
        intent: string;
        urgencyScore: number;
        mainAsk: string;
        actionItems: string[];
    };
    attachments: Array<{
        id: string;
        filename: string;
        aiSummary?: string;
        keyPoints?: string[];
    }>;
}
