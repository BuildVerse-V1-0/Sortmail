'use client';

import React, { useState, useMemo } from 'react';
import Link from 'next/link';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import AppShell from '@/components/layout/AppShell';
import { useThreads } from '@/hooks/useThreads';
import { useSmartSync } from '@/hooks/useSmartSync';
import { useRealtimeEvents } from '@/hooks/useRealtimeEvents';
import {
    Search,
    RefreshCw,
    Inbox,
    AlertTriangle,
    Clock,
    FileText,
    ChevronRight
} from 'lucide-react';
import { FilterTab, ThreadListItem } from '@/types/dashboard';

export default function InboxPage() {
    const [search, setSearch] = useState('');
    const [activeTab, setActiveTab] = useState<FilterTab>('all');

    // DB-first: threads load instantly from cache/DB
    const { data: threads, isLoading, error } = useThreads(activeTab === 'all' ? undefined : activeTab);

    // Smart background sync: checks if stale → incremental Gmail sync → invalidates cache
    const { syncState, triggerSync } = useSmartSync();

    // Real-time SSE: auto-refresh when backend publishes intel_ready / new_emails
    useRealtimeEvents();

    const isSyncing = syncState === 'syncing' || syncState === 'checking';

    const filtered = useMemo(() => {
        if (!threads) return [];
        let items = threads;
        if (search) {
            const q = search.toLowerCase();
            items = items.filter((t: ThreadListItem) =>
                t.subject.toLowerCase().includes(q) ||
                t.summary.toLowerCase().includes(q)
            );
        }
        return items;
    }, [search, threads]);


    return (
        <AppShell title="Inbox" subtitle={`${threads?.length || 0} threads`}>
            <div className="max-w-4xl mx-auto space-y-4">

                {/* ─── Search + Sync ──────────────────── */}
                <div className="flex items-center gap-3">
                    <div className="relative flex-1">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                        <Input
                            placeholder="Search emails..."
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                            className="pl-10 bg-surface-card border-border-light"
                        />
                    </div>
                    <Button
                        variant="outline" size="icon" className="shrink-0"
                        onClick={triggerSync}
                        disabled={isSyncing}
                        title={isSyncing ? 'Syncing...' : 'Sync emails'}
                    >
                        <RefreshCw className={`h-4 w-4 ${isSyncing ? 'animate-spin' : ''}`} />
                    </Button>
                </div>
                {isSyncing && (
                    <p className="text-xs text-muted-foreground text-center animate-pulse">
                        Checking for new emails...
                    </p>
                )}

                {/* ─── Tabs ───────────────────────────── */}
                <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as FilterTab)}>
                    <TabsList className="bg-paper-mid">
                        <TabsTrigger value="all" className="gap-1.5">
                            <Inbox className="h-3.5 w-3.5" />
                            All
                        </TabsTrigger>
                        <TabsTrigger value="urgent" className="gap-1.5">
                            <AlertTriangle className="h-3.5 w-3.5" />
                            Urgent
                        </TabsTrigger>
                        <TabsTrigger value="action_required" className="gap-1.5">
                            <Clock className="h-3.5 w-3.5" />
                            Action Required
                        </TabsTrigger>
                        <TabsTrigger value="fyi" className="gap-1.5">
                            <FileText className="h-3.5 w-3.5" />
                            FYI
                        </TabsTrigger>
                    </TabsList>
                </Tabs>

                {/* ─── Thread List ────────────────────── */}
                <Card>
                    <CardContent className="p-0">
                        <ScrollArea className="h-[calc(100vh-280px)]">
                            {isLoading ? (
                                <div className="p-4 space-y-4">
                                    {[1, 2, 3, 4, 5].map((i) => (
                                        <div key={i} className="h-20 rounded-lg bg-paper-mid animate-pulse" />
                                    ))}
                                </div>
                            ) : error ? (
                                <div className="p-8 text-center text-danger">
                                    Failed to load threads.
                                </div>
                            ) : filtered.length === 0 ? (
                                <div className="flex flex-col items-center justify-center py-16 text-muted-foreground gap-3">
                                    <Inbox className="h-10 w-10 opacity-40" />
                                    <p className="text-sm font-medium">Your inbox is empty</p>
                                    <p className="text-xs">Make sure your Gmail account is connected, then sync.</p>
                                    <Button size="sm" variant="outline" onClick={triggerSync} disabled={syncing} className="gap-2 mt-1">
                                        <RefreshCw className={`h-3.5 w-3.5 ${syncing ? 'animate-spin' : ''}`} />
                                        Sync Emails
                                    </Button>
                                </div>
                            ) : (
                                filtered.map((thread: ThreadListItem, i: number) => (
                                    <ThreadRow key={thread.thread_id} thread={thread} isLast={i === filtered.length - 1} />
                                ))
                            )}
                        </ScrollArea>
                    </CardContent>
                </Card>
            </div>
        </AppShell>
    );
}


function ThreadRow({ thread, isLast }: { thread: ThreadListItem; isLast: boolean }) {
    // Parse sender from thread.participants
    const firstParticipant = (thread as any).participants?.[0] ?? '';
    const sender = (() => {
        if (!firstParticipant) return { name: 'Unknown', initials: '??', color: '#6b7280' };
        const nameMatch = firstParticipant.match(/^"?([^"<]+)"?\s*</);
        const name = nameMatch
            ? nameMatch[1].trim()
            : firstParticipant.split('@')[0].replace(/[._]/g, ' ');
        const parts = name.trim().split(' ').filter(Boolean);
        const initials = parts.length >= 2
            ? (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
            : name.slice(0, 2).toUpperCase();
        // Deterministic color from name
        const colors = ['#6366f1', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#3b82f6', '#ef4444', '#14b8a6'];
        const color = colors[name.charCodeAt(0) % colors.length];
        return { name, initials, color };
    })();

    const isUrgent = thread.urgency_score >= 70;
    const isAction = thread.intent === 'action_required';
    const isFyi = thread.intent === 'fyi';
    const isUnread = (thread as any).is_unread ?? false;

    return (
        <Link href={`/inbox/${thread.thread_id}`}>
            <div className={`
                relative flex items-stretch gap-0
                hover:bg-white/5 transition-all duration-150 cursor-pointer group
                ${!isLast ? 'border-b border-white/5' : ''}
            `}>
                {/* Priority left bar */}
                {isUrgent && <div className="w-0.5 bg-red-500 shrink-0 rounded-r" />}
                {isAction && !isUrgent && <div className="w-0.5 bg-amber-400 shrink-0 rounded-r" />}
                {!isUrgent && !isAction && <div className="w-0.5 shrink-0" />}

                <div className="flex items-start gap-3 px-4 py-3.5 flex-1 min-w-0">
                    {/* Avatar */}
                    <div
                        className="w-9 h-9 rounded-full flex items-center justify-center text-[11px] font-bold shrink-0 mt-0.5 ring-1 ring-white/10"
                        style={{ backgroundColor: sender.color + '25', color: sender.color }}
                    >
                        {sender.initials}
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                        {/* Row 1: Name + Time */}
                        <div className="flex items-center justify-between gap-2 mb-0.5">
                            <div className="flex items-center gap-1.5 min-w-0">
                                {isUnread && (
                                    <span className="w-1.5 h-1.5 rounded-full bg-blue-400 shrink-0" />
                                )}
                                <span className={`text-sm truncate ${isUnread ? 'font-semibold text-white' : 'font-medium text-zinc-300'}`}>
                                    {sender.name}
                                </span>
                            </div>
                            <span className="text-[11px] text-zinc-500 shrink-0 tabular-nums">
                                {formatTime(thread.last_updated)}
                            </span>
                        </div>

                        {/* Row 2: Subject */}
                        <p className={`text-[13px] truncate leading-snug ${isUnread ? 'font-medium text-zinc-100' : 'text-zinc-400'}`}>
                            {thread.subject || '(No Subject)'}
                        </p>

                        {/* Row 3: Summary + Chips */}
                        <div className="flex items-center gap-2 mt-1.5">
                            <p className="text-[11px] text-zinc-600 truncate flex-1 leading-relaxed">
                                {thread.summary || 'Pending analysis...'}
                            </p>
                            <div className="flex items-center gap-1 shrink-0">
                                {isUrgent && (
                                    <span className="inline-flex items-center gap-0.5 text-[10px] font-semibold px-1.5 py-0.5 rounded bg-red-500/15 text-red-400 border border-red-500/20">
                                        🔥 Urgent
                                    </span>
                                )}
                                {isAction && !isUrgent && (
                                    <span className="inline-flex items-center text-[10px] font-semibold px-1.5 py-0.5 rounded bg-amber-500/15 text-amber-400 border border-amber-500/20">
                                        ⚡ Action
                                    </span>
                                )}
                                {isFyi && (
                                    <span className="inline-flex items-center text-[10px] font-medium px-1.5 py-0.5 rounded bg-zinc-700/60 text-zinc-400 border border-zinc-700">
                                        FYI
                                    </span>
                                )}
                                {thread.has_attachments && (
                                    <span className="inline-flex items-center gap-0.5 text-[10px] text-zinc-500 border border-zinc-700 px-1.5 py-0.5 rounded">
                                        <FileText className="h-2.5 w-2.5" />
                                    </span>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* Hover arrow */}
                    <ChevronRight className="h-3.5 w-3.5 text-zinc-600 shrink-0 mt-2 opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>
            </div>
        </Link>
    );
}

function formatTime(isoDate: string): string {
    const normalized = isoDate.endsWith('Z') || isoDate.includes('+') ? isoDate : isoDate + 'Z';
    const date = new Date(normalized);
    const now = new Date();
    const diffHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);
    const tz = 'Asia/Kolkata';
    if (diffHours < 24) {
        return date.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', timeZone: tz });
    }
    if (diffHours < 24 * 7) {
        return date.toLocaleDateString('en-IN', { weekday: 'short', timeZone: tz });
    }
    return date.toLocaleDateString('en-IN', { month: 'short', day: 'numeric', timeZone: tz });
}
