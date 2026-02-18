'use client';

import { useState, useMemo } from 'react';
import Link from 'next/link';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import AppShell from '@/components/layout/AppShell';
import { useThreads } from '@/hooks/useThreads';
import {
    Search,
    SlidersHorizontal,
    Inbox,
    AlertTriangle,
    Clock,
    FileText,
    ChevronRight
} from 'lucide-react';
import { FilterTab, ThreadListItem, EmailThreadV1 } from '@/types/dashboard';
import { mockThreads } from '@/data/mockData';
import { getSenderInfo } from '@/lib/utils';

export default function InboxPage() {
    const [search, setSearch] = useState('');
    const [activeTab, setActiveTab] = useState<FilterTab>('all');

    // Pass activeTab to hook for filtering (even if we do some client-side refining for search)
    const { data: threads, isLoading, error } = useThreads(activeTab === 'all' ? undefined : activeTab);

    const filtered = useMemo(() => {
        if (!threads) return [];
        let items = threads;

        // Search filter (client-side for now)
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

                {/* ─── Search + Filters ───────────────── */}
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
                    <Button variant="outline" size="icon" className="shrink-0">
                        <SlidersHorizontal className="h-4 w-4" />
                    </Button>
                </div>

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
                                <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
                                    <Inbox className="h-10 w-10 mb-3 opacity-40" />
                                    <p className="text-sm">No threads match your filters</p>
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
    const fullThread = mockThreads.find((t: EmailThreadV1) => t.thread_id === thread.thread_id);
    const lastMsg = fullThread?.messages[fullThread.messages.length - 1];
    const sender = lastMsg ? getSenderInfo(lastMsg.from_address) : { name: 'Unknown', initials: '??' };
    const isUrgent = thread.urgency_score >= 70;
    const isAction = thread.intent === 'action_required';

    return (
        <Link href={`/inbox/${thread.thread_id}`}>
            <div className={`flex items-start gap-4 px-5 py-4 hover:bg-paper-mid transition-colors cursor-pointer group ${!isLast ? 'border-b border-border' : ''}`}>
                {/* Avatar */}
                <div className={`w-10 h-10 rounded-full flex items-center justify-center text-xs font-semibold shrink-0 ${isUrgent ? 'bg-red-100 text-red-600' : 'bg-paper-deep text-ink-light'}`}>
                    {sender.initials}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-0.5">
                        <span className="text-sm font-semibold truncate">{sender.name}</span>
                        <span className="text-xs text-muted-foreground font-mono shrink-0">
                            {formatTime(thread.last_updated)}
                        </span>
                    </div>
                    <p className="text-sm font-medium truncate">{thread.subject}</p>
                    <p className="text-xs text-muted-foreground truncate mt-0.5">{thread.summary}</p>

                    {/* Tags */}
                    <div className="flex items-center gap-1.5 mt-2">
                        {isUrgent && (
                            <Badge variant="destructive" className="text-[10px] px-1.5 py-0">
                                Urgent
                            </Badge>
                        )}
                        {isAction && !isUrgent && (
                            <Badge variant="default" className="text-[10px] px-1.5 py-0">
                                Action Required
                            </Badge>
                        )}
                        {thread.intent === 'fyi' && (
                            <Badge variant="secondary" className="text-[10px] px-1.5 py-0">
                                FYI
                            </Badge>
                        )}
                        {thread.has_attachments && (
                            <Badge variant="outline" className="text-[10px] px-1.5 py-0 gap-0.5">
                                <FileText className="h-2.5 w-2.5" />
                                Attachment
                            </Badge>
                        )}
                    </div>
                </div>

                <ChevronRight className="h-4 w-4 text-muted-foreground shrink-0 mt-3 opacity-0 group-hover:opacity-100 transition-opacity" />
            </div>
        </Link>
    );
}

function formatTime(isoDate: string): string {
    const date = new Date(isoDate);
    const now = new Date();
    const diffHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);

    if (diffHours < 24) {
        return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    }
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}
