"use client";

import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Bell, Mail, Smartphone, Save, Clock, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { api, endpoints } from "@/lib/api";

interface NotifPrefs {
    email_enabled: boolean;
    push_enabled: boolean;
    in_app_enabled: boolean;
    channels: Record<string, boolean>;
    quiet_hours_start?: string;
    quiet_hours_end?: string;
    quiet_hours_timezone?: string;
}

const CHANNEL_LABELS: Record<string, { label: string; desc: string }> = {
    email_urgent: { label: "Urgent Email Alerts", desc: "Get notified for high-priority emails" },
    follow_up_reminder: { label: "Follow-up Reminders", desc: "Reminders when you need to follow up" },
    task_due: { label: "Task Due Dates", desc: "Alerts when tasks are due" },
    credit_low: { label: "Low Credit Warning", desc: "Alert when credits fall below threshold" },
    account_update: { label: "Account Updates", desc: "Gmail reconnection or sync issues" },
};

export default function SettingsNotificationsPage() {
    const queryClient = useQueryClient();
    const [saved, setSaved] = useState(false);

    const { data: prefs, isLoading } = useQuery<NotifPrefs>({
        queryKey: ["notification-prefs"],
        queryFn: async () => {
            const { data } = await api.get(endpoints.notificationPrefs);
            return data;
        },
    });

    const [local, setLocal] = useState<Partial<NotifPrefs>>({});

    // Merge API data into local state on first load
    const merged = { ...prefs, ...local } as NotifPrefs;

    const save = useMutation({
        mutationFn: () => api.patch(endpoints.notificationPrefs, local),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["notification-prefs"] });
            setSaved(true);
            setTimeout(() => setSaved(false), 3000);
            setLocal({});
        },
    });

    const update = (patch: Partial<NotifPrefs>) => {
        setLocal(p => ({ ...p, ...patch }));
    };

    if (isLoading) {
        return <div className="max-w-4xl space-y-4">{[1, 2, 3].map(i => <div key={i} className="h-28 rounded-xl bg-paper-mid animate-pulse" />)}</div>;
    }

    return (
        <div className="max-w-4xl space-y-6">
            <div className="mb-6">
                <h1 className="font-display text-2xl text-ink mb-2">Notification Settings</h1>
                <p className="text-muted">Control how and when SortMail notifies you.</p>
            </div>

            {/* Channels */}
            <Card className="p-6">
                <h3 className="font-medium text-ink mb-4">Delivery Channels</h3>
                <div className="space-y-4">
                    {[
                        { key: "email_enabled" as const, icon: <Mail className="w-5 h-5 text-muted" />, label: "Email Notifications", desc: "Receive notifications via email" },
                        { key: "push_enabled" as const, icon: <Smartphone className="w-5 h-5 text-muted" />, label: "Push Notifications", desc: "Browser push notifications" },
                        { key: "in_app_enabled" as const, icon: <Bell className="w-5 h-5 text-muted" />, label: "In-App Notifications", desc: "Notification center inside SortMail" },
                    ].map(item => (
                        <div key={item.key} className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                {item.icon}
                                <div>
                                    <Label className="font-medium text-ink">{item.label}</Label>
                                    <p className="text-sm text-muted">{item.desc}</p>
                                </div>
                            </div>
                            <Switch
                                checked={merged[item.key] ?? true}
                                onCheckedChange={(v) => update({ [item.key]: v })}
                            />
                        </div>
                    ))}
                </div>
            </Card>

            {/* Notification Types */}
            <Card className="p-6">
                <h3 className="font-medium text-ink mb-4">Notification Types</h3>
                <div className="space-y-4">
                    {Object.entries(CHANNEL_LABELS).map(([key, { label, desc }]) => (
                        <div key={key} className="flex items-center justify-between">
                            <div>
                                <Label className="font-medium text-ink">{label}</Label>
                                <p className="text-sm text-muted">{desc}</p>
                            </div>
                            <Switch
                                checked={merged.channels?.[key] ?? true}
                                onCheckedChange={(v) =>
                                    update({ channels: { ...(merged.channels || {}), [key]: v } })
                                }
                            />
                        </div>
                    ))}
                </div>
            </Card>

            {/* Quiet Hours */}
            <Card className="p-6">
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                        <Clock className="w-5 h-5 text-muted" />
                        <div>
                            <h3 className="font-medium text-ink">Quiet Hours</h3>
                            <p className="text-sm text-muted">Pause email/push notifications during these hours</p>
                        </div>
                    </div>
                    <Switch
                        checked={!!(merged.quiet_hours_start)}
                        onCheckedChange={(v) =>
                            update({ quiet_hours_start: v ? "22:00" : undefined, quiet_hours_end: v ? "08:00" : undefined })
                        }
                    />
                </div>
                {merged.quiet_hours_start && (
                    <div className="grid grid-cols-2 gap-4 pt-4 border-t border-border">
                        <div>
                            <Label className="text-sm text-muted mb-2 block">Start Time</Label>
                            <Input type="time" value={merged.quiet_hours_start || "22:00"}
                                onChange={e => update({ quiet_hours_start: e.target.value })} />
                        </div>
                        <div>
                            <Label className="text-sm text-muted mb-2 block">End Time</Label>
                            <Input type="time" value={merged.quiet_hours_end || "08:00"}
                                onChange={e => update({ quiet_hours_end: e.target.value })} />
                        </div>
                    </div>
                )}
            </Card>

            {/* Save */}
            <div className="flex justify-end gap-3">
                {saved && (
                    <div className="flex items-center gap-2 text-success text-sm">
                        <Check className="w-4 h-4" /> Saved!
                    </div>
                )}
                <Button onClick={() => save.mutate()} disabled={save.isPending || Object.keys(local).length === 0} className="gap-2">
                    <Save className="w-4 h-4" />
                    {save.isPending ? "Saving..." : "Save Settings"}
                </Button>
            </div>
        </div>
    );
}
