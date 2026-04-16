"use client";

import React from "react";
import { useQuery } from "@tanstack/react-query";
import { Globe, Link2, BookText, Activity, ExternalLink, Shield } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { api, endpoints } from "@/lib/api";
import { config } from "@/lib/config";

export default function DeveloperSettingsPage() {
    const apiBase = config.apiUrl || (typeof window !== "undefined" ? window.location.origin : "");

    const { data: appStatus } = useQuery<any>({
        queryKey: ["app-status", "settings-dev"],
        queryFn: async () => {
            const { data } = await api.get(endpoints.appStatus);
            return data;
        },
        retry: 0,
    });

    return (
        <div className="max-w-5xl space-y-8">
            <div>
                <h1 className="font-display text-3xl text-ink font-bold">Developer</h1>
                <p className="text-ink-light mt-2">Runtime endpoints and integration references for your workspace.</p>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Globe className="w-5 h-5 text-primary" /> API Base URL
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <code className="text-sm bg-paper-mid px-3 py-2 rounded block overflow-x-auto">{apiBase}</code>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Activity className="w-5 h-5 text-primary" /> Service Health
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="flex items-center gap-2">
                        <Badge variant={appStatus?.status === "ok" ? "secondary" : "outline"}>
                            {appStatus?.status || "unknown"}
                        </Badge>
                        <span className="text-sm text-ink-light">from {endpoints.appStatus}</span>
                    </CardContent>
                </Card>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Link2 className="w-5 h-5 text-primary" /> Integration Endpoints
                    </CardTitle>
                    <CardDescription>Stable endpoints commonly used for automation and integrations.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-2 text-sm">
                    <EndpointRow label="Webhooks" value="/api/webhooks" />
                    <EndpointRow label="Event Stream" value={endpoints.eventStream} />
                    <EndpointRow label="Search" value={endpoints.search} />
                    <EndpointRow label="Connected Accounts" value={endpoints.connectedAccounts} />
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <BookText className="w-5 h-5 text-primary" /> Documentation
                    </CardTitle>
                    <CardDescription>Use OpenAPI docs and project guides for implementation details.</CardDescription>
                </CardHeader>
                <CardContent className="flex flex-wrap gap-3">
                    <a href={`${apiBase.replace(/\/$/, "")}/docs`} target="_blank" rel="noreferrer">
                        <Button variant="outline" className="gap-2">Open API Docs <ExternalLink className="w-4 h-4" /></Button>
                    </a>
                    <a href="/help" target="_blank" rel="noreferrer">
                        <Button variant="outline" className="gap-2">Execution Guide <ExternalLink className="w-4 h-4" /></Button>
                    </a>
                </CardContent>
            </Card>

            <Card className="border-primary/20 bg-primary/5">
                <CardContent className="p-5 text-sm text-ink-light flex items-start gap-3">
                    <Shield className="w-4 h-4 mt-0.5 text-primary" />
                    Developer secrets are not exposed in this UI. Use server-side environment management and admin flows for key lifecycle operations.
                </CardContent>
            </Card>
        </div>
    );
}

function EndpointRow({ label, value }: { label: string; value: string }) {
    return (
        <div className="flex items-center justify-between gap-3 border border-border-light rounded-lg px-3 py-2">
            <span className="text-ink">{label}</span>
            <code className="text-xs bg-paper-mid px-2 py-1 rounded">{value}</code>
        </div>
    );
}
