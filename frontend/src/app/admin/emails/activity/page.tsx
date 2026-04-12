'use client';

import React, { useMemo, useState } from 'react';
import {
    CheckCircle2,
    Clock,
    AlertCircle,
    Search,
    Filter,
    ArrowLeft,
    RefreshCcw,
    Zap,
} from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import Link from 'next/link';
import { api, endpoints } from '@/lib/api';

type UsageRow = {
    id: string;
    created_at: string | null;
    user_email?: string | null;
    user_name?: string | null;
    user_id: string;
    operation_type: string;
    related_entity_type?: string | null;
    related_entity_id?: string | null;
    related_entity_preview?: Record<string, unknown> | null;
    latency_ms?: number | null;
    error_occurred: boolean;
    error_type?: string | null;
    model_name: string;
};

type UsageResponse = {
    totals: {
        calls: number;
        errors: number;
        error_rate_pct: number;
    };
    records: UsageRow[];
};

type QueueResponse = {
    enabled: boolean;
    pending_items: number | null;
};

export default function EmailActivityPage() {
    const [query, setQuery] = useState('');

    const usageQuery = useQuery<UsageResponse>({
        queryKey: ['admin-email-activity-usage', 24],
        queryFn: async () => {
            const response = await api.get(endpoints.adminMetricsAIUsage, { params: { hours: 24, limit: 300 } });
            return response.data;
        },
        refetchInterval: 30000,
        staleTime: 10000,
    });

    const queueQuery = useQuery<QueueResponse>({
        queryKey: ['admin-email-activity-queue'],
        queryFn: async () => {
            const response = await api.get(endpoints.adminMetricsQueue);
            return response.data;
        },
        refetchInterval: 30000,
        staleTime: 10000,
    });

    const rows = usageQuery.data?.records || [];

    const filteredRows = useMemo(() => {
        const q = query.trim().toLowerCase();
        if (!q) return rows;
        return rows.filter((row) => {
            const who = (row.user_email || row.user_name || row.user_id || '').toLowerCase();
            const op = (row.operation_type || '').toLowerCase();
            const model = (row.model_name || '').toLowerCase();
            const subject = String((row.related_entity_preview || {}).subject || '').toLowerCase();
            const entity = String(row.related_entity_id || '').toLowerCase();
            return who.includes(q) || op.includes(q) || model.includes(q) || subject.includes(q) || entity.includes(q);
        });
    }, [rows, query]);

    const avgLatency = useMemo(() => {
        const vals = filteredRows.map((r) => Number(r.latency_ms || 0)).filter((v) => v > 0);
        if (!vals.length) return 0;
        return Math.round(vals.reduce((a, b) => a + b, 0) / vals.length);
    }, [filteredRows]);

    const successRate = useMemo(() => {
        const total = usageQuery.data?.totals.calls || 0;
        if (!total) return 0;
        const errors = usageQuery.data?.totals.errors || 0;
        return Math.max(0, Math.min(100, ((total - errors) / total) * 100));
    }, [usageQuery.data]);

    const onRefresh = async () => {
        await Promise.all([usageQuery.refetch(), queueQuery.refetch()]);
    };

    return (
        <div className="p-8 max-w-7xl mx-auto space-y-8 animate-in fade-in duration-500">
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
                <div className="space-y-4">
                    <Link href="/admin" className="flex items-center gap-2 text-xs font-mono font-bold text-accent hover:opacity-70 transition-opacity uppercase tracking-widest">
                        <ArrowLeft size={12} /> Admin Home
                    </Link>
                    <div>
                        <h1 className="text-3xl font-display text-ink mb-1">Email Processing Activity</h1>
                        <p className="text-ink-light text-sm">Live monitoring of sync and AI processing activity from the last 24 hours.</p>
                    </div>
                </div>
                <Button variant="outline" onClick={onRefresh} className="h-10 border-border-light text-ink text-xs font-bold uppercase tracking-wider shadow-sm">
                    <RefreshCcw size={14} className={`mr-2 ${(usageQuery.isFetching || queueQuery.isFetching) ? 'animate-spin' : ''}`} /> Refresh
                </Button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <ActivityStat
                    label="Success Rate"
                    value={`${successRate.toFixed(2)}%`}
                    sub={`${usageQuery.data?.totals.calls || 0} calls / 24h`}
                    icon={CheckCircle2}
                    color="text-success"
                />
                <ActivityStat
                    label="Avg Latency"
                    value={avgLatency ? `${avgLatency} ms` : '--'}
                    sub="Across filtered rows"
                    icon={Clock}
                    color="text-info"
                />
                <ActivityStat
                    label="AI Queue"
                    value={queueQuery.data?.enabled ? `${queueQuery.data?.pending_items ?? 0} items` : 'disabled'}
                    sub="Pending intelligence work"
                    icon={Zap}
                    color="text-ai"
                />
            </div>

            <Card className="border-border-light bg-white shadow-sm ring-1 ring-black/5">
                <CardContent className="p-4 flex flex-col md:flex-row gap-4 items-center">
                    <div className="relative flex-1 w-full">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                        <Input
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            placeholder="Search by user, subject, operation, model, or entity..."
                            className="pl-10 h-10 border-border-light focus-visible:ring-accent"
                        />
                    </div>
                    <Button variant="outline" disabled className="h-10 gap-2 border-border-light text-ink w-full md:w-auto" title="Additional filters will be added next">
                        <Filter size={14} /> Filters
                    </Button>
                </CardContent>
            </Card>

            <Card className="border-border-light bg-white overflow-hidden shadow-sm">
                <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                        <thead className="bg-paper-mid border-b border-border-light text-[10px] font-mono text-muted-foreground uppercase tracking-widest">
                            <tr>
                                <th className="px-6 py-4 font-bold">Processed At</th>
                                <th className="px-6 py-4 font-bold">User</th>
                                <th className="px-6 py-4 font-bold">Thread/Subject</th>
                                <th className="px-6 py-4 font-bold">Operation</th>
                                <th className="px-6 py-4 font-bold">Latency</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-border-light">
                            {filteredRows.map((log) => (
                                <tr key={log.id} className="hover:bg-paper-mid/50 transition-colors group">
                                    <td className="px-6 py-4 text-xs font-mono text-ink-mid">
                                        {log.created_at ? new Date(log.created_at).toLocaleString() : '-'}
                                    </td>
                                    <td className="px-6 py-4">
                                        <span className="text-sm font-medium text-ink">{log.user_email || log.user_name || log.user_id}</span>
                                    </td>
                                    <td className="px-6 py-4 max-w-sm">
                                        <p className="text-sm text-ink-mid truncate">{String((log.related_entity_preview || {}).subject || log.related_entity_id || '-')}</p>
                                    </td>
                                    <td className="px-6 py-4">
                                        <StatusBadge status={log.error_occurred ? 'Error' : 'Analyzed'} detail={log.operation_type} />
                                    </td>
                                    <td className="px-6 py-4">
                                        <span className={`text-[10px] font-mono font-bold ${(log.latency_ms || 0) > 5000 ? 'text-danger' : 'text-ink-light'}`}>
                                            {log.latency_ms ? `${log.latency_ms} ms` : '--'}
                                        </span>
                                    </td>
                                </tr>
                            ))}
                            {!usageQuery.isLoading && filteredRows.length === 0 && (
                                <tr>
                                    <td colSpan={5} className="px-6 py-10 text-center text-sm text-ink-light">No email activity available.</td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </Card>
        </div>
    );
}

function ActivityStat({ label, value, sub, icon: Icon, color }: { label: string; value: string; sub: string; icon: any; color: string }) {
    return (
        <Card className="border-border-light shadow-sm">
            <CardContent className="p-5 flex items-center gap-4">
                <div className="w-12 h-12 rounded-2xl bg-paper-mid flex items-center justify-center shrink-0">
                    <Icon size={20} className={color} />
                </div>
                <div>
                    <h4 className="text-[10px] font-mono font-bold text-muted-foreground uppercase tracking-widest">{label}</h4>
                    <p className="text-xl font-display text-ink mt-0.5">{value}</p>
                    <p className="text-[10px] text-ink-light mt-0.5 font-mono">{sub}</p>
                </div>
            </CardContent>
        </Card>
    );
}

function StatusBadge({ status, detail }: { status: string; detail?: string }) {
    const styles: Record<string, string> = {
        Analyzed: 'bg-ai/10 text-ai border-ai/20',
        Synced: 'bg-success/10 text-success border-success/20',
        Error: 'bg-danger/10 text-danger border-danger/20',
        Deleted: 'bg-paper-mid text-ink-light border-border-light',
    };
    return (
        <span className={`text-[10px] font-mono font-bold uppercase px-2 py-0.5 rounded border flex items-center gap-1.5 w-fit ${styles[status] || styles.Analyzed}`} title={detail || status}>
            {status === 'Error' && <AlertCircle size={10} />}
            {status}
        </span>
    );
}
