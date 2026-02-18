'use client';

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Skeleton } from '@/components/ui/skeleton';
import AppShell from '@/components/layout/AppShell';
import { mockThreads, getSenderInfo } from '@/data/mockData';
import { useDashboard } from '@/hooks/useDashboard';
import type { TaskDTOv1, ThreadListItem, EmailThreadV1, PriorityLevel } from '@/types/dashboard';
import {
    Sparkles, Mail, AlertTriangle, CheckSquare, Clock,
    ArrowUpRight, ChevronRight, Zap, FileText
} from 'lucide-react';
import Link from 'next/link';

const priorityConfig = {
    do_now: { label: 'Do Now', variant: 'destructive' as const, color: 'bg-red-500' },
    do_today: { label: 'Today', variant: 'default' as const, color: 'bg-amber-500' },
    can_wait: { label: 'Can Wait', variant: 'secondary' as const, color: 'bg-green-500' },
};

export default function DashboardPage() {
    const { data, isLoading, error } = useDashboard();

    if (isLoading) {
        return (
            <AppShell title="Dashboard" subtitle="Your morning briefing">
                <div className="p-6 max-w-7xl mx-auto space-y-6">
                    <div className="h-48 rounded-xl bg-paper-mid animate-pulse" />
                    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                        {[1, 2, 3, 4].map((i) => (
                            <div key={i} className="h-32 rounded-xl bg-paper-mid animate-pulse" />
                        ))}
                    </div>
                </div>
            </AppShell>
        );
    }

    if (error || !data) {
        return (
            <AppShell title="Dashboard">
                <div className="p-6 text-center text-danger">
                    Failed to load dashboard data.
                </div>
            </AppShell>
        );
    }

    const { briefing, stats, recent_threads, priority_tasks } = data;

    return (
        <AppShell title="Dashboard" subtitle="Your morning briefing">
            <div className="p-6 max-w-7xl mx-auto space-y-6">

                {/* ─── AI Briefing Card ────────────────── */}
                <Card className="relative overflow-hidden border-ai/20">
                    <div className="absolute top-0 left-0 w-1 h-full bg-gradient-to-b from-ai to-purple-400" />
                    <CardHeader className="pl-6">
                        <div className="flex items-center gap-2">
                            <Sparkles className="h-4 w-4 text-ai" />
                            <CardTitle className="text-sm font-mono uppercase tracking-wider text-ai">
                                AI Briefing
                            </CardTitle>
                        </div>
                        <CardDescription className="text-base leading-relaxed mt-2">
                            {briefing.summary}
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="pl-6">
                        <div className="flex flex-wrap gap-2">
                            {briefing.suggested_actions.map((action: string, i: number) => (
                                <Button key={i} variant="outline" size="sm" className="gap-1.5 text-xs">
                                    <Zap className="h-3 w-3" />
                                    {action}
                                </Button>
                            ))}
                        </div>
                    </CardContent>
                </Card>

                {/* ─── Stat Cards ─────────────────────── */}
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                    {[
                        { label: 'Unread', value: stats.unread, icon: Mail, delta: stats.unread_delta, color: 'text-info' },
                        { label: 'Urgent', value: stats.urgent, icon: AlertTriangle, delta: null, color: 'text-danger' },
                        { label: 'Tasks Due', value: stats.tasks_due, icon: CheckSquare, delta: null, color: 'text-warning' },
                        { label: 'Awaiting Reply', value: stats.awaiting_reply, icon: Clock, delta: null, color: 'text-accent' },
                    ].map((stat) => (
                        <Card key={stat.label}>
                            <CardContent className="p-5">
                                <div className="flex items-center justify-between mb-3">
                                    <span className="section-label">{stat.label}</span>
                                    <stat.icon className={`h-4 w-4 ${stat.color}`} />
                                </div>
                                <p className="font-display text-h1">{stat.value}</p>
                                {stat.delta && (
                                    <p className="font-mono text-xs text-muted-foreground mt-1">{stat.delta}</p>
                                )}
                            </CardContent>
                        </Card>
                    ))}
                </div>

                <div className="grid lg:grid-cols-5 gap-6">

                    {/* ─── Priority Tasks ─────────────── */}
                    <div className="lg:col-span-2">
                        <Card>
                            <CardHeader className="pb-3">
                                <CardTitle className="text-sm font-mono uppercase tracking-wider text-muted-foreground">
                                    Priority Queue
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="p-0">
                                <ScrollArea className="h-[360px]">
                                    {priority_tasks.map((task: TaskDTOv1) => {
                                        const cfg = priorityConfig[task.priority as PriorityLevel];
                                        return (
                                            <div key={task.task_id} className="flex items-start gap-3 px-5 py-4 border-b border-border last:border-0 hover:bg-paper-mid transition-colors">
                                                <div className={`w-1 h-12 rounded-full ${cfg.color} shrink-0 mt-0.5`} />
                                                <div className="flex-1 min-w-0">
                                                    <div className="flex items-center gap-2 mb-1">
                                                        <Badge variant={cfg.variant} className="text-[10px] px-1.5 py-0">
                                                            {cfg.label}
                                                        </Badge>
                                                        <Badge variant="outline" className="text-[10px] px-1.5 py-0">
                                                            {task.task_type}
                                                        </Badge>
                                                    </div>
                                                    <p className="text-sm font-medium truncate">{task.title}</p>
                                                    {task.deadline && (
                                                        <p className="text-xs text-muted-foreground font-mono mt-1">
                                                            Due: {new Date(task.deadline).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })}
                                                        </p>
                                                    )}
                                                </div>
                                                <ChevronRight className="h-4 w-4 text-muted-foreground shrink-0" />
                                            </div>
                                        );
                                    })}
                                </ScrollArea>
                            </CardContent>
                        </Card>
                    </div>

                    {/* ─── Recent Threads ─────────────── */}
                    <div className="lg:col-span-3">
                        <Card>
                            <CardHeader className="pb-3 flex flex-row items-center justify-between">
                                <CardTitle className="text-sm font-mono uppercase tracking-wider text-muted-foreground">
                                    Recent Emails
                                </CardTitle>
                                <Link href="/inbox">
                                    <Button variant="ghost" size="sm" className="text-xs gap-1">
                                        View all <ArrowUpRight className="h-3 w-3" />
                                    </Button>
                                </Link>
                            </CardHeader>
                            <CardContent className="p-0">
                                <ScrollArea className="h-[360px]">
                                    {recent_threads.map((thread: ThreadListItem) => {
                                        const fullThread = mockThreads.find((t: EmailThreadV1) => t.thread_id === thread.thread_id);
                                        const lastMsg = fullThread?.messages[fullThread.messages.length - 1];
                                        const sender = lastMsg ? getSenderInfo(lastMsg.from_address) : { name: 'Unknown', initials: '??' };

                                        return (
                                            <Link key={thread.thread_id} href={`/inbox/${thread.thread_id}`}>
                                                <div className="flex items-start gap-3 px-5 py-4 border-b border-border last:border-0 hover:bg-paper-mid transition-colors cursor-pointer group">
                                                    {/* Avatar */}
                                                    <div className="w-9 h-9 rounded-full bg-paper-deep flex items-center justify-center text-xs font-semibold text-ink-light shrink-0">
                                                        {sender.initials}
                                                    </div>

                                                    {/* Content */}
                                                    <div className="flex-1 min-w-0">
                                                        <div className="flex items-center justify-between">
                                                            <p className="text-sm font-semibold truncate">{sender.name}</p>
                                                            <span className="text-xs text-muted-foreground font-mono shrink-0 ml-2">
                                                                {new Date(thread.last_updated).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}
                                                            </span>
                                                        </div>
                                                        <p className="text-sm truncate">{thread.subject}</p>
                                                        <p className="text-xs text-muted-foreground truncate mt-0.5">
                                                            {thread.summary.slice(0, 80)}...
                                                        </p>
                                                    </div>

                                                    {/* Indicators */}
                                                    <div className="flex flex-col items-end gap-1 shrink-0">
                                                        {thread.urgency_score >= 70 && (
                                                            <Badge variant="destructive" className="text-[10px]">Urgent</Badge>
                                                        )}
                                                        {thread.has_attachments && (
                                                            <FileText className="h-3.5 w-3.5 text-muted-foreground" />
                                                        )}
                                                    </div>
                                                </div>
                                            </Link>
                                        );
                                    })}
                                </ScrollArea>
                            </CardContent>
                        </Card>
                    </div>
                </div>
            </div>
        </AppShell>
    );
}
