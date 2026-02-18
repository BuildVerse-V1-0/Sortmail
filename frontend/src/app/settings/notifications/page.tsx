"use client";

import React, { useState } from "react";
import { Bell, Mail, Smartphone, Save, Clock } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";

export default function SettingsNotificationsPage() {
    const [settings, setSettings] = useState({
        emailNotifications: true,
        pushNotifications: true,
        notifyNewEmail: true,
        notifyTaskDue: true,
        notifyAISummary: false,
        notifyReminder: true,
        quietHoursEnabled: false,
        quietHoursStart: "22:00",
        quietHoursEnd: "08:00",
    });

    const handleSave = () => {
        console.log("Saving notification settings:", settings);
    };

    return (
        <div className="max-w-4xl">
            <div className="mb-6">
                <h1 className="font-display text-2xl text-ink mb-2">Notification Settings</h1>
                <p className="text-muted">
                    Control how and when you receive notifications from SortMail.
                </p>
            </div>

            <div className="space-y-6">
                {/* Channels */}
                <Card className="p-6">
                    <h3 className="font-medium text-ink mb-4">Notification Channels</h3>
                    <div className="space-y-4">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <Mail className="w-5 h-5 text-muted" />
                                <div>
                                    <Label className="font-medium text-ink">Email Notifications</Label>
                                    <p className="text-sm text-muted">Receive notifications via email</p>
                                </div>
                            </div>
                            <Switch
                                checked={settings.emailNotifications}
                                onCheckedChange={(checked) =>
                                    setSettings({ ...settings, emailNotifications: checked })
                                }
                            />
                        </div>
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <Smartphone className="w-5 h-5 text-muted" />
                                <div>
                                    <Label className="font-medium text-ink">Push Notifications</Label>
                                    <p className="text-sm text-muted">Receive push notifications in browser</p>
                                </div>
                            </div>
                            <Switch
                                checked={settings.pushNotifications}
                                onCheckedChange={(checked) =>
                                    setSettings({ ...settings, pushNotifications: checked })
                                }
                            />
                        </div>
                    </div>
                </Card>

                {/* Notification Types */}
                <Card className="p-6">
                    <h3 className="font-medium text-ink mb-4">Notification Types</h3>
                    <div className="space-y-4">
                        {[
                            { key: "notifyNewEmail", label: "New Emails", desc: "Get notified for new urgent emails" },
                            { key: "notifyTaskDue", label: "Task Due", desc: "Reminders when tasks are due" },
                            { key: "notifyAISummary", label: "AI Summaries", desc: "Daily AI briefing ready" },
                            { key: "notifyReminder", label: "Follow-up Reminders", desc: "Reminders for follow-ups" },
                        ].map((item) => (
                            <div key={item.key} className="flex items-center justify-between">
                                <div>
                                    <Label className="font-medium text-ink">{item.label}</Label>
                                    <p className="text-sm text-muted">{item.desc}</p>
                                </div>
                                <Switch
                                    checked={settings[item.key as keyof typeof settings] as boolean}
                                    onCheckedChange={(checked) =>
                                        setSettings({ ...settings, [item.key]: checked })
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
                                <p className="text-sm text-muted">Pause notifications during specific hours</p>
                            </div>
                        </div>
                        <Switch
                            checked={settings.quietHoursEnabled}
                            onCheckedChange={(checked) =>
                                setSettings({ ...settings, quietHoursEnabled: checked })
                            }
                        />
                    </div>
                    {settings.quietHoursEnabled && (
                        <div className="grid grid-cols-2 gap-4 pt-4 border-t border-border">
                            <div>
                                <Label className="text-sm text-muted mb-2 block">Start Time</Label>
                                <Input
                                    type="time"
                                    value={settings.quietHoursStart}
                                    onChange={(e) =>
                                        setSettings({ ...settings, quietHoursStart: e.target.value })
                                    }
                                />
                            </div>
                            <div>
                                <Label className="text-sm text-muted mb-2 block">End Time</Label>
                                <Input
                                    type="time"
                                    value={settings.quietHoursEnd}
                                    onChange={(e) =>
                                        setSettings({ ...settings, quietHoursEnd: e.target.value })
                                    }
                                />
                            </div>
                        </div>
                    )}
                </Card>

                {/* Save Button */}
                <div className="flex justify-end">
                    <Button onClick={handleSave} className="gap-2">
                        <Save className="w-4 h-4" />
                        Save Settings
                    </Button>
                </div>
            </div>
        </div>
    );
}
