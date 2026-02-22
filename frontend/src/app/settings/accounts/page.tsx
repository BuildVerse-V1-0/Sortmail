"use client";

import React from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Mail, RefreshCw, Power, AlertCircle, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatDistanceToNow } from "date-fns";
import { api, endpoints } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";

interface ConnectedAccount {
    id: string;
    email: string;
    provider: string;
    status: string;
    sync_status?: string;
    last_sync_at?: string;
    created_at: string;
}

export default function SettingsAccountsPage() {
    const { user, login } = useAuth();
    const queryClient = useQueryClient();

    const { data: accounts = [], isLoading } = useQuery<ConnectedAccount[]>({
        queryKey: ["connected-accounts"],
        queryFn: async () => {
            const { data } = await api.get(endpoints.connectedAccounts);
            return data;
        },
    });

    const syncNow = useMutation({
        mutationFn: (id: string) => api.post(`${endpoints.connectedAccounts}/${id}/sync`),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ["connected-accounts"] }),
    });

    const disconnect = useMutation({
        mutationFn: (id: string) => api.post(`${endpoints.connectedAccounts}/${id}/disconnect`),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ["connected-accounts"] }),
    });

    const statusBadge = (status: string) => {
        switch (status) {
            case "active": return <Badge className="bg-success/10 text-success border-success/20">Connected</Badge>;
            case "error": return <Badge className="bg-danger/10 text-danger border-danger/20">Error</Badge>;
            case "revoked": return <Badge className="bg-warning/10 text-warning border-warning/20">Reconnect Required</Badge>;
            default: return <Badge variant="secondary">{status}</Badge>;
        }
    };

    return (
        <div className="max-w-4xl space-y-6">
            <div className="mb-6">
                <h1 className="font-display text-2xl text-ink mb-2">Email Accounts</h1>
                <p className="text-muted">Connect and manage your email accounts for syncing.</p>
            </div>

            {isLoading ? (
                <div className="space-y-4">{[1, 2].map(i => <div key={i} className="h-28 rounded-xl bg-paper-mid animate-pulse" />)}</div>
            ) : accounts.length === 0 ? (
                <Card className="p-12 text-center text-muted-foreground">
                    <Mail className="h-12 w-12 mx-auto mb-4 opacity-30" />
                    <p className="font-medium text-lg">No accounts connected</p>
                    <p className="text-sm mt-1 mb-4">Connect Gmail to start syncing your emails.</p>
                    <Button onClick={login}>Connect Gmail</Button>
                </Card>
            ) : (
                <div className="space-y-4">
                    {accounts.map(account => (
                        <Card key={account.id} className="p-6">
                            <div className="flex items-start justify-between">
                                <div className="flex items-start gap-4 flex-1">
                                    <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
                                        <Mail className="w-6 h-6 text-primary" />
                                    </div>
                                    <div className="flex-1">
                                        <div className="flex items-center gap-2 mb-1">
                                            <h3 className="font-medium text-ink">{account.email}</h3>
                                            {statusBadge(account.status)}
                                        </div>
                                        <p className="text-sm text-muted mb-1 capitalize">
                                            {account.provider === "gmail" ? "Google Workspace / Gmail" : "Microsoft 365 / Outlook"}
                                        </p>
                                        {account.last_sync_at && (
                                            <p className="text-xs text-muted">
                                                Last synced {formatDistanceToNow(new Date(account.last_sync_at), { addSuffix: true })}
                                            </p>
                                        )}
                                        {account.sync_status === "syncing" && (
                                            <p className="text-xs text-primary flex items-center gap-1 mt-1">
                                                <Loader2 className="w-3 h-3 animate-spin" /> Syncing...
                                            </p>
                                        )}
                                    </div>
                                </div>
                                <div className="flex items-center gap-2 shrink-0">
                                    <Button
                                        variant="outline" size="sm" className="gap-2"
                                        onClick={() => syncNow.mutate(account.id)}
                                        disabled={syncNow.isPending}
                                    >
                                        <RefreshCw className={`w-4 h-4 ${syncNow.isPending ? "animate-spin" : ""}`} />
                                        Sync Now
                                    </Button>
                                    <Button
                                        variant="outline" size="sm" className="gap-2 text-danger hover:bg-danger hover:text-white border-danger/30"
                                        onClick={() => {
                                            if (confirm(`Disconnect ${account.email}?`)) disconnect.mutate(account.id);
                                        }}
                                    >
                                        <Power className="w-4 h-4" />
                                        Disconnect
                                    </Button>
                                </div>
                            </div>
                        </Card>
                    ))}
                </div>
            )}

            {/* Add Account */}
            <Card className="p-6 border-dashed">
                <div className="flex items-center justify-between">
                    <div>
                        <h3 className="font-medium text-ink mb-1">Add another account</h3>
                        <p className="text-sm text-muted">Connect Gmail or Outlook to sync your emails</p>
                    </div>
                    <Button onClick={login} className="gap-2">
                        <Mail className="w-4 h-4" />
                        Connect Gmail
                    </Button>
                </div>
            </Card>

            <Card className="p-4 bg-ai-purple-soft border-ai-purple/20">
                <div className="flex gap-3">
                    <AlertCircle className="w-5 h-5 text-ai-purple shrink-0 mt-0.5" />
                    <p className="text-sm text-muted">
                        <span className="font-medium text-ink">OAuth 2.0 Secured.</span>{" "}
                        SortMail uses read-only OAuth to access your email. We never store your password and never send emails on your behalf without explicit confirmation.
                    </p>
                </div>
            </Card>
        </div>
    );
}
