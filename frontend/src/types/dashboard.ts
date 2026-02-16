
export enum Urgency {
    HIGH = 'High',
    MEDIUM = 'Medium',
    LOW = 'Low'
}

export enum View {
    DASHBOARD = 'Dashboard',
    PRIORITY = 'Priority List',
    STATS = 'Quick Stats',
    WAITING = 'Waiting For'
}

export interface Attachment {
    id: string;
    name: string;
    type: string;
    size: string;
    url?: string;
    aiSummary?: string;
}

export interface Email {
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
    attachments?: Attachment[];
    aiTldr?: string;
}

export interface WaitingItem {
    id: string;
    recipient: string;
    subject: string;
    sentDate: string;
    daysPending: number;
    avatar: string;
}

export interface Task {
    id: string;
    title: string;
    sourceEmailId: string;
    status: 'todo' | 'in-progress' | 'done';
}

export interface AIAnalysisResult {
    summary: string[];
    actionItems: string[];
    suggestedReply?: string;
}
