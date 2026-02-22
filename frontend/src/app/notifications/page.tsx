"use client";

import React from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Bell, CheckCheck, X, Mail, CheckSquare, Sparkles, Clock } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";
import AppShell from "@/components/layout/AppShell";
import { api, endpoints } from "@/lib/api";
import { formatDistanceToNow } from "date-fns";

interface Notification {
    id: string;
    type: string;
    title: string;
    body?: string;
    action_url?: string;
    is_read: boolean;
    priority: string;
    created_at: string;
}

export default function NotificationsPage() {
    const queryClient = useQueryClient();

    const { data: notifications = [], isLoading } = useQuery<Notification[]>({
        queryKey: ["notifications"],
        queryFn: async () => {
            const { data } = await api.get(endpoints.notifications);
            return data;
        },
    });

    const markRead = useMutation({
        mutationFn: (id: string) => api.post(`${endpoints.notifications}/${id}/read`),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ["notifications"] }),
    });

    const markAllRead = useMutation({
        mutationFn: () => api.post(`${endpoints.notifications}/read-all`),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ["notifications"] }),
    });

    const dismiss = useMutation({
        mutationFn: (id: string) => api.delete(`${endpoints.notifications}/${id}`),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ["notifications"] }),
    });

    const unreadCount = notifications.filter((n) => !n.is_read).length;

    const getIcon = (type: string) => {
        switch (type) {
            case "email_urgent": return <Mail className="w-4 h-4 text-red-500" />;
            case "task_due": return <CheckSquare className="w-4 h-4 text-amber-500" />;
            case "follow_up_reminder": return <Clock className="w-4 h-4 text-blue-500" />;
            case "credit_low": return <Sparkles className="w-4 h-4 text-purple-500" />;
            default: return <Bell className="w-4 h-4 text-muted-foreground" />;
        }
    };

    if (isLoading) {
        return (
            <AppShell title="Notifications">
                <div className="max-w-3xl mx-auto space-y-3 p-6">
                    {[1, 2, 3].map(i => (
                        <div key={i} className="h-20 rounded-xl bg-paper-mid animate-pulse" />
                    ))}
                </div>
            </AppShell>
        );
    }

    return (
        <AppShell title="Notifications" subtitle={unreadCount > 0 ? `${unreadCount} unread` : "All caught up"}>
            <div className="max-w-3xl mx-auto space-y-4 p-6">
                {/* Header Actions */}
                <div className="flex items-center justify-between">
                    <h1 className="font-display text-2xl text-ink">Notifications</h1>
                    <div className="flex gap-2">
                        {unreadCount > 0 && (
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={() => markAllRead.mutate()}
                                disabled={markAllRead.isPending}
                            >
                                <CheckCheck className="h-4 w-4 mr-2" />
                                Mark all read
                            </Button>
                        )}
                    </div>
                </div>

                {notifications.length === 0 ? (
                    <Card className="p-12 text-center text-muted-foreground">
                        <Bell className="h-12 w-12 mx-auto mb-4 opacity-30" />
                        <p className="text-lg font-medium">No notifications</p>
                        <p className="text-sm">You&apos;re all caught up!</p>
                    </Card>
                ) : (
                    <div className="space-y-2">
                        {notifications.map((n) => (
                            <Card
                                key={n.id}
                                className={`p-4 flex items-start gap-4 transition-colors group ${!n.is_read ? "border-primary/30 bg-primary/5" : ""}`}
                            >
                                <div className="mt-0.5 p-2 rounded-lg bg-paper-mid">
                                    {getIcon(n.type)}
                                </div>
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-start justify-between gap-2">
                                        <p className={`text-sm font-medium truncate ${!n.is_read ? "text-ink" : "text-ink-light"}`}>
                                            {n.title}
                                        </p>
                                        {!n.is_read && (
                                            <Badge variant="secondary" className="text-xs shrink-0 bg-primary/10 text-primary">New</Badge>
                                        )}
                                    </div>
                                    {n.body && <p className="text-xs text-muted-foreground mt-0.5 line-clamp-2">{n.body}</p>}
                                    <p className="text-xs text-muted-foreground mt-1">
                                        {formatDistanceToNow(new Date(n.created_at), { addSuffix: true })}
                                    </p>
                                </div>
                                <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity shrink-0">
                                    {!n.is_read && (
                                        <Button size="icon" variant="ghost" className="h-7 w-7" onClick={() => markRead.mutate(n.id)}>
                                            <CheckCheck className="h-3.5 w-3.5" />
                                        </Button>
                                    )}
                                    {n.action_url && (
                                        <Button size="sm" variant="outline" asChild className="h-7 text-xs">
                                            <Link href={n.action_url}>View</Link>
                                        </Button>
                                    )}
                                    <Button size="icon" variant="ghost" className="h-7 w-7 text-muted-foreground hover:text-danger" onClick={() => dismiss.mutate(n.id)}>
                                        <X className="h-3.5 w-3.5" />
                                    </Button>
                                </div>
                            </Card>
                        ))}
                    </div>
                )}
            </div>
        </AppShell>
    );
}
