"use client";

import React, { useState } from "react";
import { Shield, Download, Trash2, Save, AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";

export default function SettingsPrivacyPage() {
    const [settings, setSettings] = useState({
        dataRetention: "1year",
        emailTracking: false,
        readReceipts: true,
    });

    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

    const handleSave = () => {
        console.log("Saving privacy settings:", settings);
    };

    const handleExportData = () => {
        console.log("Exporting user data...");
    };

    const handleDeleteAccount = () => {
        console.log("Deleting account...");
    };

    return (
        <div className="max-w-4xl">
            <div className="mb-6">
                <h1 className="font-display text-2xl text-ink mb-2">Privacy Settings</h1>
                <p className="text-muted">
                    Manage your data, privacy preferences, and account security.
                </p>
            </div>

            <div className="space-y-6">
                {/* Data Retention */}
                <Card className="p-6">
                    <div className="mb-4">
                        <h3 className="font-medium text-ink mb-1">Data Retention</h3>
                        <p className="text-sm text-muted">
                            How long to keep your email data and AI analysis
                        </p>
                    </div>
                    <Select
                        value={settings.dataRetention}
                        onValueChange={(value) =>
                            setSettings({ ...settings, dataRetention: value })
                        }
                    >
                        <SelectTrigger className="w-full">
                            <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="30days">30 days</SelectItem>
                            <SelectItem value="90days">90 days</SelectItem>
                            <SelectItem value="6months">6 months</SelectItem>
                            <SelectItem value="1year">1 year</SelectItem>
                            <SelectItem value="forever">Forever</SelectItem>
                        </SelectContent>
                    </Select>
                </Card>

                {/* Email Tracking */}
                <Card className="p-6">
                    <div className="flex items-center justify-between">
                        <div className="flex-1">
                            <h3 className="font-medium text-ink mb-1">Email Tracking</h3>
                            <p className="text-sm text-muted">
                                Track when recipients open your emails
                            </p>
                        </div>
                        <Switch
                            checked={settings.emailTracking}
                            onCheckedChange={(checked) =>
                                setSettings({ ...settings, emailTracking: checked })
                            }
                        />
                    </div>
                </Card>

                {/* Read Receipts */}
                <Card className="p-6">
                    <div className="flex items-center justify-between">
                        <div className="flex-1">
                            <h3 className="font-medium text-ink mb-1">Read Receipts</h3>
                            <p className="text-sm text-muted">
                                Send read receipts when you open emails
                            </p>
                        </div>
                        <Switch
                            checked={settings.readReceipts}
                            onCheckedChange={(checked) =>
                                setSettings({ ...settings, readReceipts: checked })
                            }
                        />
                    </div>
                </Card>

                {/* Export Data */}
                <Card className="p-6">
                    <div className="flex items-start justify-between">
                        <div className="flex-1">
                            <h3 className="font-medium text-ink mb-1">Export Your Data</h3>
                            <p className="text-sm text-muted">
                                Download a copy of all your data (emails, tasks, AI analysis)
                            </p>
                        </div>
                        <Button onClick={handleExportData} variant="outline" className="gap-2">
                            <Download className="w-4 h-4" />
                            Export Data
                        </Button>
                    </div>
                </Card>

                {/* Save Button */}
                <div className="flex justify-end">
                    <Button onClick={handleSave} className="gap-2">
                        <Save className="w-4 h-4" />
                        Save Settings
                    </Button>
                </div>

                {/* Danger Zone */}
                <Card className="p-6 border-danger/20 bg-danger/5">
                    <div className="flex items-start gap-3 mb-4">
                        <AlertTriangle className="w-5 h-5 text-danger shrink-0 mt-0.5" />
                        <div className="flex-1">
                            <h3 className="font-medium text-danger mb-1">Danger Zone</h3>
                            <p className="text-sm text-muted">
                                Permanently delete your account and all associated data
                            </p>
                        </div>
                    </div>
                    {!showDeleteConfirm ? (
                        <Button
                            onClick={() => setShowDeleteConfirm(true)}
                            variant="outline"
                            className="gap-2 text-danger border-danger hover:bg-danger hover:text-white"
                        >
                            <Trash2 className="w-4 h-4" />
                            Delete Account
                        </Button>
                    ) : (
                        <div className="space-y-3">
                            <p className="text-sm font-medium text-danger">
                                Are you absolutely sure? This action cannot be undone.
                            </p>
                            <div className="flex gap-2">
                                <Button
                                    onClick={handleDeleteAccount}
                                    variant="default"
                                    className="bg-danger hover:bg-danger/90"
                                >
                                    Yes, Delete My Account
                                </Button>
                                <Button
                                    onClick={() => setShowDeleteConfirm(false)}
                                    variant="outline"
                                >
                                    Cancel
                                </Button>
                            </div>
                        </div>
                    )}
                </Card>
            </div>
        </div>
    );
}
