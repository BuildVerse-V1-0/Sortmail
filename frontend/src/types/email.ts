/**
 * Email Types
 * Matches backend contracts
 */

export type IntentType =
    | "action_required"
    | "fyi"
    | "scheduling"
    | "urgent"
    | "unknown";

export interface ThreadListItem {
    thread_id: string;
    subject: string;
    summary: string;
    intent: IntentType;
    urgency_score: number;
    last_updated: string;
    has_attachments: boolean;
}

export interface ThreadIntel {
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

export interface ExtractedDeadline {
    raw_text: string;
    normalized: string | null;
    confidence: number;
    source: string;
}

export interface ExtractedEntity {
    entity_type: string;
    value: string;
    confidence: number;
}

export interface AttachmentIntel {
    attachment_id: string;
    summary: string;
    key_points: string[];
    document_type: string;
    importance: "high" | "medium" | "low";
}
