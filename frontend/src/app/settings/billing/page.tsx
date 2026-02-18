"use client";

import React from "react";
import { CreditCard, Download, Zap, TrendingUp, Calendar } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import Link from "next/link";

const mockBillingData = {
    plan: {
        name: "Pro Plan",
        price: "$19/month",
        billingCycle: "Monthly",
        nextBilling: "2026-03-17",
    },
    usage: {
        aiCalls: { used: 1247, limit: 5000 },
        emailsProcessed: { used: 3821, limit: 10000 },
    },
    paymentMethod: {
        type: "Visa",
        last4: "4242",
        expiry: "12/2027",
    },
    invoices: [
        { id: "INV-001", date: "2026-02-17", amount: "$19.00", status: "paid" },
        { id: "INV-002", date: "2026-01-17", amount: "$19.00", status: "paid" },
        { id: "INV-003", date: "2025-12-17", amount: "$19.00", status: "paid" },
    ],
};

export default function SettingsBillingPage() {
    return (
        <div className="max-w-4xl">
            <div className="mb-6">
                <h1 className="font-display text-2xl text-ink mb-2">Billing & Usage</h1>
                <p className="text-muted">
                    Manage your subscription, payment method, and view usage statistics.
                </p>
            </div>

            <div className="space-y-6">
                {/* Current Plan */}
                <Card className="p-6">
                    <div className="flex items-start justify-between mb-4">
                        <div>
                            <h3 className="font-medium text-ink mb-1">{mockBillingData.plan.name}</h3>
                            <p className="text-2xl font-bold text-ink mb-2">
                                {mockBillingData.plan.price}
                            </p>
                            <p className="text-sm text-muted">
                                Billed {mockBillingData.plan.billingCycle.toLowerCase()} • Next billing:{" "}
                                {new Date(mockBillingData.plan.nextBilling).toLocaleDateString()}
                            </p>
                        </div>
                        <Link href="/upgrade">
                            <Button className="gap-2">
                                <Zap className="w-4 h-4" />
                                Upgrade Plan
                            </Button>
                        </Link>
                    </div>
                </Card>

                {/* Usage Stats */}
                <Card className="p-6">
                    <h3 className="font-medium text-ink mb-4">Usage This Month</h3>
                    <div className="space-y-4">
                        <div>
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-sm text-ink">AI Calls</span>
                                <span className="text-sm text-muted">
                                    {mockBillingData.usage.aiCalls.used.toLocaleString()} /{" "}
                                    {mockBillingData.usage.aiCalls.limit.toLocaleString()}
                                </span>
                            </div>
                            <Progress
                                value={(mockBillingData.usage.aiCalls.used / mockBillingData.usage.aiCalls.limit) * 100}
                                className="h-2"
                            />
                        </div>
                        <div>
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-sm text-ink">Emails Processed</span>
                                <span className="text-sm text-muted">
                                    {mockBillingData.usage.emailsProcessed.used.toLocaleString()} /{" "}
                                    {mockBillingData.usage.emailsProcessed.limit.toLocaleString()}
                                </span>
                            </div>
                            <Progress
                                value={(mockBillingData.usage.emailsProcessed.used / mockBillingData.usage.emailsProcessed.limit) * 100}
                                className="h-2"
                            />
                        </div>
                    </div>
                </Card>

                {/* Payment Method */}
                <Card className="p-6">
                    <div className="flex items-start justify-between">
                        <div className="flex items-start gap-4">
                            <div className="w-12 h-12 rounded-lg bg-accent/10 flex items-center justify-center shrink-0">
                                <CreditCard className="w-6 h-6 text-accent" />
                            </div>
                            <div>
                                <h3 className="font-medium text-ink mb-1">Payment Method</h3>
                                <p className="text-sm text-muted mb-2">
                                    {mockBillingData.paymentMethod.type} ending in {mockBillingData.paymentMethod.last4}
                                </p>
                                <p className="text-xs text-muted">
                                    Expires {mockBillingData.paymentMethod.expiry}
                                </p>
                            </div>
                        </div>
                        <Button variant="outline">Update</Button>
                    </div>
                </Card>

                {/* Billing History */}
                <Card className="p-6">
                    <h3 className="font-medium text-ink mb-4">Billing History</h3>
                    <div className="space-y-3">
                        {mockBillingData.invoices.map((invoice) => (
                            <div
                                key={invoice.id}
                                className="flex items-center justify-between py-3 border-b border-border last:border-0"
                            >
                                <div className="flex items-center gap-3">
                                    <Calendar className="w-4 h-4 text-muted" />
                                    <div>
                                        <p className="text-sm font-medium text-ink">{invoice.id}</p>
                                        <p className="text-xs text-muted">
                                            {new Date(invoice.date).toLocaleDateString()}
                                        </p>
                                    </div>
                                </div>
                                <div className="flex items-center gap-3">
                                    <Badge className="bg-success text-white">
                                        {invoice.status}
                                    </Badge>
                                    <span className="text-sm font-medium text-ink w-20 text-right">
                                        {invoice.amount}
                                    </span>
                                    <Button variant="ghost" size="sm" className="gap-2">
                                        <Download className="w-3 h-3" />
                                        PDF
                                    </Button>
                                </div>
                            </div>
                        ))}
                    </div>
                </Card>

                {/* Cancel Subscription */}
                <Card className="p-6 border-danger/20 bg-danger/5">
                    <div className="flex items-start justify-between">
                        <div>
                            <h3 className="font-medium text-danger mb-1">Cancel Subscription</h3>
                            <p className="text-sm text-muted">
                                You can cancel your subscription at any time. You&apos;ll retain access until the end of your billing period.
                            </p>
                        </div>
                        <Button variant="outline" className="text-danger border-danger hover:bg-danger hover:text-white">
                            Cancel Plan
                        </Button>
                    </div>
                </Card>
            </div>
        </div>
    );
}
