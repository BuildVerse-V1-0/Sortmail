'use client';

import React, { useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, Activity, Database, Server, Cpu, RefreshCw, Copy } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { api, endpoints } from '@/lib/api';

type MetricsOverviewResponse = {
    app: {
        window_seconds: number;
        events_last_minute: Record<string, number>;
        total_events_last_minute: number;
        events_lifetime: Record<string, number>;
        total_events_lifetime: number;
        sampled_at: string;
    };
    redis: {
        window_seconds: number;
        calls_last_minute: number;
        commands_last_minute: Record<string, number>;
        total_calls_lifetime: number;
        commands_lifetime: Record<string, number>;
        sampled_at: string;
    };
    queue: {
        enabled: boolean;
        pending_items: number | null;
    };
};

type Sample = {
    at: string;
    appEvents: number;
    redisCalls: number;
    queuePending: number;
};

type RedisDetailResponse = {
    in_process: {
        sampled_at: string;
        window_summary: {
            calls_last_10s: number;
            calls_last_30s: number;
            calls_last_60s: number;
            calls_last_300s: number;
        };
        command_breakdown_last_300s: Record<string, number>;
        top_commands_last_300s: Array<{ command: string; calls: number }>;
        timeline_last_60s_5s_buckets: Array<{
            bucket_index: number;
            seconds_ago_start: number;
            seconds_ago_end: number;
            calls: number;
        }>;
        recent_calls: Array<{ command: string; age_seconds: number }>;
        lifetime: {
            total_calls: number;
            commands: Record<string, number>;
        };
    };
    command_pool: {
        max_connections: number | null;
        in_use_connections: number | null;
        available_connections: number | null;
        utilization_pct: number | null;
    } | null;
    pubsub_pool: {
        max_connections: number | null;
        in_use_connections: number | null;
        available_connections: number | null;
        utilization_pct: number | null;
    } | null;
    clients: Record<string, any> | null;
    stats: Record<string, any> | null;
    memory: Record<string, any> | null;
    errors: string[];
};

const POLL_MS = 10_000;
const MAX_SAMPLES = 30;

export default function AdminMetricsPage() {
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [copying, setCopying] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [overview, setOverview] = useState<MetricsOverviewResponse | null>(null);
    const [redisDetail, setRedisDetail] = useState<RedisDetailResponse | null>(null);
    const [samples, setSamples] = useState<Sample[]>([]);

    const fetchOverview = async (isManual = false) => {
        if (isManual) setRefreshing(true);
        try {
            const [overviewResponse, redisDetailResponse] = await Promise.all([
                api.get<MetricsOverviewResponse>(endpoints.adminMetricsOverview),
                api.get<RedisDetailResponse>(endpoints.adminMetricsRedisDetail),
            ]);
            const data = overviewResponse.data;
            setOverview(data);
            setRedisDetail(redisDetailResponse.data);
            setError(null);
            setSamples((prev) => {
                const next: Sample[] = [
                    ...prev,
                    {
                        at: new Date().toISOString(),
                        appEvents: data.app.total_events_last_minute || 0,
                        redisCalls: data.redis.calls_last_minute || 0,
                        queuePending: data.queue.pending_items || 0,
                    },
                ];
                return next.slice(-MAX_SAMPLES);
            });
        } catch (e: any) {
            const status = e?.response?.status;
            if (status === 403) {
                setError('Admin access required (403). Confirm your account is marked is_superuser=true.');
            } else {
                setError('Failed to load admin metrics.');
            }
        } finally {
            setLoading(false);
            if (isManual) setRefreshing(false);
        }
    };

    useEffect(() => {
        let mounted = true;
        const run = async () => {
            if (!mounted) return;
            await fetchOverview();
        };

        run();
        const id = setInterval(run, POLL_MS);
        return () => {
            mounted = false;
            clearInterval(id);
        };
    }, []);

    const topAppEvents = useMemo(() => {
        if (!overview) return [] as Array<[string, number]>;
        return Object.entries(overview.app.events_last_minute)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 8);
    }, [overview]);

    const topRedisCommands = useMemo(() => {
        if (!overview) return [] as Array<[string, number]>;
        return Object.entries(overview.redis.commands_last_minute)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 8);
    }, [overview]);

    const topRedisCommands300s = useMemo(() => {
        return redisDetail?.in_process.top_commands_last_300s?.slice(0, 12) || [];
    }, [redisDetail]);

    const abnormalFlags = useMemo(() => {
        const flags: string[] = [];
        const commandUtil = redisDetail?.command_pool?.utilization_pct ?? 0;
        const pubsubUtil = redisDetail?.pubsub_pool?.utilization_pct ?? 0;
        const calls10s = redisDetail?.in_process.window_summary.calls_last_10s ?? 0;
        const calls60s = redisDetail?.in_process.window_summary.calls_last_60s ?? 0;
        const rejected = Number(redisDetail?.stats?.rejected_connections || 0);

        if (commandUtil >= 85) flags.push(`Command pool utilization high: ${commandUtil}%`);
        if (pubsubUtil >= 85) flags.push(`Pubsub pool utilization high: ${pubsubUtil}%`);
        if (calls10s >= 300) flags.push(`Redis burst high in 10s window: ${calls10s} calls`);
        if (calls60s >= 1500) flags.push(`Redis sustained load high in 60s window: ${calls60s} calls`);
        if (rejected > 0) flags.push(`Redis rejected connections observed: ${rejected}`);
        if ((redisDetail?.errors || []).length > 0) flags.push(`Diagnostics errors: ${redisDetail?.errors.join(' | ')}`);

        return flags;
    }, [redisDetail]);

    const copyPayload = async () => {
        if (!overview || !redisDetail) return;
        setCopying(true);
        try {
            const payload = {
                sampled_at: new Date().toISOString(),
                overview,
                redis_detail: redisDetail,
                abnormal_flags: abnormalFlags,
            };
            await navigator.clipboard.writeText(JSON.stringify(payload, null, 2));
        } finally {
            setCopying(false);
        }
    };

    return (
        <div className="p-8 max-w-7xl mx-auto space-y-8 animate-in fade-in duration-500">
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
                <div className="space-y-4">
                    <Link href="/admin" className="flex items-center gap-2 text-xs font-mono font-bold text-accent hover:opacity-70 transition-opacity uppercase tracking-widest">
                        <ArrowLeft size={12} /> Admin Home
                    </Link>
                    <div>
                        <h1 className="text-3xl font-display text-ink mb-1">Live Metrics</h1>
                        <p className="text-ink-light text-sm">Admin-only operational metrics. Auto-refresh every 10 seconds.</p>
                    </div>
                </div>
                <Button
                    onClick={() => fetchOverview(true)}
                    disabled={refreshing}
                    variant="outline"
                    className="h-10 border-border-light text-ink text-xs font-bold uppercase tracking-wider shadow-sm"
                >
                    <RefreshCw size={14} className={refreshing ? 'animate-spin mr-2' : 'mr-2'} />
                    Refresh
                </Button>
                <Button
                    onClick={copyPayload}
                    disabled={copying || !overview || !redisDetail}
                    variant="outline"
                    className="h-10 border-border-light text-ink text-xs font-bold uppercase tracking-wider shadow-sm"
                >
                    <Copy size={14} className="mr-2" />
                    {copying ? 'Copying...' : 'Copy Redis Report'}
                </Button>
            </div>

            {error && (
                <Card className="border-danger/30 bg-danger/5">
                    <CardContent className="p-4 text-danger text-sm font-medium">{error}</CardContent>
                </Card>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard label="App Events / Min" value={overview?.app.total_events_last_minute ?? 0} icon={Activity} color="text-accent" />
                <StatCard label="Redis Calls / Min" value={overview?.redis.calls_last_minute ?? 0} icon={Database} color="text-info" />
                <StatCard label="Queue Pending" value={overview?.queue.pending_items ?? 0} icon={Server} color="text-warning" />
                <StatCard label="Queue Enabled" value={overview?.queue.enabled ? 'Yes' : 'No'} icon={Cpu} color="text-success" />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <Card className="lg:col-span-2 border-border-light shadow-sm overflow-hidden">
                    <CardHeader className="bg-paper-mid/50 border-b border-border-light">
                        <CardTitle className="text-xs font-mono font-bold uppercase tracking-widest text-muted-foreground">Live Calls (Rolling 60s)</CardTitle>
                    </CardHeader>
                    <CardContent className="p-6 space-y-8 bg-white">
                        <MiniBarChart
                            title="Redis Calls / Minute"
                            data={samples.map((s) => s.redisCalls)}
                            colorClass="bg-info"
                        />
                        <MiniBarChart
                            title="App Events / Minute"
                            data={samples.map((s) => s.appEvents)}
                            colorClass="bg-accent"
                        />
                        <MiniBarChart
                            title="Queue Pending"
                            data={samples.map((s) => s.queuePending)}
                            colorClass="bg-warning"
                        />
                    </CardContent>
                </Card>

                <div className="space-y-6">
                    <Card className="border-border-light shadow-sm">
                        <CardHeader className="bg-paper-mid/50 border-b border-border-light">
                            <CardTitle className="text-[10px] font-mono font-bold uppercase tracking-widest text-muted-foreground">Top App Events / Min</CardTitle>
                        </CardHeader>
                        <CardContent className="p-4 space-y-2">
                            {topAppEvents.length === 0 ? (
                                <EmptyLine text={loading ? 'Loading...' : 'No events yet'} />
                            ) : (
                                topAppEvents.map(([k, v]) => <MetricRow key={k} label={k} value={v} />)
                            )}
                        </CardContent>
                    </Card>

                    <Card className="border-border-light shadow-sm">
                        <CardHeader className="bg-paper-mid/50 border-b border-border-light">
                            <CardTitle className="text-[10px] font-mono font-bold uppercase tracking-widest text-muted-foreground">Top Redis Commands / Min</CardTitle>
                        </CardHeader>
                        <CardContent className="p-4 space-y-2">
                            {topRedisCommands.length === 0 ? (
                                <EmptyLine text={loading ? 'Loading...' : 'No command activity'} />
                            ) : (
                                topRedisCommands.map(([k, v]) => <MetricRow key={k} label={k} value={v} />)
                            )}
                        </CardContent>
                    </Card>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <Card className="border-border-light shadow-sm">
                    <CardHeader className="bg-paper-mid/50 border-b border-border-light">
                        <CardTitle className="text-[10px] font-mono font-bold uppercase tracking-widest text-muted-foreground">Redis Depletion Signals</CardTitle>
                    </CardHeader>
                    <CardContent className="p-4 space-y-2">
                        {abnormalFlags.length === 0 ? (
                            <EmptyLine text="No obvious depletion flags right now." />
                        ) : (
                            abnormalFlags.map((flag) => <EmptyLine key={flag} text={flag} />)
                        )}
                        <div className="pt-2 border-t border-border-light">
                            <MetricRow label="Command Pool Utilization %" value={Number(redisDetail?.command_pool?.utilization_pct || 0)} />
                            <MetricRow label="Pubsub Pool Utilization %" value={Number(redisDetail?.pubsub_pool?.utilization_pct || 0)} />
                            <MetricRow label="Calls Last 10s" value={Number(redisDetail?.in_process.window_summary.calls_last_10s || 0)} />
                            <MetricRow label="Calls Last 30s" value={Number(redisDetail?.in_process.window_summary.calls_last_30s || 0)} />
                            <MetricRow label="Calls Last 60s" value={Number(redisDetail?.in_process.window_summary.calls_last_60s || 0)} />
                            <MetricRow label="Calls Last 300s" value={Number(redisDetail?.in_process.window_summary.calls_last_300s || 0)} />
                        </div>
                    </CardContent>
                </Card>

                <Card className="border-border-light shadow-sm">
                    <CardHeader className="bg-paper-mid/50 border-b border-border-light">
                        <CardTitle className="text-[10px] font-mono font-bold uppercase tracking-widest text-muted-foreground">Top Redis Commands / 5 Min</CardTitle>
                    </CardHeader>
                    <CardContent className="p-4 space-y-2">
                        {topRedisCommands300s.length === 0 ? (
                            <EmptyLine text={loading ? 'Loading...' : 'No command activity in 5 min window'} />
                        ) : (
                            topRedisCommands300s.map((row) => <MetricRow key={row.command} label={row.command} value={row.calls} />)
                        )}
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}

function StatCard({ label, value, icon: Icon, color }: { label: string; value: string | number; icon: any; color: string }) {
    return (
        <Card className="border-border-light shadow-sm">
            <CardContent className="p-5">
                <div className="flex items-center justify-between mb-3 text-muted-foreground">
                    <span className="text-[10px] font-mono font-bold uppercase tracking-widest">{label}</span>
                    <Icon size={16} className={color} />
                </div>
                <p className="text-2xl font-display text-ink">{value}</p>
            </CardContent>
        </Card>
    );
}

function MiniBarChart({ title, data, colorClass }: { title: string; data: number[]; colorClass: string }) {
    const max = Math.max(1, ...data);
    return (
        <div className="space-y-2">
            <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono font-bold uppercase tracking-widest text-ink-mid">{title}</span>
                <span className="text-[10px] font-mono text-ink-light">{data.length} samples</span>
            </div>
            <div className="h-28 w-full rounded-lg border border-border-light bg-paper-mid/20 p-2 flex items-end gap-1">
                {(data.length ? data : [0]).map((value, idx) => {
                    const height = Math.max(6, Math.round((value / max) * 100));
                    return (
                        <div
                            key={`${title}-${idx}`}
                            className={`${colorClass} rounded-t-sm flex-1 transition-all`}
                            style={{ height: `${height}%` }}
                            title={`${value}`}
                        />
                    );
                })}
            </div>
        </div>
    );
}

function MetricRow({ label, value }: { label: string; value: number }) {
    return (
        <div className="flex items-center justify-between text-[11px] font-mono">
            <span className="text-ink-light truncate pr-3">{label}</span>
            <span className="text-ink font-bold">{value}</span>
        </div>
    );
}

function EmptyLine({ text }: { text: string }) {
    return <p className="text-[11px] font-mono text-ink-light">{text}</p>;
}
