"use client";

import React from "react";
import { useQuery } from "@tanstack/react-query";
import { CreditCard, Zap, TrendingUp, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import Link from "next/link";
import { api, endpoints } from "@/lib/api";
import { formatDistanceToNow, format } from "date-fns";

interface CreditBalance {
    balance: number;
    plan: string;
    monthly_allowance: number;
    used_this_month: number;
    resets_on?: string;
}

interface Transaction {
    id: string;
    amount: number;
    balance_after: number;
    transaction_type: string;
    operation_type?: string;
    status: string;
    created_at: string;
}

const PLAN_COLORS: Record<string, string> = {
    free: "bg-slate-100 text-slate-700",
    pro: "bg-primary/10 text-primary",
    team: "bg-purple-100 text-purple-700",
    enterprise: "bg-amber-100 text-amber-700",
};

const OPERATION_LABELS: Record<string, string> = {
    thread_summary: "Email Summary",
    draft_reply: "Draft Reply",
    task_generation: "Task Generation",
    monthly_allowance: "Monthly Allowance",
    admin_adjustment: "Admin Adjustment",
    bonus: "Bonus Credits",
    purchase: "Credit Purchase",
    refund: "Refund",
};

export default function SettingsBillingPage() {
    const { data: credits, isLoading: creditsLoading } = useQuery<CreditBalance>({
        queryKey: ["credits-me"],
        queryFn: async () => {
            const { data } = await api.get(endpoints.creditsMe);
            return data;
        },
    });

    const { data: transactions = [], isLoading: txLoading } = useQuery<Transaction[]>({
        queryKey: ["credits-transactions"],
        queryFn: async () => {
            const { data } = await api.get(endpoints.creditsTransactions, { params: { limit: 10 } });
            return data;
        },
    });

    const usagePct = credits
        ? Math.round((credits.used_this_month / (credits.monthly_allowance || 1)) * 100)
        : 0;

    const balancePct = credits
        ? Math.round((credits.balance / (credits.monthly_allowance || 1)) * 100)
        : 0;

    const balanceColor =
        balancePct > 50 ? "bg-success" : balancePct > 20 ? "bg-warning" : "bg-danger";

    return (
        <div className="max-w-4xl space-y-6">
            <div className="mb-6">
                <h1 className="font-display text-2xl text-ink mb-2">Billing &amp; Credits</h1>
                <p className="text-muted">Your current plan, credit balance, and usage history.</p>
            </div>

            {/* Credit Balance Card */}
            <Card>
                <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                        <CardTitle className="text-base font-body flex items-center gap-2">
                            <Zap className="h-5 w-5 text-primary" />
                            Credit Balance
                        </CardTitle>
                        {credits?.plan && (
                            <Badge className={PLAN_COLORS[credits.plan] || PLAN_COLORS.free}>
                                {credits.plan.charAt(0).toUpperCase() + credits.plan.slice(1)} Plan
                            </Badge>
                        )}
                    </div>
                </CardHeader>
                <CardContent>
                    {creditsLoading ? (
                        <div className="h-24 rounded-lg bg-paper-mid animate-pulse" />
                    ) : credits ? (
                        <div className="space-y-4">
                            <div>
                                <div className="flex items-end justify-between mb-2">
                                    <span className="text-4xl font-bold text-ink">{credits.balance}</span>
                                    <span className="text-sm text-muted">/ {credits.monthly_allowance} monthly</span>
                                </div>
                                <Progress value={balancePct} className={`h-2 ${balanceColor}`} />
                                <p className="text-xs text-muted mt-1.5">
                                    {credits.used_this_month} used this month
                                    {credits.resets_on && ` · Resets ${format(new Date(credits.resets_on), "MMM d")}`}
                                </p>
                            </div>
                            <div className="flex gap-2 pt-2 border-t border-border-light">
                                <Link href="/upgrade" className="flex-1">
                                    <Button className="w-full gap-2" size="sm">
                                        <TrendingUp className="h-4 w-4" /> Upgrade Plan
                                    </Button>
                                </Link>
                                <Button variant="outline" size="sm" className="gap-2">
                                    <CreditCard className="h-4 w-4" /> Buy Credits
                                </Button>
                            </div>
                        </div>
                    ) : (
                        <p className="text-muted text-sm">Could not load credit data.</p>
                    )}
                </CardContent>
            </Card>

            {/* Recent Transactions */}
            <Card>
                <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                        <CardTitle className="text-base font-body">Recent Transactions</CardTitle>
                        <Link href="/settings/billing/history">
                            <Button variant="ghost" size="sm" className="text-xs text-muted-foreground">View all</Button>
                        </Link>
                    </div>
                </CardHeader>
                <CardContent>
                    {txLoading ? (
                        <div className="space-y-2">{[1, 2, 3].map(i => <div key={i} className="h-10 rounded bg-paper-mid animate-pulse" />)}</div>
                    ) : transactions.length === 0 ? (
                        <p className="text-sm text-muted py-4 text-center">No transactions yet.</p>
                    ) : (
                        <div className="space-y-1">
                            {transactions.map(t => (
                                <div key={t.id} className="flex items-center justify-between py-2 border-b border-border-light last:border-0">
                                    <div>
                                        <p className="text-sm font-medium text-ink">
                                            {OPERATION_LABELS[t.operation_type || t.transaction_type] || t.transaction_type}
                                        </p>
                                        <p className="text-xs text-muted">
                                            {formatDistanceToNow(new Date(t.created_at), { addSuffix: true })}
                                        </p>
                                    </div>
                                    <div className="text-right">
                                        <p className={`text-sm font-semibold ${t.amount > 0 ? "text-success" : "text-danger"}`}>
                                            {t.amount > 0 ? "+" : ""}{t.amount}
                                        </p>
                                        <p className="text-xs text-muted">{t.balance_after} bal</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}
