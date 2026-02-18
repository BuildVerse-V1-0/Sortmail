"use client";

import React, { useState } from "react";
import { Mail, Plus, RefreshCw, Power, Check, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";

interface EmailAccount {
    id: string;
    email: string;
    provider: "gmail" | "outlook";
    status: "connected" | "error" | "syncing";
    syncEnabled: boolean;
    lastSync: string;
}

const mockAccounts: EmailAccount[] = [
    {
        id: "1",
        email: "isabella.rodriguez@gmail.com",
        provider: "gmail",
        status: "connected",
        syncEnabled: true,
        lastSync: "2026-02-17T10:30:00",
    },
    {
        id: "2",
        email: "i.rodriguez@company.com",
        provider: "outlook",
        status: "connected",
        syncEnabled: true,
        lastSync: "2026-02-17T10:28:00",
    },
];

export default function SettingsAccountsPage() {
    const [accounts, setAccounts] = useState(mockAccounts);

    const toggleSync = (id: string) => {
        setAccounts((prev) =>
            prev.map((acc) =>
                acc.id === id ? { ...acc, syncEnabled: !acc.syncEnabled } : acc
            )
        );
    };

    const getStatusBadge = (status: string) => {
        switch (status) {
            case "connected":
                return <Badge className="bg-success text-white">Connected</Badge>;
            case "error":
                return <Badge className="bg-danger text-white">Error</Badge>;
            case "syncing":
                return <Badge className="bg-warning text-white">Syncing...</Badge>;
            default:
                return null;
        }
    };

    return (
        <div className="max-w-4xl">
            <div className="mb-6">
                <h1 className="font-display text-2xl text-ink mb-2">Email Accounts</h1>
                <p className="text-muted">
                    Connect and manage your email accounts. SortMail supports Gmail and Outlook.
                </p>
            </div>

            {/* Connected Accounts */}
            <div className="space-y-4 mb-6">
                {accounts.map((account) => (
                    <Card key={account.id} className="p-6">
                        <div className="flex items-start justify-between">
                            <div className="flex items-start gap-4 flex-1">
                                <div className="w-12 h-12 rounded-lg bg-accent/10 flex items-center justify-center shrink-0">
                                    <Mail className="w-6 h-6 text-accent" />
                                </div>
                                <div className="flex-1">
                                    <div className="flex items-center gap-2 mb-1">
                                        <h3 className="font-medium text-ink">{account.email}</h3>
                                        {getStatusBadge(account.status)}
                                    </div>
                                    <p className="text-sm text-muted mb-3">
                                        {account.provider === "gmail" ? "Google Workspace" : "Microsoft 365"}
                                    </p>
                                    <div className="flex items-center gap-4 text-xs text-muted">
                                        <span>
                                            Last synced: {new Date(account.lastSync).toLocaleString()}
                                        </span>
                                    </div>
                                </div>
                            </div>
                            <div className="flex items-center gap-3">
                                <div className="flex items-center gap-2">
                                    <span className="text-sm text-muted">Sync</span>
                                    <Switch
                                        checked={account.syncEnabled}
                                        onCheckedChange={() => toggleSync(account.id)}
                                    />
                                </div>
                                <Button variant="outline" size="sm" className="gap-2">
                                    <RefreshCw className="w-4 h-4" />
                                    Re-auth
                                </Button>
                                <Button variant="outline" size="sm" className="gap-2 text-danger hover:bg-danger hover:text-white">
                                    <Power className="w-4 h-4" />
                                    Disconnect
                                </Button>
                            </div>
                        </div>
                    </Card>
                ))}
            </div>

            {/* Add Account */}
            <Card className="p-6 border-dashed">
                <div className="flex items-center justify-between">
                    <div>
                        <h3 className="font-medium text-ink mb-1">Add another account</h3>
                        <p className="text-sm text-muted">
                            Connect Gmail or Outlook to sync your emails
                        </p>
                    </div>
                    <Button className="gap-2">
                        <Plus className="w-4 h-4" />
                        Add Account
                    </Button>
                </div>
            </Card>

            {/* Info */}
            <Card className="p-4 mt-6 bg-ai-purple-soft border-ai-purple/20">
                <div className="flex gap-3">
                    <AlertCircle className="w-5 h-5 text-ai-purple shrink-0 mt-0.5" />
                    <div>
                        <p className="text-sm text-ink mb-1 font-medium">OAuth Authentication</p>
                        <p className="text-sm text-muted">
                            SortMail uses secure OAuth 2.0 to connect to your email. We never store your password.
                        </p>
                    </div>
                </div>
            </Card>
        </div>
    );
}
