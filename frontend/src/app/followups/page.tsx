'use client';

import React from 'react';
import AppShell from '@/components/layout/AppShell';
import { WaitingForDTOv1 } from '@/types/dashboard';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Clock, Bell, CheckCircle2, MoreHorizontal, CalendarClock, AlertCircle } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { useWaitingFor } from '@/hooks/useWaitingFor';

function FollowUpGroup({ title, items, variant }: { title: string; items: WaitingForDTOv1[]; variant: 'destructive' | 'warning' | 'default' }) {
    if (items.length === 0) return null;

    let Icon;
    let colorClass;
    let badgeClass;

    switch (variant) {
        case 'destructive':
            Icon = AlertCircle;
            colorClass = 'text-destructive';
            badgeClass = 'bg-destructive/10 text-destructive';
            break;
        case 'warning':
            Icon = Clock;
            colorClass = 'text-warning';
            badgeClass = 'bg-warning/10 text-warning';
            break;
        case 'default':
            Icon = CheckCircle2;
            colorClass = 'text-ink-light'; // Or a neutral color
            badgeClass = 'bg-primary/10 text-primary'; // Or a neutral badge
            break;
        default:
            Icon = Clock;
            colorClass = 'text-muted-foreground';
            badgeClass = 'bg-muted/10 text-muted-foreground';
    }

    return (
        <div className="space-y-4">
            <h3 className={`font-display text-lg flex items-center gap-2 ${colorClass}`}>
                <Icon className="h-5 w-5" />
                {title}
                <span className="text-sm font-sans font-normal text-muted-foreground ml-2">({items.length})</span>
            </h3>
            <div className="space-y-3">
                {items.map((item) => {
                    // Extract initials
                    const initials = item.recipient.split('@')[0].substring(0, 2).toUpperCase();

                    return (
                        <Card key={item.waiting_id} className="hover:shadow-md transition-shadow cursor-pointer group">
                            <CardContent className="p-4 flex items-center justify-between gap-4">
                                <div className="flex items-center gap-4 flex-1 min-w-0">
                                    <Avatar className="h-10 w-10 border border-border-light bg-paper-mid">
                                        <AvatarFallback className="text-xs font-medium text-ink-light">
                                            {initials}
                                        </AvatarFallback>
                                    </Avatar>
                                    <div className="min-w-0 flex-1">
                                        <div className="flex items-baseline gap-2 mb-0.5">
                                            <span className="font-medium text-ink truncate">{item.recipient}</span>
                                            <span className="text-xs text-muted-foreground">
                                                Sent {formatDistanceToNow(new Date(item.last_sent_at))} ago
                                            </span>
                                        </div>
                                        <h4 className="text-sm text-ink-light truncate font-medium">
                                            {item.thread_subject}
                                        </h4>
                                        <p className="text-xs text-muted-foreground truncate max-w-md">
                                            {item.thread_summary}
                                        </p>
                                    </div>
                                </div>

                                <div className="flex items-center gap-3 opacity-0 group-hover:opacity-100 transition-opacity">
                                    <Button variant="ghost" size="sm" className="h-8 w-8 p-0" title="Set Reminder">
                                        <Bell className="h-4 w-4 text-muted-foreground hover:text-ink" />
                                    </Button>
                                    <Button variant="ghost" size="sm" className="h-8 w-8 p-0" title="Snooze">
                                        <CalendarClock className="h-4 w-4 text-muted-foreground hover:text-ink" />
                                    </Button>
                                    <Button variant="ghost" size="sm" className="h-8 w-8 p-0" title="Mark Resolved">
                                        <CheckCircle2 className="h-4 w-4 text-success hover:text-success/80" />
                                    </Button>
                                    <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                                        <MoreHorizontal className="h-4 w-4 text-muted-foreground" />
                                    </Button>
                                </div>

                                <div className="text-right shrink-0">
                                    <Badge variant="outline" className={`border-transparent ${colorClass === 'text-destructive' ? 'bg-destructive/10 text-destructive' : 'bg-warning/10 text-warning'}`}>
                                        {item.days_waiting} days
                                    </Badge>
                                </div>
                            </CardContent>
                        </Card>
                    );
                })}
            </div>
        </div>
    );
}

export default function FollowupsPage() {
    const { data: waitingItems, isLoading, error } = useWaitingFor();

    if (isLoading) {
        return (
            <AppShell title="Follow-up Tracker">
                <div className="p-8 space-y-6">
                    <div className="h-8 w-48 bg-paper-mid animate-pulse rounded-md" />
                    <div className="space-y-4">
                        {[1, 2, 3].map(i => (
                            <div key={i} className="h-32 bg-paper-mid animate-pulse rounded-xl" />
                        ))}
                    </div>
                </div>
            </AppShell>
        );
    }

    if (error || !waitingItems) {
        return (
            <AppShell title="Follow-up Tracker">
                <div className="p-8 text-center text-danger">
                    Failed to load follow-ups.
                </div>
            </AppShell>
        );
    }

    // Group items by status
    const overdue = waitingItems.filter(i => i.days_waiting > 3);
    const dueSoon = waitingItems.filter(i => i.days_waiting <= 3);
    const snoozed: WaitingForDTOv1[] = []; // Placeholder until API supports snoozed

    return (
        <AppShell title="Follow-up Tracker">
            <div className="flex flex-col h-full overflow-hidden">
                <div className="px-8 py-6 border-b border-border-light bg-surface-card/30">
                    <h1 className="font-display text-3xl text-ink">Follow-up Tracker</h1>
                    <p className="text-ink-light mt-1">Track outstanding emails and get nudges when replies are late.</p>
                </div>

                <div className="flex-1 overflow-y-auto p-8 space-y-8 scrollbar-thin">
                    <FollowUpGroup
                        title="Overdue"
                        items={overdue}
                        variant="destructive"
                    />
                    <FollowUpGroup
                        title="Due Soon"
                        items={dueSoon}
                        variant="warning"
                    />

                    {/* Empty State for Snoozed */}
                    <div className="space-y-4 opacity-60">
                        <h3 className="font-display text-lg flex items-center gap-2 text-muted-foreground">
                            <CalendarClock className="h-5 w-5" />
                            Snoozed
                            <span className="text-sm font-sans font-normal ml-2">({snoozed.length})</span>
                        </h3>
                        <div className="border border-dashed border-border-light rounded-xl p-8 text-center bg-paper-mid/30">
                            <p className="text-sm text-muted-foreground">No snoozed items.</p>
                        </div>
                    </div>
                </div>
            </div>
        </AppShell>
    );
}
