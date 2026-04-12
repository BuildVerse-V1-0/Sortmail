'use client';

import React, { useMemo, useState } from 'react';
import Link from 'next/link';
import { useQuery } from '@tanstack/react-query';
import {
    ArrowLeft,
    RefreshCw,
    Cpu,
    Coins,
    DollarSign,
    Triangle,
    TrendingUp,
    Layers,
    Activity,
    LucideIcon,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
} from '@/components/ui/dialog';
import { api, endpoints } from '@/lib/api';

type AIUsageRecord = {
    id: string;
    created_at: string | null;
    user_id: string;
    user_email?: string | null;
    user_name?: string | null;
    user_plan?: string | null;
    operation_type: string;
    model_name: string;
    provider: string | null;
    tokens_input: number;
    tokens_output: number;
    tokens_total: number;
    cost_cents: number;
    credits_charged: number;
    latency_ms: number | null;
    related_entity_type?: string | null;
    related_entity_id?: string | null;
    related_entity_preview?: Record<string, unknown> | null;
    request_id?: string | null;
    error_occurred: boolean;
    error_type: string | null;
    token_source?: string | null;
    cache_hit?: boolean;
    provider_cost_usd?: number;
    user_billable_usd?: number;
    implied_margin_usd?: number;
    charged_milli_credits?: number;
    balance_after?: number | null;
    charge_error?: string | null;
    metadata?: Record<string, unknown>;
};

type AIUsageResponse = {
    window: { hours: number; since: string };
    totals: {
        calls: number;
        tokens_input: number;
        tokens_output: number;
        tokens_total: number;
        cost_cents: number;
        errors: number;
        avg_tokens_per_call: number;
        error_rate_pct: number;
    };
    bedrock: {
        calls: number;
        tokens_total: number;
        errors: number;
        error_rate_pct: number;
    };
    by_model: Array<{
        model_name: string;
        calls: number;
        tokens_total: number;
        avg_latency_ms: number;
        errors: number;
    }>;
    by_operation: Array<{
        operation_type: string;
        calls: number;
        tokens_total: number;
        cost_cents: number;
    }>;
    records: AIUsageRecord[];
};

type EconomicsResponse = {
    window: { days: number; since: string };
    totals: {
        calls: number;
        tokens_total: number;
        credits_charged: number;
        provider_cost_usd: number;
        user_billable_usd: number;
        implied_margin_usd: number;
        charge_failures: number;
    };
    financials: {
        active_subscriptions: number;
        subscription_revenue_usd: number;
        credit_purchase_revenue_usd: number;
        free_plan_burn_usd: number;
        paid_plan_provider_cost_usd: number;
        paid_plan_implied_usage_margin_usd: number;
    };
    by_plan: Record<string, {
        calls: number;
        tokens_total: number;
        credits_charged: number;
        provider_cost_usd: number;
        user_billable_usd: number;
        implied_margin_usd: number;
    }>;
};

type EconomicsTrendResponse = {
    window: { days: number; since: string };
    series: Array<{
        date: string;
        plan: string;
        calls: number;
        tokens_total: number;
        credits_charged: number;
        provider_cost_usd: number;
        user_billable_usd: number;
        implied_margin_usd: number;
    }>;
};

function n(value: number): string {
    return new Intl.NumberFormat().format(value || 0);
}

function usd(value: number): string {
    return `$${(value || 0).toFixed(2)}`;
}

function num(value: number): string {
    return (value || 0).toFixed(2);
}

export default function AIUsagePage() {
    const [hours, setHours] = useState(24);
    const [days, setDays] = useState(30);
    const [selectedRecord, setSelectedRecord] = useState<AIUsageRecord | null>(null);

    const usageQuery = useQuery<AIUsageResponse>({
        queryKey: ['admin-ai-usage-v2', hours],
        queryFn: async () => {
            const response = await api.get(endpoints.adminMetricsAIUsage, {
                params: { hours, limit: 200 },
            });
            return response.data;
        },
        refetchInterval: 30000,
        staleTime: 10000,
    });

    const economicsQuery = useQuery<EconomicsResponse>({
        queryKey: ['admin-ai-economics', days],
        queryFn: async () => {
            const response = await api.get(endpoints.adminMetricsEconomics, { params: { days } });
            return response.data;
        },
        refetchInterval: 30000,
        staleTime: 10000,
    });

    const trendsQuery = useQuery<EconomicsTrendResponse>({
        queryKey: ['admin-ai-economics-trends', days],
        queryFn: async () => {
            const response = await api.get(endpoints.adminMetricsEconomicsTrends, { params: { days } });
            return response.data;
        },
        refetchInterval: 30000,
        staleTime: 10000,
    });

    const isLoading = usageQuery.isLoading || economicsQuery.isLoading || trendsQuery.isLoading;
    const isFetching = usageQuery.isFetching || economicsQuery.isFetching || trendsQuery.isFetching;
    const isError = usageQuery.isError || economicsQuery.isError || trendsQuery.isError;

    const usage = usageQuery.data;
    const economics = economicsQuery.data;
    const trends = trendsQuery.data;

    const planRows = useMemo(() => {
        if (!economics?.by_plan) return [] as Array<{ plan: string; calls: number; tokens_total: number; credits_charged: number; provider_cost_usd: number; user_billable_usd: number; implied_margin_usd: number }>;
        return Object.entries(economics.by_plan)
            .map(([plan, value]) => ({ plan, ...value }))
            .sort((a, b) => b.calls - a.calls);
    }, [economics]);

    const trendByDate = useMemo(() => {
        const bucket: Record<string, { provider: number; billable: number; margin: number; credits: number; calls: number }> = {};
        for (const row of trends?.series || []) {
            if (!bucket[row.date]) {
                bucket[row.date] = { provider: 0, billable: 0, margin: 0, credits: 0, calls: 0 };
            }
            bucket[row.date].provider += row.provider_cost_usd;
            bucket[row.date].billable += row.user_billable_usd;
            bucket[row.date].margin += row.implied_margin_usd;
            bucket[row.date].credits += row.credits_charged;
            bucket[row.date].calls += row.calls;
        }
        return Object.entries(bucket)
            .map(([date, value]) => ({ date, ...value }))
            .sort((a, b) => a.date.localeCompare(b.date))
            .slice(-14);
    }, [trends]);

    const maxTrend = useMemo(() => {
        return Math.max(
            1,
            ...trendByDate.map((d) => Math.max(d.provider, d.billable))
        );
    }, [trendByDate]);

    const onRefresh = async () => {
        await Promise.all([usageQuery.refetch(), economicsQuery.refetch(), trendsQuery.refetch()]);
    };

    const recordForWho = (row: AIUsageRecord): string => {
        if (row.user_email) return row.user_email;
        if (row.user_name) return row.user_name;
        return row.user_id;
    };

    const recordWhatFor = (row: AIUsageRecord): string => {
        const entityType = (row.related_entity_type || '').toUpperCase();
        const preview = row.related_entity_preview || {};
        if (entityType === 'THREAD') {
            const subject = typeof preview.subject === 'string' ? preview.subject : '';
            return subject ? `THREAD • ${subject}` : `THREAD • ${row.related_entity_id || '-'}`;
        }
        if (entityType === 'EMAIL') {
            const subject = typeof preview.subject === 'string' ? preview.subject : '';
            return subject ? `EMAIL • ${subject}` : `EMAIL • ${row.related_entity_id || '-'}`;
        }
        if (entityType === 'DRAFT') {
            const subject = typeof preview.subject === 'string' ? preview.subject : '';
            return subject ? `DRAFT • ${subject}` : `DRAFT • ${row.related_entity_id || '-'}`;
        }
        return row.related_entity_id || '-';
    };

    return (
        <div className="p-8 max-w-[1200px] mx-auto space-y-8 animate-in fade-in duration-500">
            <div className="flex flex-col xl:flex-row xl:items-end justify-between gap-4">
                <div className="space-y-4">
                    <Link href="/admin" className="flex items-center gap-2 text-xs font-mono font-bold text-accent hover:opacity-70 transition-opacity uppercase tracking-widest">
                        <ArrowLeft size={12} /> Admin Home
                    </Link>
                    <div>
                        <h1 className="text-3xl font-display text-ink mb-1">AI Usage, Cost, Economics</h1>
                        <p className="text-ink-light text-sm">Detailed telemetry for calls, token burn, provider cost, billable value, and margin dynamics.</p>
                    </div>
                </div>
                <div className="flex flex-wrap gap-2">
                    <select
                        value={hours}
                        onChange={(e) => setHours(Number(e.target.value))}
                        className="h-10 rounded-md border border-border-light bg-white px-3 text-xs font-bold uppercase tracking-wider text-ink"
                    >
                        <option value={1}>Usage: 1h</option>
                        <option value={6}>Usage: 6h</option>
                        <option value={24}>Usage: 24h</option>
                        <option value={72}>Usage: 72h</option>
                        <option value={168}>Usage: 7d</option>
                    </select>
                    <select
                        value={days}
                        onChange={(e) => setDays(Number(e.target.value))}
                        className="h-10 rounded-md border border-border-light bg-white px-3 text-xs font-bold uppercase tracking-wider text-ink"
                    >
                        <option value={7}>Economics: 7d</option>
                        <option value={14}>Economics: 14d</option>
                        <option value={30}>Economics: 30d</option>
                        <option value={60}>Economics: 60d</option>
                        <option value={90}>Economics: 90d</option>
                    </select>
                    <Button onClick={onRefresh} variant="outline" className="h-10 border-border-light text-ink text-xs font-bold uppercase tracking-wider shadow-sm">
                        <RefreshCw size={14} className={`mr-2 ${isFetching ? 'animate-spin' : ''}`} /> Refresh
                    </Button>
                </div>
            </div>

            {isError && (
                <Card className="border-red-200 bg-red-50">
                    <CardContent className="p-4 text-sm text-red-700">Failed to load one or more AI metrics endpoints.</CardContent>
                </Card>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-6 gap-4">
                <MetricCard title="Calls" value={isLoading ? '...' : n(usage?.totals.calls || 0)} icon={Cpu} tone="text-ai" />
                <MetricCard title="Tokens" value={isLoading ? '...' : n(usage?.totals.tokens_total || 0)} icon={Layers} tone="text-info" />
                <MetricCard title="Credits Charged" value={isLoading ? '...' : num(economics?.totals.credits_charged || 0)} icon={Coins} tone="text-accent" />
                <MetricCard title="Provider Cost" value={isLoading ? '...' : usd(economics?.totals.provider_cost_usd || 0)} icon={DollarSign} tone="text-warning" />
                <MetricCard title="Billable" value={isLoading ? '...' : usd(economics?.totals.user_billable_usd || 0)} icon={TrendingUp} tone="text-success" />
                <MetricCard title="Implied Margin" value={isLoading ? '...' : usd(economics?.totals.implied_margin_usd || 0)} icon={Triangle} tone={(economics?.totals.implied_margin_usd || 0) >= 0 ? 'text-success' : 'text-danger'} />
            </div>

            <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
                <Card className="xl:col-span-2 border-border-light shadow-sm overflow-hidden">
                    <CardHeader className="bg-paper-mid/50 border-b border-border-light">
                        <CardTitle className="text-xs font-mono font-bold uppercase tracking-widest text-muted-foreground">14-Day Cost vs Billable Trend</CardTitle>
                    </CardHeader>
                    <CardContent className="p-5 bg-white">
                        <div className="h-56 rounded-lg border border-border-light bg-paper-mid/20 p-3 flex items-end gap-2 overflow-x-auto">
                            {(trendByDate.length ? trendByDate : [{ date: 'n/a', provider: 0, billable: 0, margin: 0, credits: 0, calls: 0 }]).map((point) => {
                                const providerHeight = Math.max(4, Math.round((point.provider / maxTrend) * 100));
                                const billableHeight = Math.max(4, Math.round((point.billable / maxTrend) * 100));
                                return (
                                    <div key={point.date} className="min-w-[38px] flex-1 h-full flex flex-col items-center justify-end gap-1">
                                        <div className="w-full flex items-end gap-1 h-[82%]">
                                            <div className="w-1/2 bg-warning/80 rounded-t-sm" style={{ height: `${providerHeight}%` }} title={`Provider ${usd(point.provider)}`} />
                                            <div className="w-1/2 bg-success/80 rounded-t-sm" style={{ height: `${billableHeight}%` }} title={`Billable ${usd(point.billable)}`} />
                                        </div>
                                        <div className="text-[10px] text-ink-light font-mono">{point.date.slice(5)}</div>
                                    </div>
                                );
                            })}
                        </div>
                        <div className="mt-3 flex flex-wrap items-center gap-4 text-[11px] font-mono text-ink-light">
                            <span className="inline-flex items-center gap-1"><span className="h-2 w-2 rounded bg-warning/80" /> Provider cost</span>
                            <span className="inline-flex items-center gap-1"><span className="h-2 w-2 rounded bg-success/80" /> User billable</span>
                        </div>
                    </CardContent>
                </Card>

                <Card className="border-border-light shadow-sm overflow-hidden">
                    <CardHeader className="bg-paper-mid/50 border-b border-border-light">
                        <CardTitle className="text-xs font-mono font-bold uppercase tracking-widest text-muted-foreground">Economics Summary</CardTitle>
                    </CardHeader>
                    <CardContent className="p-5 space-y-3 text-xs">
                        <Summary label="Charge Failures" value={n(economics?.totals.charge_failures || 0)} />
                        <Summary label="Active Subscriptions" value={n(economics?.financials.active_subscriptions || 0)} />
                        <Summary label="Subscription Revenue" value={usd(economics?.financials.subscription_revenue_usd || 0)} />
                        <Summary label="Credit Purchase Revenue" value={usd(economics?.financials.credit_purchase_revenue_usd || 0)} />
                        <Summary label="Free Plan Burn" value={usd(economics?.financials.free_plan_burn_usd || 0)} />
                        <Summary label="Paid Usage Margin" value={usd(economics?.financials.paid_plan_implied_usage_margin_usd || 0)} />
                        <Summary label="Usage Error Rate" value={`${num(usage?.totals.error_rate_pct || 0)}%`} />
                    </CardContent>
                </Card>
            </div>

            <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                <Card className="border-border-light shadow-sm overflow-hidden">
                    <CardHeader className="bg-paper-mid/50 border-b border-border-light">
                        <CardTitle className="text-xs font-mono font-bold uppercase tracking-widest text-muted-foreground">By Plan</CardTitle>
                    </CardHeader>
                    <CardContent className="p-0 overflow-x-auto">
                        <table className="w-full text-xs">
                            <thead className="bg-paper-mid/30 text-ink-light uppercase tracking-wider text-[10px]">
                                <tr>
                                    <th className="text-left px-4 py-3">Plan</th>
                                    <th className="text-right px-4 py-3">Calls</th>
                                    <th className="text-right px-4 py-3">Credits</th>
                                    <th className="text-right px-4 py-3">Provider</th>
                                    <th className="text-right px-4 py-3">Billable</th>
                                    <th className="text-right px-4 py-3">Margin</th>
                                </tr>
                            </thead>
                            <tbody>
                                {planRows.map((row) => (
                                    <tr key={row.plan} className="border-t border-border-light/60 hover:bg-paper-mid/20">
                                        <td className="px-4 py-3"><Badge variant="outline" className="font-mono">{row.plan}</Badge></td>
                                        <td className="px-4 py-3 text-right font-mono">{n(row.calls)}</td>
                                        <td className="px-4 py-3 text-right font-mono">{num(row.credits_charged)}</td>
                                        <td className="px-4 py-3 text-right font-mono">{usd(row.provider_cost_usd)}</td>
                                        <td className="px-4 py-3 text-right font-mono">{usd(row.user_billable_usd)}</td>
                                        <td className={`px-4 py-3 text-right font-mono ${(row.implied_margin_usd || 0) >= 0 ? 'text-success' : 'text-danger'}`}>{usd(row.implied_margin_usd)}</td>
                                    </tr>
                                ))}
                                {!isLoading && planRows.length === 0 && (
                                    <tr><td colSpan={6} className="px-4 py-8 text-center text-ink-light">No plan economics available.</td></tr>
                                )}
                            </tbody>
                        </table>
                    </CardContent>
                </Card>

                <Card className="border-border-light shadow-sm overflow-hidden">
                    <CardHeader className="bg-paper-mid/50 border-b border-border-light">
                        <CardTitle className="text-xs font-mono font-bold uppercase tracking-widest text-muted-foreground">Top Models & Operations</CardTitle>
                    </CardHeader>
                    <CardContent className="p-5 grid grid-cols-1 md:grid-cols-2 gap-5">
                        <div className="space-y-3">
                            <h3 className="text-[11px] uppercase font-mono tracking-widest text-ink-light">Models</h3>
                            {(usage?.by_model || []).slice(0, 6).map((row) => (
                                <div key={row.model_name} className="space-y-1">
                                    <div className="flex items-center justify-between text-[11px]">
                                        <span className="truncate pr-3" title={row.model_name}>{row.model_name}</span>
                                        <span className="font-mono text-ink-light">{n(row.tokens_total)}</span>
                                    </div>
                                    <div className="h-2 bg-paper-mid rounded">
                                        <div className="h-full bg-ai rounded" style={{ width: `${Math.min(100, ((row.tokens_total || 0) / Math.max(1, usage?.totals.tokens_total || 1)) * 100)}%` }} />
                                    </div>
                                </div>
                            ))}
                        </div>
                        <div className="space-y-3">
                            <h3 className="text-[11px] uppercase font-mono tracking-widest text-ink-light">Operations</h3>
                            {(usage?.by_operation || []).slice(0, 6).map((row) => (
                                <div key={row.operation_type} className="flex items-center justify-between text-[11px] border-b border-border-light/50 pb-2">
                                    <span className="truncate pr-3">{row.operation_type}</span>
                                    <span className="font-mono text-ink-light">{n(row.calls)} calls</span>
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>
            </div>

            <Card className="border-border-light shadow-sm overflow-hidden">
                <CardHeader className="bg-paper-mid/50 border-b border-border-light">
                    <CardTitle className="text-xs font-mono font-bold uppercase tracking-widest text-muted-foreground">Recent AI Usage Records</CardTitle>
                </CardHeader>
                <CardContent className="p-0 overflow-x-auto">
                    <table className="w-full text-xs">
                        <thead className="bg-paper-mid/30 text-ink-light uppercase tracking-wider text-[10px]">
                            <tr>
                                <th className="text-left px-4 py-3">Time</th>
                                <th className="text-left px-4 py-3">Who</th>
                                <th className="text-left px-4 py-3">Operation</th>
                                <th className="text-left px-4 py-3">What For</th>
                                <th className="text-left px-4 py-3">Model</th>
                                <th className="text-right px-4 py-3">Tokens</th>
                                <th className="text-right px-4 py-3">Credits</th>
                                <th className="text-right px-4 py-3">Cost</th>
                                <th className="text-right px-4 py-3">Latency</th>
                                <th className="text-right px-4 py-3">Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {(usage?.records || []).slice(0, 120).map((row) => (
                                <tr
                                    key={row.id}
                                    className="border-t border-border-light/60 hover:bg-paper-mid/20 cursor-pointer"
                                    onClick={() => setSelectedRecord(row)}
                                >
                                    <td className="px-4 py-3 whitespace-nowrap">{row.created_at ? new Date(row.created_at).toLocaleString() : '-'}</td>
                                    <td className="px-4 py-3 max-w-[220px] truncate" title={recordForWho(row)}>{recordForWho(row)}</td>
                                    <td className="px-4 py-3">{row.operation_type}</td>
                                    <td className="px-4 py-3 max-w-[260px] truncate" title={recordWhatFor(row)}>{recordWhatFor(row)}</td>
                                    <td className="px-4 py-3 max-w-[240px] truncate" title={row.model_name}>{row.model_name}</td>
                                    <td className="px-4 py-3 text-right font-mono">{n(row.tokens_total || 0)}</td>
                                    <td className="px-4 py-3 text-right font-mono">{num(row.credits_charged || 0)}</td>
                                    <td className="px-4 py-3 text-right font-mono">{usd((row.cost_cents || 0) / 100)}</td>
                                    <td className="px-4 py-3 text-right font-mono">{row.latency_ms ?? '-'}</td>
                                    <td className="px-4 py-3 text-right">{row.error_occurred ? <span className="text-danger font-bold">Error</span> : <span className="text-success">OK</span>}</td>
                                </tr>
                            ))}
                            {!isLoading && (usage?.records || []).length === 0 && (
                                <tr><td colSpan={10} className="px-4 py-8 text-center text-ink-light">No usage rows in this window.</td></tr>
                            )}
                        </tbody>
                    </table>
                </CardContent>
            </Card>

            <Dialog open={!!selectedRecord} onOpenChange={(open) => !open && setSelectedRecord(null)}>
                <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
                    <DialogHeader>
                        <DialogTitle className="text-base font-mono">AI Call Trace Detail</DialogTitle>
                        <DialogDescription>
                            Full per-call traceability: caller identity, operation intent, target entity, pricing, and metadata.
                        </DialogDescription>
                    </DialogHeader>

                    {selectedRecord && (
                        <div className="space-y-5 text-xs">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <TraceRow label="Call ID" value={selectedRecord.id} mono />
                                <TraceRow label="Time" value={selectedRecord.created_at ? new Date(selectedRecord.created_at).toLocaleString() : '-'} />
                                <TraceRow label="Who (User ID)" value={selectedRecord.user_id} mono />
                                <TraceRow label="Who (Email)" value={selectedRecord.user_email || '-'} mono />
                                <TraceRow label="Who (Name)" value={selectedRecord.user_name || '-'} />
                                <TraceRow label="Plan" value={selectedRecord.user_plan || '-'} mono />
                                <TraceRow label="Operation" value={selectedRecord.operation_type} mono />
                                <TraceRow label="Model" value={selectedRecord.model_name} mono />
                                <TraceRow label="Provider" value={selectedRecord.provider || '-'} mono />
                                <TraceRow label="Request Ref" value={selectedRecord.request_id || '-'} mono />
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <TraceRow label="Entity Type" value={selectedRecord.related_entity_type || '-'} mono />
                                <TraceRow label="Entity ID" value={selectedRecord.related_entity_id || '-'} mono />
                                <TraceRow label="What For" value={recordWhatFor(selectedRecord)} />
                                <TraceRow label="Token Source" value={selectedRecord.token_source || '-'} mono />
                            </div>

                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                <TraceRow label="Input Tokens" value={n(selectedRecord.tokens_input || 0)} mono />
                                <TraceRow label="Output Tokens" value={n(selectedRecord.tokens_output || 0)} mono />
                                <TraceRow label="Total Tokens" value={n(selectedRecord.tokens_total || 0)} mono />
                                <TraceRow label="Latency (ms)" value={selectedRecord.latency_ms == null ? '-' : n(selectedRecord.latency_ms)} mono />
                                <TraceRow label="Credits" value={num(selectedRecord.credits_charged || 0)} mono />
                                <TraceRow label="Provider Cost" value={usd(selectedRecord.provider_cost_usd || 0)} mono />
                                <TraceRow label="Billable" value={usd(selectedRecord.user_billable_usd || 0)} mono />
                                <TraceRow label="Margin" value={usd(selectedRecord.implied_margin_usd || 0)} mono />
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <TraceRow label="Status" value={selectedRecord.error_occurred ? 'ERROR' : 'OK'} mono />
                                <TraceRow label="Error Type" value={selectedRecord.error_type || '-'} mono />
                                <TraceRow label="Charge Error" value={selectedRecord.charge_error || '-'} mono />
                                <TraceRow label="Balance After" value={selectedRecord.balance_after == null ? '-' : num(selectedRecord.balance_after)} mono />
                                <TraceRow label="Cache Hit" value={selectedRecord.cache_hit ? 'true' : 'false'} mono />
                                <TraceRow label="Charged Milli Credits" value={n(selectedRecord.charged_milli_credits || 0)} mono />
                            </div>

                            <div>
                                <div className="text-[11px] uppercase tracking-widest font-mono text-ink-light mb-2">Metadata JSON</div>
                                <pre className="rounded-md border border-border-light bg-paper-mid/30 p-3 text-[11px] font-mono whitespace-pre-wrap break-words max-h-[320px] overflow-auto">
{JSON.stringify(selectedRecord.metadata || {}, null, 2)}
                                </pre>
                            </div>
                        </div>
                    )}
                </DialogContent>
            </Dialog>
        </div>
    );
}

function MetricCard({ title, value, icon: Icon, tone }: { title: string; value: string; icon: LucideIcon; tone: string }) {
    return (
        <Card className="border-border-light shadow-sm">
            <CardContent className="p-4">
                <div className="flex items-center justify-between mb-2 text-muted-foreground">
                    <span className="text-[10px] font-mono font-bold uppercase tracking-widest">{title}</span>
                    <Icon size={15} className={tone} />
                </div>
                <p className="text-2xl font-display text-ink">{value}</p>
            </CardContent>
        </Card>
    );
}

function Summary({ label, value }: { label: string; value: string }) {
    return (
        <div className="flex items-center justify-between">
            <span className="text-ink-light">{label}</span>
            <span className="font-mono text-ink">{value}</span>
        </div>
    );
}

function TraceRow({ label, value, mono = false }: { label: string; value: string; mono?: boolean }) {
    return (
        <div className="rounded border border-border-light/70 bg-paper-mid/20 p-2">
            <div className="text-[10px] uppercase tracking-widest font-mono text-ink-light mb-1">{label}</div>
            <div className={`${mono ? 'font-mono' : ''} text-ink break-all`}>{value}</div>
        </div>
    );
}
