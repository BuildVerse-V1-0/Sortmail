/**
 * SortMail Mock Data
 * ==================
 * Shapes match backend contracts exactly (contracts/mocks.py).
 * When the backend is ready, replace these with fetch() calls.
 */

import type {
    EmailThreadV1,
    ThreadIntelV1,
    TaskDTOv1,
    DraftDTOv1,
    WaitingForDTOv1,
    CalendarSuggestionV1,
    ThreadListItem,
    DashboardData,
} from '@/types/dashboard';

// --- Email Threads (Ingestion contract) ----------------------

export const mockThreads: EmailThreadV1[] = [
    {
        thread_id: 'thread-001',
        external_id: '18d5f6a7b8c9d0e1',
        subject: 'Contract Review - Final Terms',
        participants: ['sarah@client.com', 'you@company.com'],
        messages: [
            {
                message_id: 'msg-001-a',
                from_address: 'you@company.com',
                to_addresses: ['sarah@client.com'],
                cc_addresses: [],
                subject: 'Contract Review - Final Terms',
                body_text: "Hi Sarah,\n\nCould you please send over the final contract terms when ready?\n\nBest,\nUser",
                sent_at: '2026-02-14T08:00:00Z',
                is_from_user: true,
            },
            {
                message_id: 'msg-001-b',
                from_address: 'sarah@client.com',
                to_addresses: ['you@company.com'],
                cc_addresses: [],
                subject: 'Re: Contract Review - Final Terms',
                body_text: "Hi,\n\nPlease find the final contract terms attached. We need your approval by Friday EOD.\n\nKey changes from the last version:\n- Payment terms moved to NET 30\n- Liability cap increased to $500K\n\nLet me know if you have any questions.\n\nBest,\nSarah",
                sent_at: '2026-02-16T14:30:00Z',
                is_from_user: false,
            },
        ],
        attachments: [
            {
                attachment_id: 'att-001',
                filename: 'Contract_ClientA_Jan2026.pdf',
                original_filename: 'scan001.pdf',
                mime_type: 'application/pdf',
                storage_path: '/storage/attachments/att-001.pdf',
                size_bytes: 245760,
            },
        ],
        last_updated: '2026-02-16T14:30:00Z',
        provider: 'gmail',
    },
    {
        thread_id: 'thread-002',
        external_id: '18d5f6a7b8c9d0e2',
        subject: 'Q3 Marketing Budget Approval',
        participants: ['mike.chen@company.com', 'you@company.com', 'cfo@company.com'],
        messages: [
            {
                message_id: 'msg-002-a',
                from_address: 'mike.chen@company.com',
                to_addresses: ['you@company.com'],
                cc_addresses: ['cfo@company.com'],
                subject: 'Q3 Marketing Budget Approval',
                body_text: "Hi,\n\nAttached is the Q3 marketing budget proposal. Total spend is $45K, up 12% from Q2.\n\nKey highlights:\n- Increased spend on content ($15K)\n- New influencer program ($8K)\n- Reduced paid search (-$3K)\n\nNeed approval by Wednesday.\n\nMike",
                sent_at: '2026-02-15T09:15:00Z',
                is_from_user: false,
            },
        ],
        attachments: [
            {
                attachment_id: 'att-002',
                filename: 'Q3_Marketing_Budget.xlsx',
                original_filename: 'budget_q3.xlsx',
                mime_type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                storage_path: '/storage/attachments/att-002.xlsx',
                size_bytes: 89600,
            },
        ],
        last_updated: '2026-02-15T09:15:00Z',
        provider: 'gmail',
    },
    {
        thread_id: 'thread-003',
        external_id: '18d5f6a7b8c9d0e3',
        subject: 'Team standup notes - Feb 14',
        participants: ['alex@company.com', 'you@company.com', 'team@company.com'],
        messages: [
            {
                message_id: 'msg-003-a',
                from_address: 'alex@company.com',
                to_addresses: ['team@company.com'],
                cc_addresses: [],
                subject: 'Team standup notes - Feb 14',
                body_text: "Hi team,\n\nHere are the standup notes:\n- Sprint velocity is on track\n- Backend API v2 deployed to staging\n- Frontend redesign merged to main\n\nNo blockers.\n\nAlex",
                sent_at: '2026-02-14T10:30:00Z',
                is_from_user: false,
            },
        ],
        attachments: [],
        last_updated: '2026-02-14T10:30:00Z',
        provider: 'gmail',
    },
    {
        thread_id: 'thread-004',
        external_id: '18d5f6a7b8c9d0e4',
        subject: 'Urgent: Server downtime alert',
        participants: ['devops@company.com', 'you@company.com'],
        messages: [
            {
                message_id: 'msg-004-a',
                from_address: 'devops@company.com',
                to_addresses: ['you@company.com'],
                cc_addresses: [],
                subject: 'Urgent: Server downtime alert',
                body_text: "ALERT: Production server response time has exceeded 2s threshold.\n\nAffected services:\n- User authentication API\n- Payment processing\n\nInvestigation in progress. ETA for fix: 2 hours.\n\n-- DevOps Bot",
                sent_at: '2026-02-16T16:00:00Z',
                is_from_user: false,
            },
        ],
        attachments: [],
        last_updated: '2026-02-16T16:00:00Z',
        provider: 'outlook',
    },
    {
        thread_id: 'thread-005',
        external_id: '18d5f6a7b8c9d0e5',
        subject: 'Partnership proposal - StreamlineAI',
        participants: ['jessica@streamlineai.com', 'you@company.com'],
        messages: [
            {
                message_id: 'msg-005-a',
                from_address: 'jessica@streamlineai.com',
                to_addresses: ['you@company.com'],
                cc_addresses: [],
                subject: 'Partnership proposal - StreamlineAI',
                body_text: "Hi,\n\nWe would love to explore a partnership between our companies. StreamlineAI specializes in workflow automation and we think there is strong synergy.\n\nWould you be open to a 30-min call next Tuesday?\n\nBest,\nJessica Park\nHead of Partnerships, StreamlineAI",
                sent_at: '2026-02-13T11:20:00Z',
                is_from_user: false,
            },
        ],
        attachments: [
            {
                attachment_id: 'att-005',
                filename: 'StreamlineAI_Partnership_Deck.pdf',
                original_filename: 'partnership_deck.pdf',
                mime_type: 'application/pdf',
                storage_path: '/storage/attachments/att-005.pdf',
                size_bytes: 1572864,
            },
        ],
        last_updated: '2026-02-13T11:20:00Z',
        provider: 'outlook',
    },
];

// --- Thread Intelligence (Intelligence contract) -------------

export const mockThreadIntel: Record<string, ThreadIntelV1> = {
    'thread-001': {
        thread_id: 'thread-001',
        summary: 'Sarah sent the final contract terms and needs approval by Friday EOD. Key changes include NET 30 payment terms and $500K liability cap.',
        intent: 'action_required',
        urgency_score: 75,
        main_ask: 'Approve or request changes to contract',
        decision_needed: 'Contract approval',
        extracted_deadlines: [
            {
                raw_text: 'by Friday EOD',
                normalized: '2026-02-21T17:00:00Z',
                confidence: 0.92,
                source: 'msg-001-b',
            },
        ],
        entities: [
            { entity_type: 'amount', value: '$500K', confidence: 0.95 },
            { entity_type: 'person', value: 'Sarah', confidence: 0.99 },
        ],
        attachment_summaries: [
            {
                attachment_id: 'att-001',
                summary: 'Master Services Agreement between Company and ClientA. Covers 12-month engagement with defined deliverables and payment terms.',
                key_points: [
                    '12-month contract term',
                    'NET 30 payment terms',
                    '$500K liability cap',
                    'Includes IP assignment clause',
                ],
                document_type: 'contract',
                importance: 'high',
            },
        ],
        suggested_action: 'Review attached contract and respond with approval or concerns',
        suggested_reply_points: [
            'Confirm receipt of contract',
            'Acknowledge the updated terms',
            'State your decision',
        ],
        model_version: 'gemini-1.5-pro',
        processed_at: '2026-02-16T14:35:00Z',
    },
    'thread-002': {
        thread_id: 'thread-002',
        summary: 'Mike is requesting approval for the Q3 marketing budget. Total spend is $45K, a 12% increase from Q2. He needs a decision by Wednesday.',
        intent: 'action_required',
        urgency_score: 60,
        main_ask: 'Approve or adjust Q3 marketing budget',
        decision_needed: 'Budget approval',
        extracted_deadlines: [
            {
                raw_text: 'by Wednesday',
                normalized: '2026-02-19T17:00:00Z',
                confidence: 0.88,
                source: 'msg-002-a',
            },
        ],
        entities: [
            { entity_type: 'amount', value: '$45K', confidence: 0.96 },
            { entity_type: 'person', value: 'Mike Chen', confidence: 0.97 },
        ],
        attachment_summaries: [
            {
                attachment_id: 'att-002',
                summary: 'Q3 Marketing Budget spreadsheet with line-by-line breakdown. Shows 12% increase driven by content and influencer programs.',
                key_points: ['Content: $15K', 'Influencer: $8K', 'Paid search reduced by $3K'],
                document_type: 'budget',
                importance: 'high',
            },
        ],
        suggested_action: 'Review budget spreadsheet and approve or request adjustments',
        suggested_reply_points: [
            'Acknowledge budget proposal',
            'Comment on content spend increase',
            'Approve or flag concerns',
        ],
        model_version: 'gemini-1.5-pro',
        processed_at: '2026-02-15T10:00:00Z',
    },
    'thread-004': {
        thread_id: 'thread-004',
        summary: 'Production server alert - response times exceeding 2s threshold. Auth API and payments affected. Fix ETA is 2 hours.',
        intent: 'urgent',
        urgency_score: 95,
        main_ask: null,
        decision_needed: null,
        extracted_deadlines: [],
        entities: [
            { entity_type: 'service', value: 'User authentication API', confidence: 0.98 },
            { entity_type: 'service', value: 'Payment processing', confidence: 0.97 },
        ],
        attachment_summaries: [],
        suggested_action: 'Monitor the situation and coordinate with DevOps',
        suggested_reply_points: [],
        model_version: 'gemini-1.5-pro',
        processed_at: '2026-02-16T16:05:00Z',
    },
};

// --- Thread List Items (API route response) ------------------

export const mockThreadListItems: ThreadListItem[] = mockThreads.map(t => ({
    thread_id: t.thread_id,
    subject: t.subject,
    summary: mockThreadIntel[t.thread_id]?.summary ?? (t.messages[0]?.body_text || '').slice(0, 100) + '...',
    intent: mockThreadIntel[t.thread_id]?.intent ?? 'unknown',
    urgency_score: mockThreadIntel[t.thread_id]?.urgency_score ?? 0,
    last_updated: t.last_updated,
    has_attachments: t.attachments.length > 0,
    days_waiting: 0,
    is_read: false,
}));

// --- Tasks (Workflow contract) -------------------------------

export const mockTasks: TaskDTOv1[] = [
    {
        task_id: 'task-001',
        thread_id: 'thread-001',
        user_id: 'user-001',
        title: 'Reply to Sarah - Contract Review',
        description: 'Review contract terms and respond with approval or concerns',
        task_type: 'reply',
        priority: 'do_now',
        priority_score: 85,
        priority_explanation: 'High: Key client + deadline Friday + contract value significant',
        effort: 'quick',
        deadline: '2026-02-21T17:00:00Z',
        deadline_source: 'Email: by Friday EOD',
        status: 'pending',
        created_at: '2026-02-16T14:00:00Z',
        updated_at: '2026-02-16T14:00:00Z',
    },
    {
        task_id: 'task-002',
        thread_id: 'thread-002',
        user_id: 'user-001',
        title: 'Approve Q3 Marketing Budget',
        description: 'Review $45K budget proposal and approve or flag concerns',
        task_type: 'review',
        priority: 'do_today',
        priority_score: 65,
        priority_explanation: 'Medium: Internal request, deadline Wednesday, budget decision',
        effort: 'quick',
        deadline: '2026-02-19T17:00:00Z',
        deadline_source: 'Email: by Wednesday',
        status: 'pending',
        created_at: '2026-02-15T10:00:00Z',
        updated_at: '2026-02-15T10:00:00Z',
    },
    {
        task_id: 'task-003',
        thread_id: 'thread-005',
        user_id: 'user-001',
        title: 'Schedule call with StreamlineAI',
        description: 'Respond to partnership inquiry and schedule 30-min call for Tuesday',
        task_type: 'schedule',
        priority: 'can_wait',
        priority_score: 35,
        priority_explanation: 'Low: External partnership, no hard deadline, exploratory',
        effort: 'quick',
        deadline: null,
        deadline_source: null,
        status: 'pending',
        created_at: '2026-02-13T12:00:00Z',
        updated_at: '2026-02-13T12:00:00Z',
    },
    {
        task_id: 'task-004',
        thread_id: 'thread-004',
        user_id: 'user-001',
        title: 'Follow up on server downtime',
        description: 'Check with DevOps for post-mortem after resolution',
        task_type: 'followup',
        priority: 'do_now',
        priority_score: 90,
        priority_explanation: 'Critical: Production incident affecting payments',
        effort: 'deep_work',
        deadline: '2026-02-16T18:00:00Z',
        deadline_source: 'ETA: 2 hours from alert',
        status: 'in_progress',
        created_at: '2026-02-16T16:05:00Z',
        updated_at: '2026-02-16T16:10:00Z',
    },
];

// --- Drafts (Workflow contract) ------------------------------

export const mockDraft: DraftDTOv1 = {
    draft_id: 'draft-001',
    thread_id: 'thread-001',
    user_id: 'user-001',
    content: "Hi Sarah,\n\nThank you for sending over the final contract. I have reviewed the updated terms including the NET 30 payment schedule and $500K liability cap.\n\n[Confirm approval OR request specific changes]\n\nI will have this finalized by Friday EOD as requested.\n\nBest regards",
    tone: 'normal',
    placeholders: [
        {
            key: '[Confirm approval OR request specific changes]',
            description: 'State your decision on the contract',
            suggested_value: 'Everything looks good - approved',
        },
    ],
    has_unresolved_placeholders: true,
    references_attachments: true,
    references_deadlines: true,
    created_at: '2026-02-16T14:30:00Z',
    model_version: 'gemini-1.5-pro',
};

// --- Waiting For (Workflow contract) -------------------------

export const mockWaitingFor: WaitingForDTOv1[] = [
    {
        waiting_id: 'wait-001',
        thread_id: 'thread-other-001',
        user_id: 'user-001',
        last_sent_at: '2026-02-11T10:00:00Z',
        days_waiting: 5,
        recipient: 'john@bigclient.com',
        reminded: false,
        last_reminded_at: null,
        thread_subject: 'Proposal Follow-up',
        thread_summary: 'Sent proposal for Q2 project, awaiting feedback on pricing',
    },
    {
        waiting_id: 'wait-002',
        thread_id: 'thread-other-002',
        user_id: 'user-001',
        last_sent_at: '2026-02-14T14:00:00Z',
        days_waiting: 2,
        recipient: 'lisa@vendor.com',
        reminded: false,
        last_reminded_at: null,
        thread_subject: 'Invoice #4521 Clarification',
        thread_summary: 'Asked for updated line items on service charges',
    },
];

// --- Calendar Suggestions (Workflow contract) ----------------

export const mockCalendarSuggestions: CalendarSuggestionV1[] = [
    {
        suggestion_id: 'cal-001',
        thread_id: 'thread-001',
        user_id: 'user-001',
        title: 'Contract review deadline',
        suggested_time: '2026-02-21T15:00:00Z',
        duration_minutes: 30,
        location: null,
        extracted_from: 'by Friday EOD',
        confidence: 0.85,
        is_accepted: false,
        is_dismissed: false,
        created_at: '2026-02-16T14:30:00Z',
    },
    {
        suggestion_id: 'cal-002',
        thread_id: 'thread-005',
        user_id: 'user-001',
        title: 'Call with StreamlineAI (Jessica)',
        suggested_time: '2026-02-18T14:00:00Z',
        duration_minutes: 30,
        location: null,
        extracted_from: 'call next Tuesday',
        confidence: 0.80,
        is_accepted: false,
        is_dismissed: false,
        created_at: '2026-02-13T12:00:00Z',
    },
];

// --- Dashboard Aggregate -------------------------------------

export const mockDashboard: DashboardData = {
    briefing: {
        summary: 'You have 2 high-priority items today: a contract from Sarah Chen needing approval by Friday, and a production server incident affecting payments. Mike Chen also needs your Q3 budget sign-off by Wednesday.',
        suggested_actions: [
            'Review and approve contract from Sarah',
            'Monitor server incident resolution',
            'Sign off on Q3 marketing budget',
        ],
        urgent_count: 2,
        date: '2026-02-16',
    },
    stats: {
        unread: 12,
        urgent: 2,
        tasks_due: 4,
        awaiting_reply: 2,
        unread_delta: '+3 from yesterday',
    },
    recent_threads: mockThreadListItems.slice(0, 5),
    priority_tasks: mockTasks.filter(t => t.status !== 'completed').sort((a, b) => b.priority_score - a.priority_score).slice(0, 5),
};

// --- Helper: Extract sender display info ---------------------

export function getSenderInfo(email: string): { name: string; initials: string } {
    const name = email.split('@')[0]
        .split('.')
        .map(s => s.charAt(0).toUpperCase() + s.slice(1))
        .join(' ');
    const parts = name.split(' ');
    const initials = parts.length >= 2
        ? parts[0][0] + parts[1][0]
        : parts[0].slice(0, 2).toUpperCase();
    return { name, initials };
}
