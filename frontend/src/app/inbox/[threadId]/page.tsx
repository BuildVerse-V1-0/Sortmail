'use client';

import { useState } from 'react';
import { getSenderInfo } from '@/data/mockData';
import type { EmailMessage, EmailThreadV1, ThreadIntelV1, TaskDTOv1, DraftDTOv1, AttachmentRef, PriorityLevel } from '@/types/dashboard';
import {
    ArrowLeft, Sparkles, AlertTriangle, Clock, FileText,
    Calendar, Users, Target, Send, RefreshCw, ChevronDown,
    Paperclip, Brain, Zap, MessageSquare
} from 'lucide-react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import AppShell from '@/components/layout/AppShell';
import { useThreadDetail } from '@/hooks/useThreadDetail';
import { Skeleton } from '@/components/ui/skeleton';

export default function ThreadDetailPage() {
    const params = useParams();
    const threadId = params?.threadId as string;

    const { data, isLoading, error } = useThreadDetail(threadId);

    if (isLoading) {
        return (
            <AppShell title="Loading Thread...">
                <div className="max-w-6xl mx-auto grid lg:grid-cols-3 gap-6 p-6">
                    <div className="lg:col-span-2 space-y-4">
                        <div className="h-12 w-3/4 bg-paper-mid animate-pulse rounded-lg" />
                        <div className="space-y-4">
                            {[1, 2, 3].map(i => (
                                <div key={i} className="h-48 bg-paper-mid animate-pulse rounded-xl" />
                            ))}
                        </div>
                    </div>
                    <div className="space-y-4">
                        <div className="h-64 bg-paper-mid animate-pulse rounded-xl" />
                        <div className="h-32 bg-paper-mid animate-pulse rounded-xl" />
                    </div>
                </div>
            </AppShell>
        );
    }

    if (error || !data || !data.thread) {
        return (
            <AppShell title="Thread Not Found">
                <div className="flex flex-col items-center justify-center h-96 text-muted-foreground">
                    <MessageSquare className="h-12 w-12 mb-4 opacity-30" />
                    <p className="text-lg font-medium">Thread not found</p>
                    <Link href="/inbox">
                        <Button variant="outline" className="mt-4 gap-2">
                            <ArrowLeft className="h-4 w-4" /> Back to Inbox
                        </Button>
                    </Link>
                </div>
            </AppShell>
        );
    }

    const { thread, intel, tasks, draft } = data;

    return (
        <AppShell title={thread.subject} subtitle={`${thread.messages.length} messages`}>
            <div className="max-w-6xl mx-auto">
                {/* Back nav */}
                <Link href="/inbox">
                    <Button variant="ghost" size="sm" className="gap-1.5 mb-4 text-muted-foreground">
                        <ArrowLeft className="h-3.5 w-3.5" /> Inbox
                    </Button>
                </Link>

                <div className="grid lg:grid-cols-3 gap-6">
                    {/* ─── Messages Column ────────────── */}
                    <div className="lg:col-span-2 space-y-4">
                        {/* Thread header */}
                        <div>
                            <h1 className="font-display text-h2 mb-1">{thread.subject}</h1>
                            <div className="flex items-center gap-2 text-sm text-muted-foreground">
                                <Users className="h-3.5 w-3.5" />
                                {thread.participants.join(', ')}
                            </div>
                        </div>

                        {/* Messages */}
                        <ScrollArea className="h-[calc(100vh-320px)]">
                            <div className="space-y-3 pr-4">
                                {thread.messages.map((msg: EmailMessage) => (
                                    <MessageCard key={msg.message_id} message={msg} />
                                ))}

                                {/* Draft composer preview */}
                                {draft && <DraftCard draft={draft} />}
                            </div>
                        </ScrollArea>
                    </div>

                    {/* ─── Intelligence Sidebar ──────── */}
                    <div className="space-y-4">
                        {intel && <IntelPanel intel={intel} />}
                        {tasks.length > 0 && <TasksPanel tasks={tasks} />}
                        {thread.attachments.length > 0 && (
                            <AttachmentsPanel attachments={thread.attachments} intel={intel} />
                        )}
                    </div>
                </div>
            </div>
        </AppShell>
    );
}

// ─── Message Card ────────────────────────────────────────────

function MessageCard({ message }: { message: EmailMessage }) {
    const sender = getSenderInfo(message.from_address);
    const [expanded, setExpanded] = useState(true);

    return (
        <Card className={message.is_from_user ? 'border-l-2 border-l-primary' : ''}>
            <CardHeader className="pb-2 cursor-pointer" onClick={() => setExpanded(!expanded)}>
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold ${message.is_from_user ? 'bg-primary/10 text-primary' : 'bg-paper-deep text-ink-light'}`}>
                            {sender.initials}
                        </div>
                        <div>
                            <p className="text-sm font-semibold">
                                {message.is_from_user ? 'You' : sender.name}
                            </p>
                            <p className="text-xs text-muted-foreground font-mono">
                                {new Date(message.sent_at).toLocaleString('en-US', {
                                    month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
                                })}
                            </p>
                        </div>
                    </div>
                    <ChevronDown className={`h-4 w-4 text-muted-foreground transition-transform ${expanded ? 'rotate-180' : ''}`} />
                </div>
            </CardHeader>
            {expanded && (
                <CardContent className="pt-0">
                    <Separator className="mb-3" />
                    <div className="text-sm leading-relaxed whitespace-pre-line text-ink-mid">
                        {message.body_text}
                    </div>
                </CardContent>
            )}
        </Card>
    );
}

// ─── Intelligence Panel ──────────────────────────────────────

function IntelPanel({ intel }: { intel: ThreadIntelV1 }) {
    const urgencyColor = intel.urgency_score >= 70 ? 'text-danger' : intel.urgency_score >= 40 ? 'text-warning' : 'text-success';

    return (
        <Card className="border-ai/20">
            <CardHeader className="pb-3">
                <div className="flex items-center gap-2">
                    <Brain className="h-4 w-4 text-ai" />
                    <CardTitle className="text-sm font-mono uppercase tracking-wider text-ai">
                        AI Intelligence
                    </CardTitle>
                </div>
            </CardHeader>
            <CardContent className="space-y-4">
                {/* Summary */}
                <div>
                    <p className="text-xs font-mono text-muted-foreground uppercase tracking-wider mb-1">Summary</p>
                    <p className="text-sm leading-relaxed">{intel.summary}</p>
                </div>

                {/* Intent & Urgency */}
                <div className="flex items-center gap-2">
                    <Badge variant="outline" className="capitalize text-xs">
                        {intel.intent.replace('_', ' ')}
                    </Badge>
                    <Badge variant="outline" className={`text-xs ${urgencyColor}`}>
                        <AlertTriangle className="h-3 w-3 mr-1" />
                        Urgency: {intel.urgency_score}/100
                    </Badge>
                </div>

                {/* Main Ask */}
                {intel.main_ask && (
                    <div className="bg-amber-50 border border-amber-200 rounded-md p-3">
                        <p className="text-xs font-mono text-amber-600 uppercase tracking-wider mb-1">Main Ask</p>
                        <p className="text-sm font-medium">{intel.main_ask}</p>
                    </div>
                )}

                {/* Decision Needed */}
                {intel.decision_needed && (
                    <div className="bg-red-50 border border-red-200 rounded-md p-3">
                        <p className="text-xs font-mono text-red-600 uppercase tracking-wider mb-1">Decision Needed</p>
                        <p className="text-sm font-medium">{intel.decision_needed}</p>
                    </div>
                )}

                {/* Deadlines */}
                {intel.extracted_deadlines.length > 0 && (
                    <div>
                        <p className="text-xs font-mono text-muted-foreground uppercase tracking-wider mb-2">Deadlines</p>
                        {intel.extracted_deadlines.map((d, i) => (
                            <div key={i} className="flex items-center gap-2 text-sm">
                                <Calendar className="h-3.5 w-3.5 text-warning" />
                                <span className="font-medium">
                                    {d.normalized ? new Date(d.normalized).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' }) : d.raw_text}
                                </span>
                                <span className="text-xs text-muted-foreground">&ldquo;{d.raw_text}&rdquo;</span>
                            </div>
                        ))}
                    </div>
                )}

                {/* Suggested Action */}
                {intel.suggested_action && (
                    <div className="bg-ai-soft border border-ai/20 rounded-md p-3">
                        <p className="text-xs font-mono text-ai uppercase tracking-wider mb-1">Suggested Action</p>
                        <p className="text-sm">{intel.suggested_action}</p>
                    </div>
                )}

                {/* Reply Points */}
                {intel.suggested_reply_points.length > 0 && (
                    <div>
                        <p className="text-xs font-mono text-muted-foreground uppercase tracking-wider mb-2">Reply Points</p>
                        <ul className="space-y-1">
                            {intel.suggested_reply_points.map((p, i) => (
                                <li key={i} className="flex items-center gap-2 text-sm">
                                    <Zap className="h-3 w-3 text-ai shrink-0" />
                                    {p}
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
            </CardContent>
        </Card>
    );
}

// ─── Tasks Panel ─────────────────────────────────────────────

function TasksPanel({ tasks }: { tasks: TaskDTOv1[] }) {
    const priorityConfig = {
        do_now: { label: 'Do Now', color: 'bg-red-500' },
        do_today: { label: 'Today', color: 'bg-amber-500' },
        can_wait: { label: 'Can Wait', color: 'bg-green-500' },
    };

    return (
        <Card>
            <CardHeader className="pb-3">
                <div className="flex items-center gap-2">
                    <Target className="h-4 w-4 text-accent" />
                    <CardTitle className="text-sm font-mono uppercase tracking-wider text-muted-foreground">
                        Tasks ({tasks.length})
                    </CardTitle>
                </div>
            </CardHeader>
            <CardContent className="space-y-3">
                {tasks.map((task: TaskDTOv1) => {
                    const cfg = priorityConfig[task.priority as PriorityLevel];
                    return (
                        <div key={task.task_id} className="flex items-start gap-2">
                            <div className={`w-1.5 h-1.5 rounded-full ${cfg.color} mt-2 shrink-0`} />
                            <div>
                                <p className="text-sm font-medium">{task.title}</p>
                                <div className="flex items-center gap-1.5 mt-1">
                                    <Badge variant="outline" className="text-[10px] px-1.5 py-0">{cfg.label}</Badge>
                                    <Badge variant="outline" className="text-[10px] px-1.5 py-0">{task.effort}</Badge>
                                </div>
                            </div>
                        </div>
                    );
                })}
            </CardContent>
        </Card>
    );
}

// ─── Attachments Panel ───────────────────────────────────────

function AttachmentsPanel({ attachments, intel }: { attachments: AttachmentRef[]; intel: ThreadIntelV1 | null }) {
    return (
        <Card>
            <CardHeader className="pb-3">
                <div className="flex items-center gap-2">
                    <Paperclip className="h-4 w-4 text-muted-foreground" />
                    <CardTitle className="text-sm font-mono uppercase tracking-wider text-muted-foreground">
                        Attachments ({attachments.length})
                    </CardTitle>
                </div>
            </CardHeader>
            <CardContent className="space-y-3">
                {attachments.map((att: AttachmentRef) => {
                    const attIntel = intel?.attachment_summaries.find(a => a.attachment_id === att.attachment_id);
                    const sizeKB = Math.round(att.size_bytes / 1024);
                    const sizeDisplay = sizeKB >= 1024 ? `${(sizeKB / 1024).toFixed(1)} MB` : `${sizeKB} KB`;

                    return (
                        <div key={att.attachment_id} className="border border-border rounded-md p-3">
                            <div className="flex items-center gap-2">
                                <FileText className="h-4 w-4 text-accent shrink-0" />
                                <div className="min-w-0">
                                    <p className="text-sm font-medium truncate">{att.filename}</p>
                                    <p className="text-xs text-muted-foreground font-mono">{sizeDisplay}</p>
                                </div>
                            </div>
                            {attIntel && (
                                <div className="mt-2 bg-ai-soft/50 rounded p-2">
                                    <p className="text-xs text-ai font-mono mb-1">AI Summary</p>
                                    <p className="text-xs leading-relaxed">{attIntel.summary}</p>
                                    {attIntel.key_points.length > 0 && (
                                        <ul className="mt-1.5 space-y-0.5">
                                            {attIntel.key_points.map((kp, i) => (
                                                <li key={i} className="text-xs text-ink-mid">• {kp}</li>
                                            ))}
                                        </ul>
                                    )}
                                </div>
                            )}
                        </div>
                    );
                })}
            </CardContent>
        </Card>
    );
}

// ─── Draft Card ──────────────────────────────────────────────

function DraftCard({ draft }: { draft: DraftDTOv1 }) {
    return (
        <Card className="border-ai/30 bg-ai-soft/10">
            <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <Sparkles className="h-4 w-4 text-ai" />
                        <CardTitle className="text-sm font-mono uppercase tracking-wider text-ai">
                            AI Draft
                        </CardTitle>
                        <Badge variant="outline" className="text-[10px] capitalize">{draft.tone}</Badge>
                    </div>
                    <div className="flex items-center gap-1.5">
                        <Button variant="ghost" size="sm" className="gap-1 text-xs h-7">
                            <RefreshCw className="h-3 w-3" /> Regenerate
                        </Button>
                        <Button size="sm" className="gap-1 text-xs h-7">
                            <Send className="h-3 w-3" /> Use Draft
                        </Button>
                    </div>
                </div>
            </CardHeader>
            <CardContent>
                <Separator className="mb-3" />
                <div className="text-sm leading-relaxed whitespace-pre-line">
                    {draft.content.split(/(\[.*?\])/).map((part, i) => {
                        if (part.startsWith('[') && part.endsWith(']')) {
                            const placeholder = draft.placeholders.find(p => p.key === part);
                            return (
                                <span key={i} className="bg-yellow-100 border border-yellow-300 rounded px-1 py-0.5 text-yellow-700 cursor-pointer hover:bg-yellow-200 transition-colors" title={placeholder?.description}>
                                    {part}
                                </span>
                            );
                        }
                        return <span key={i}>{part}</span>;
                    })}
                </div>
                {draft.has_unresolved_placeholders && (
                    <div className="mt-3 flex items-center gap-2 text-xs text-amber-600 bg-amber-50 rounded-md p-2">
                        <AlertTriangle className="h-3.5 w-3.5 shrink-0" />
                        {draft.placeholders.length} placeholder{draft.placeholders.length > 1 ? 's' : ''} need{draft.placeholders.length === 1 ? 's' : ''} your input
                    </div>
                )}
            </CardContent>
        </Card>
    );
}
