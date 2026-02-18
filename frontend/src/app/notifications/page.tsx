"use client";

import React, { useState } from "react";
import { Bell, CheckCheck, X, Mail, CheckSquare, Sparkles, Clock, Settings as SettingsIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";
import AppShell from "@/components/layout/AppShell";

interface Notification {
    id: string;
    type: "email" | "task" | "ai_summary" | "reminder";
    title: string;
    message: string;
    timestamp: string;
    read: boolean;
    link?: string;
}

const mockNotifications: Notification[] = [
    {
        id: "1",
        type: "email",
        title: "New urgent email from Sarah Chen",
        message: "Q3 budget sign-off needed by Wednesday",
        timestamp: "2026-02-17T10:30:00",
        read: false,
        link: "/inbox/thread-1",
    },
    {
        id: "2",
        type: "task",
        title: "Task due today",
        message: "Review contract from StreamlineAI",
        timestamp: "2026-02-17T09:00:00",
        read: false,
        link: "/tasks",
    },
    {
        id: "3",
        type: "ai_summary",
        title: "AI summary ready",
        message: "Your daily briefing is ready with 2 high-priority items",
        timestamp: "2026-02-17T08:00:00",
        read: true,
        link: "/dashboard",
    },
    {
        id: "4",
        type: "reminder",
        title: "Follow-up reminder",
        message: "Check on server downtime issue",
        timestamp: "2026-02-16T16:00:00",
        read: true,
        link: "/followups",
    },
    {
        id: "5",
        type: "email",
        title: "New email from Mike Johnson",
        message: "Project timeline update",
        timestamp: "2026-02-16T14:30:00",
        read: true,
        link: "/inbox/thread-2",
    },
];

export default function NotificationsPage() {
    const [notifications, setNotifications] = useState(mockNotifications);

    const unreadCount = notifications.filter((n) => !n.read).length;

    const markAsRead = (id: string) => {
        setNotifications((prev) =>
            prev.map((n) => (n.id === id ? { ...n, read: true } : n))
        );
    };

    const markAllAsRead = () => {
        setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
    };

    const clearAll = () => {
        setNotifications([]);
    };

    const getNotificationIcon = (type: string) => {
        switch (type) {
            case "email":
                return <Mail className="w-4 h-4" />;
            case "task":
                return <CheckSquare className="w-4 h-4" />;
            case "ai_summary":
                return <Sparkles className="w-4 h-4" />;
            case "reminder":
                return <Clock className="w-4 h-4" />;
            default:
                return <Bell className="w-4 h-4" />;
        }
    };

    const getNotificationColor = (type: string) => {
        switch (type) {
            case "email":
                return "bg-accent/10 text-accent";
            case "task":
                return "bg-success/10 text-success";
            case "ai_summary":
                return "bg-ai-purple/10 text-ai-purple";
            case "reminder":
                return "bg-warning/10 text-warning";
            default:
                return "bg-muted/10 text-muted";
        }
    };

    const groupByDate = (notifications: Notification[]) => {
        const groups: Record<string, Notification[]> = {};
        notifications.forEach((notification) => {
            const date = new Date(notification.timestamp).toDateString();
            if (!groups[date]) {
                groups[date] = [];
            }
            groups[date].push(notification);
        });
        return groups;
    };

    const groupedNotifications = groupByDate(notifications);

    const getRelativeTime = (timestamp: string) => {
        const now = new Date();
        const then = new Date(timestamp);
        const diffMs = now.getTime() - then.getTime();
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMins / 60);
        const diffDays = Math.floor(diffHours / 24);

        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        return `${diffDays}d ago`;
    };

    return (
        <AppShell title="Notifications">
            <div className="flex flex-col h-full bg-paper">
                {/* Header */}
                <div className="border-b border-border bg-white px-8 py-6">
                    <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-3">
                            <Bell className="w-6 h-6 text-muted" />
                            <h1 className="font-display text-2xl text-ink">Notifications</h1>
                            {unreadCount > 0 && (
                                <Badge variant="default" className="bg-accent">
                                    {unreadCount} new
                                </Badge>
                            )}
                        </div>
                        <div className="flex items-center gap-2">
                            <Link href="/settings/notifications">
                                <Button variant="outline" size="sm" className="gap-2">
                                    <SettingsIcon className="w-4 h-4" />
                                    Settings
                                </Button>
                            </Link>
                            {unreadCount > 0 && (
                                <Button variant="outline" size="sm" onClick={markAllAsRead} className="gap-2">
                                    <CheckCheck className="w-4 h-4" />
                                    Mark all read
                                </Button>
                            )}
                            {notifications.length > 0 && (
                                <Button variant="outline" size="sm" onClick={clearAll} className="gap-2 text-danger hover:bg-danger hover:text-white">
                                    <X className="w-4 h-4" />
                                    Clear all
                                </Button>
                            )}
                        </div>
                    </div>
                </div>

                {/* Notifications List */}
                <div className="flex-1 overflow-y-auto px-8 py-6">
                    {notifications.length === 0 ? (
                        <div className="flex flex-col items-center justify-center h-full text-center">
                            <Bell className="w-16 h-16 text-muted mb-4" />
                            <h2 className="font-display text-xl text-ink mb-2">
                                No notifications
                            </h2>
                            <p className="text-muted max-w-md">
                                You&apos;re all caught up! We&apos;ll notify you when something important happens.
                            </p>
                        </div>
                    ) : (
                        <div className="max-w-3xl space-y-6">
                            {Object.entries(groupedNotifications).map(([date, notifs]) => (
                                <div key={date}>
                                    <h2 className="text-xs text-muted font-mono uppercase tracking-wide mb-3">
                                        {new Date(date).toDateString() === new Date().toDateString()
                                            ? "Today"
                                            : new Date(date).toDateString() === new Date(Date.now() - 86400000).toDateString()
                                                ? "Yesterday"
                                                : new Date(date).toLocaleDateString()}
                                    </h2>
                                    <div className="space-y-2">
                                        {notifs.map((notification) => (
                                            <Card
                                                key={notification.id}
                                                className={`p-4 transition-all ${!notification.read ? "bg-accent/5 border-accent/20" : ""
                                                    }`}
                                            >
                                                <div className="flex items-start gap-3">
                                                    <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${getNotificationColor(notification.type)}`}>
                                                        {getNotificationIcon(notification.type)}
                                                    </div>
                                                    <div className="flex-1 min-w-0">
                                                        <div className="flex items-start justify-between gap-2 mb-1">
                                                            <h3 className={`font-medium ${!notification.read ? "text-ink" : "text-ink-mid"}`}>
                                                                {notification.title}
                                                            </h3>
                                                            <span className="text-xs text-muted shrink-0">
                                                                {getRelativeTime(notification.timestamp)}
                                                            </span>
                                                        </div>
                                                        <p className="text-sm text-muted mb-2">
                                                            {notification.message}
                                                        </p>
                                                        <div className="flex items-center gap-2">
                                                            {notification.link && (
                                                                <Link href={notification.link}>
                                                                    <Button variant="ghost" size="sm" className="h-7 text-xs">
                                                                        View
                                                                    </Button>
                                                                </Link>
                                                            )}
                                                            {!notification.read && (
                                                                <Button
                                                                    variant="ghost"
                                                                    size="sm"
                                                                    onClick={() => markAsRead(notification.id)}
                                                                    className="h-7 text-xs"
                                                                >
                                                                    Mark as read
                                                                </Button>
                                                            )}
                                                        </div>
                                                    </div>
                                                </div>
                                            </Card>
                                        ))}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </AppShell>
    );
}
