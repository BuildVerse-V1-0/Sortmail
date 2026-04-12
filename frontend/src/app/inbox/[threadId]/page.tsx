'use client';

import { useEffect, useState } from 'react';
import type { EmailMessage, DraftDTOv1, AttachmentRef } from '@/types/dashboard';
import {
    ArrowLeft, Sparkles, AlertTriangle, FileText,
    Send, RefreshCw, ChevronDown, X, Archive, Trash2
} from 'lucide-react';
import { useParams } from 'next/navigation';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { useThreadDetail } from '@/hooks/useThreadDetail';
import { useCreateTask } from '@/hooks/useTasks';

export default function ThreadDetailPage() {
    const params = useParams();
    const threadId = params?.threadId as string;
    const { data, isLoading, error } = useThreadDetail(threadId);
    const createTask = useCreateTask();
    const [mounted, setMounted] = useState(false);
    const [creatingMessageId, setCreatingMessageId] = useState<string | null>(null);

    useEffect(() => {
        setMounted(true);
    }, []);

    if (isLoading) {
        return <ThreadPageShell title="Opening mail..." subtitle="Loading thread details">
            <LoadingState />
        </ThreadPageShell>;
    }

    if (error || !data || !data.thread) {
        return <ThreadPageShell title="Thread unavailable" subtitle="The requested message could not be loaded">
            <ErrorState onBack={() => window.history.back()} />
        </ThreadPageShell>;
    }

    const { thread, intel, tasks, draft } = data;
    const taskItems = Array.isArray(tasks) ? tasks : [];
    const attachmentItems = thread.attachments ?? [];

    const handleCreateTaskFromMessage = async (message: EmailMessage) => {
        try {
            setCreatingMessageId(message.message_id);
            const bodySnippet = (message.body_text || '').replace(/\s+/g, ' ').trim().slice(0, 220);
            await createTask.mutateAsync({
                title: message.subject ? `Follow up: ${message.subject}` : `Follow up from ${getSenderInfo(message.from_address).name}`,
                description: bodySnippet || `Created from message ${message.message_id}`,
                thread_id: thread.thread_id,
                source_email_id: message.message_id,
                source_type: 'email_converted',
                task_type: 'REPLY',
                priority: 'DO_TODAY',
                status: 'PENDING',
            });
        } finally {
            setCreatingMessageId(null);
        }
    };

    return (
        <ThreadPageShell title={thread.subject} subtitle={getSenderInfo(thread.messages[0]?.from_address || '').email}>
            <div className="max-w-[1280px] mx-auto px-4 md:px-6 pb-10 lg:grid lg:grid-cols-[minmax(0,1fr)_320px] lg:gap-6">
                <div className="space-y-6">
                    <div className="flex items-center justify-between gap-4">
                        <Button variant="ghost" className="gap-2 text-on-surface-variant hover:text-on-surface" onClick={() => window.history.back()}>
                            <ArrowLeft className="h-4 w-4" /> Back to inbox
                        </Button>
                        <div className="flex gap-2">
                            <Button variant="outline" className="gap-2" onClick={() => window.history.back()}>
                                <Archive className="h-4 w-4" /> Archive
                            </Button>
                            <Button variant="outline" className="gap-2 border-danger/20 text-danger hover:bg-danger/5">
                                <Trash2 className="h-4 w-4" /> Trash
                            </Button>
                        </div>
                    </div>

                    <Card className="border-white/60 shadow-xl bg-white/70 backdrop-blur-md overflow-hidden">
                        <CardHeader className="bg-[#f2f6fc] border-b border-white/80 px-6 py-4">
                            <div className="flex items-center justify-between gap-4">
                                <h1 className="text-lg font-semibold text-slate-800 truncate">{thread.subject}</h1>
                                <span className="text-xs text-slate-500 font-mono uppercase tracking-widest">Thread view</span>
                            </div>
                            {intel && (
                                <div className="mt-4 grid grid-cols-1 sm:grid-cols-3 gap-3">
                                    <div className="rounded-xl bg-indigo-50 border border-indigo-600/10 p-3">
                                        <p className="text-[10px] font-bold uppercase tracking-widest text-indigo-600">AI Intelligence</p>
                                        <p className="mt-1 text-sm font-semibold text-slate-800 truncate">{intel.intent || 'Unclassified'}</p>
                                    </div>
                                    <div className="rounded-xl bg-slate-50 border border-slate-200 p-3">
                                        <p className="text-[10px] font-bold uppercase tracking-widest text-slate-500">Urgency</p>
                                        <p className="mt-1 text-sm font-semibold text-slate-800">Score {intel.urgency_score}/100</p>
                                    </div>
                                    <div className="rounded-xl bg-emerald-50 border border-emerald-600/10 p-3">
                                        <p className="text-[10px] font-bold uppercase tracking-widest text-emerald-600">Suggested Action</p>
                                        <p className="mt-1 text-sm font-semibold text-slate-800 truncate">{intel.main_ask || 'Review and respond'}</p>
                                    </div>
                                </div>
                            )}
                        </CardHeader>
                        <CardContent className="p-0">
                            <div className="px-6 py-5 border-b border-slate-100">
                                <div className="flex justify-between items-start gap-4">
                                    <div>
                                        <h2 className="text-base font-bold text-slate-900 mb-1">{getSenderInfo(thread.messages[0]?.from_address || '').name}</h2>
                                        <p className="text-[13px] text-slate-500">{getSenderInfo(thread.messages[0]?.from_address || '').email}</p>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-[13px] text-slate-500">
                                            {new Date(thread.last_updated).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}
                                        </p>
                                        <p className="text-[11px] text-slate-400 mt-1 uppercase tracking-widest font-bold">
                                            {new Date(thread.last_updated).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}
                                        </p>
                                    </div>
                                </div>
                            </div>

                            <div className="px-6 py-6 space-y-6 text-slate-700 leading-loose text-sm">
                                {thread.messages.map((msg: EmailMessage) => (
                                    <MessageContent
                                        key={msg.message_id}
                                        message={msg}
                                        onCreateTask={() => handleCreateTaskFromMessage(msg)}
                                        creating={creatingMessageId === msg.message_id}
                                    />
                                ))}
                            </div>

                            {draft && (
                                <div className="px-6 pb-6">
                                    <h3 className="text-[11px] font-bold uppercase tracking-widest text-slate-400 mb-3 flex items-center gap-2">
                                        <Send className="h-4 w-4 text-indigo-600" /> Auto-Drafted Reply
                                    </h3>
                                    <DraftCard draft={draft} />
                                </div>
                            )}

                            {attachmentItems.length > 0 && (
                                <div className="px-6 pb-6 border-t border-slate-100 pt-6">
                                    <h5 className="text-[11px] font-bold uppercase tracking-widest text-slate-400 mb-4">
                                        Attachments ({attachmentItems.length})
                                    </h5>
                                    <div className="flex flex-wrap gap-4">
                                        {attachmentItems.map((att: AttachmentRef) => {
                                            const sizeMB = (att.size_bytes / (1024 * 1024)).toFixed(1);
                                            return (
                                                <div key={att.attachment_id} className="group flex items-center gap-3 p-3 rounded-xl border border-indigo-600/10 bg-slate-50 transition-all min-w-[220px]">
                                                    <div className="w-10 h-10 rounded-lg bg-red-100 flex items-center justify-center text-red-600 shadow-sm shrink-0">
                                                        <FileText className="h-5 w-5" />
                                                    </div>
                                                    <div className="flex-1 min-w-0 pr-2">
                                                        <p className="text-[13px] font-semibold text-slate-800 truncate">{att.filename}</p>
                                                        <p className="text-[11px] text-slate-400 font-medium">{sizeMB} MB</p>
                                                    </div>
                                                </div>
                                            );
                                        })}
                                    </div>
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </div>

                <aside className="space-y-4 lg:sticky lg:top-24 h-fit">
                    <Card className="border-white/60 shadow-lg bg-white/75 backdrop-blur-md overflow-hidden">
                        <CardHeader className="px-4 py-4 border-b border-slate-100">
                            <div className="flex items-center justify-between gap-3">
                                <div>
                                    <p className="text-[10px] font-bold uppercase tracking-[0.24em] text-slate-400">AI Intelligence</p>
                                    <h3 className="text-sm font-semibold text-slate-800">Thread synthesis</h3>
                                </div>
                                <Sparkles className="h-5 w-5 text-indigo-600" />
                            </div>
                        </CardHeader>
                        <CardContent className="p-4 space-y-4">
                            <div className="rounded-xl bg-indigo-50 border border-indigo-600/10 p-3">
                                <p className="text-[10px] font-bold uppercase tracking-widest text-indigo-600">Summary</p>
                                <p className="mt-1 text-sm text-slate-700 leading-relaxed">
                                    {intel?.summary || 'No AI summary available for this thread.'}
                                </p>
                            </div>
                            <div className="grid grid-cols-2 gap-3">
                                <div className="rounded-xl bg-slate-50 border border-slate-200 p-3">
                                    <p className="text-[10px] font-bold uppercase tracking-widest text-slate-500">Messages</p>
                                    <p className="mt-1 text-lg font-semibold text-slate-800">{thread.messages.length}</p>
                                </div>
                                <div className="rounded-xl bg-slate-50 border border-slate-200 p-3">
                                    <p className="text-[10px] font-bold uppercase tracking-widest text-slate-500">Tasks</p>
                                    <p className="mt-1 text-lg font-semibold text-slate-800">{taskItems.length}</p>
                                </div>
                            </div>
                            <div className="space-y-2">
                                <p className="text-[10px] font-bold uppercase tracking-widest text-slate-400">Linked Tasks</p>
                                {taskItems.length > 0 ? taskItems.slice(0, 3).map((task: any) => (
                                    <div key={task.task_id} className="rounded-xl border border-slate-200 bg-white px-3 py-2">
                                        <p className="text-sm font-semibold text-slate-800 truncate">{task.title}</p>
                                        <p className="text-[10px] text-slate-500 uppercase tracking-widest">{task.priority} · {task.status}</p>
                                    </div>
                                )) : (
                                    <p className="text-sm text-slate-500">No linked workflow tasks yet.</p>
                                )}
                            </div>
                            <div className="space-y-2">
                                <p className="text-[10px] font-bold uppercase tracking-widest text-slate-400">Attachments</p>
                                <p className="text-sm text-slate-700">
                                    {attachmentItems.length > 0 ? `${attachmentItems.length} attachments indexed and ready for intelligence review.` : 'No attachment intelligence available.'}
                                </p>
                            </div>
                            {intel?.attachment_summaries && intel.attachment_summaries.length > 0 && (
                                <div className="space-y-2">
                                    <p className="text-[10px] font-bold uppercase tracking-widest text-slate-400">Attachment Intelligence</p>
                                    <div className="space-y-2">
                                        {intel.attachment_summaries.map((att) => (
                                            <div key={att.attachment_id} className="rounded-xl border border-slate-200 bg-white px-3 py-2">
                                                <p className="text-sm font-semibold text-slate-800">{att.document_type || 'Document'} · {att.importance || 'medium'}</p>
                                                <p className="text-xs text-slate-600 mt-1">{att.summary || 'No summary available.'}</p>
                                                {att.key_points && att.key_points.length > 0 && (
                                                    <ul className="mt-2 list-disc pl-4 space-y-1">
                                                        {att.key_points.slice(0, 3).map((point, idx) => (
                                                            <li key={`${att.attachment_id}-${idx}`} className="text-[11px] text-slate-600">{point}</li>
                                                        ))}
                                                    </ul>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </CardContent>
                    </Card>

                    {draft && (
                        <Card className="border-white/60 shadow-lg bg-white/75 backdrop-blur-md overflow-hidden">
                            <CardHeader className="px-4 py-4 border-b border-slate-100">
                                <p className="text-[10px] font-bold uppercase tracking-[0.24em] text-slate-400">Draft Intelligence</p>
                                <h3 className="text-sm font-semibold text-slate-800">Auto-generated reply</h3>
                            </CardHeader>
                            <CardContent className="p-4 space-y-3">
                                <div className="grid grid-cols-2 gap-2 text-[10px] font-bold uppercase tracking-widest text-slate-500">
                                    <div className="rounded-xl bg-slate-50 border border-slate-200 p-3">
                                        Model
                                        <div className="mt-1 text-sm text-slate-800 normal-case tracking-normal">{draft.model_version}</div>
                                    </div>
                                    <div className="rounded-xl bg-slate-50 border border-slate-200 p-3">
                                        Placeholders
                                        <div className="mt-1 text-sm text-slate-800 normal-case tracking-normal">
                                            {draft.has_unresolved_placeholders ? 'Needs review' : 'Resolved'}
                                        </div>
                                    </div>
                                </div>
                                <div className="rounded-xl bg-indigo-50 border border-indigo-600/10 p-3 text-sm text-slate-700">
                                    {draft.references_attachments ? 'References attachments' : 'No attachment references'} · {draft.references_deadlines ? 'References deadlines' : 'No deadline references'}
                                </div>
                            </CardContent>
                        </Card>
                    )}
                </aside>
            </div>
        </ThreadPageShell>
    );
}

function ThreadPageShell({ title, subtitle, children }: { title: string; subtitle: string; children: React.ReactNode }) {
    return (
        <div className="min-h-screen bg-gradient-to-b from-[#f8fafc] to-[#eef2ff]">
            <div className="sticky top-0 z-20 border-b border-slate-200/70 bg-white/80 backdrop-blur-md">
                <div className="max-w-6xl mx-auto px-4 md:px-6 h-16 flex items-center justify-between gap-4">
                    <div className="min-w-0">
                        <p className="text-[10px] font-bold uppercase tracking-[0.28em] text-slate-400">Inbox Thread</p>
                        <h1 className="text-sm md:text-base font-semibold text-slate-800 truncate">{title}</h1>
                    </div>
                    <p className="text-xs text-slate-500 truncate max-w-[40%] text-right">{subtitle}</p>
                </div>
            </div>
            {children}
        </div>
    );
}

function LoadingState() {
    return (
        <div className="max-w-4xl mx-auto px-4 md:px-6 py-10 space-y-4">
            <div className="h-10 w-64 rounded-xl bg-slate-200 animate-pulse" />
            <div className="h-40 rounded-3xl bg-white/70 border border-slate-200 animate-pulse" />
            <div className="h-80 rounded-3xl bg-white/70 border border-slate-200 animate-pulse" />
        </div>
    );
}

function ErrorState({ onBack }: { onBack: () => void }) {
    return (
        <div className="max-w-2xl mx-auto px-4 md:px-6 py-20">
            <Card className="border-red-200 bg-white/80 shadow-lg">
                <CardContent className="p-8 text-center space-y-4">
                    <AlertTriangle className="h-10 w-10 text-red-500 mx-auto" />
                    <h2 className="text-xl font-semibold text-slate-900">Thread not found</h2>
                    <p className="text-sm text-slate-600">The thread could not be loaded in the separate page view.</p>
                    <Button onClick={onBack}>Back to inbox</Button>
                </CardContent>
            </Card>
        </div>
    );
}

// ─── Message Content Helper ─────────────────────────────────────────────

function getSenderInfo(fromAddress: string) {
    let name = fromAddress;
    let email = fromAddress;
    const match = fromAddress.match(/(.*?)<(.+?)>/);
    if (match) {
        name = match[1].trim().replace(/^"|"$/g, '');
        email = match[2].trim();
    }
    if (!name || name === email) name = email.split('@')[0];
    return { name, email };
}

function MessageContent({ message, onCreateTask, creating }: { message: EmailMessage; onCreateTask: () => void; creating: boolean }) {
    return (
        <div className="border-b border-slate-100 pb-6 mb-6 last:border-0 last:pb-0 last:mb-0">
            <div className="flex items-center justify-end mb-2">
                <button
                    type="button"
                    onClick={onCreateTask}
                    disabled={creating}
                    className="h-8 px-3 rounded-lg bg-indigo-50 text-indigo-700 border border-indigo-200 text-[11px] font-bold uppercase tracking-wider disabled:opacity-60"
                >
                    {creating ? 'Creating...' : 'Create Task from Email'}
                </button>
            </div>
            {message.body_html ? (
                <div
                    className="email-body-html prose prose-sm max-w-none prose-slate"
                    dangerouslySetInnerHTML={{ __html: message.body_html }}
                />
            ) : (
                <div className="whitespace-pre-wrap">
                    {message.body_text}
                </div>
            )}
        </div>
    );
}

// ─── Draft Card ──────────────────────────────────────────────

function DraftCard({ draft }: { draft: DraftDTOv1 }) {
    const [isRegenerating, setIsRegenerating] = useState(false);

    const handleRegenerate = async () => {
        setIsRegenerating(true);
        await new Promise(r => setTimeout(r, 1200));
        setIsRegenerating(false);
    };

    return (
        <div className="rounded-xl border border-indigo-600/20 bg-indigo-50/50 p-4">
            <div className="flex items-center justify-between mb-3 border-b border-indigo-600/10 pb-3">
                <div className="flex items-center gap-2">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-indigo-600">Tone:</span>
                    <Badge variant="outline" className="text-[10px] capitalize border-indigo-600/30 text-indigo-700 bg-white shadow-sm">{draft.tone}</Badge>
                </div>
                <div className="flex items-center gap-2">
                    <Button
                        variant="ghost" size="sm"
                        className="gap-1.5 text-xs h-7 text-slate-500 hover:text-indigo-700 hover:bg-white bg-white/50 border border-slate-200"
                        onClick={handleRegenerate}
                        disabled={isRegenerating}
                    >
                        <RefreshCw className={`h-3 w-3 ${isRegenerating ? 'animate-spin' : ''}`} />
                        Regenerate
                    </Button>
                </div>
            </div>
            <div className="text-[13px] leading-relaxed whitespace-pre-line text-slate-800 font-medium">
                {draft.content.split(/(\[.*?\])/).map((part, i) => {
                    if (part.startsWith('[') && part.endsWith(']')) {
                        const placeholder = draft.placeholders?.find(p => p.key === part);
                        return (
                            <span
                                key={i}
                                className="bg-amber-100 border border-amber-300 rounded px-1 py-0.5 text-amber-800 cursor-pointer hover:bg-amber-200 transition-colors text-xs font-bold"
                                title={placeholder?.description}
                            >
                                {part}
                            </span>
                        );
                    }
                    return <span key={i}>{part}</span>;
                })}
            </div>
        </div>
    );
}
