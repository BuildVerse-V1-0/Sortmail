"use client";

import React, { useState } from "react";
import { Check, Zap, Users, Building2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import Link from "next/link";

const PLANS = [
    {
        id: "free",
        name: "Free",
        price: { monthly: 0, annual: 0 },
        description: "Perfect for trying out SortMail",
        icon: Zap,
        features: [
            "1 email account",
            "100 AI calls/month",
            "1,000 emails processed/month",
            "Basic email summaries",
            "Task extraction",
        ],
        cta: "Current Plan",
        disabled: true,
    },
    {
        id: "pro",
        name: "Pro",
        price: { monthly: 19, annual: 15 },
        description: "For power users who need more",
        icon: Zap,
        popular: true,
        features: [
            "3 email accounts",
            "5,000 AI calls/month",
            "10,000 emails processed/month",
            "Advanced AI summaries",
            "Auto-draft replies",
            "Priority support",
            "Calendar integration",
        ],
        cta: "Upgrade to Pro",
    },
    {
        id: "team",
        name: "Team",
        price: { monthly: 49, annual: 39 },
        description: "For teams and organizations",
        icon: Users,
        features: [
            "Unlimited email accounts",
            "Unlimited AI calls",
            "Unlimited emails processed",
            "Team collaboration",
            "Shared tasks & drafts",
            "Admin dashboard",
            "Custom integrations",
            "Dedicated support",
        ],
        cta: "Contact Sales",
    },
];

export default function UpgradePage() {
    const [billingCycle, setBillingCycle] = useState<"monthly" | "annual">("monthly");

    return (
        <div className="min-h-screen bg-paper py-12 px-8">
            <div className="max-w-6xl mx-auto">
                {/* Header */}
                <div className="text-center mb-12">
                    <h1 className="font-display text-4xl text-ink mb-3">
                        Upgrade Your Plan
                    </h1>
                    <p className="text-lg text-muted mb-6">
                        Choose the plan that&apos;s right for you
                    </p>

                    {/* Billing Toggle */}
                    <div className="flex items-center justify-center gap-3">
                        <span className={`text-sm ${billingCycle === "monthly" ? "text-ink font-medium" : "text-muted"}`}>
                            Monthly
                        </span>
                        <Switch
                            checked={billingCycle === "annual"}
                            onCheckedChange={(checked) => setBillingCycle(checked ? "annual" : "monthly")}
                        />
                        <span className={`text-sm ${billingCycle === "annual" ? "text-ink font-medium" : "text-muted"}`}>
                            Annual
                        </span>
                        {billingCycle === "annual" && (
                            <Badge className="bg-success text-white">Save 20%</Badge>
                        )}
                    </div>
                </div>

                {/* Plans */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
                    {PLANS.map((plan) => {
                        const Icon = plan.icon;
                        const price = plan.price[billingCycle];
                        return (
                            <Card
                                key={plan.id}
                                className={`p-6 relative ${plan.popular ? "border-accent border-2 shadow-lg" : ""
                                    }`}
                            >
                                {plan.popular && (
                                    <Badge className="absolute -top-3 left-1/2 -translate-x-1/2 bg-accent text-white">
                                        Most Popular
                                    </Badge>
                                )}
                                <div className="text-center mb-6">
                                    <div className="w-12 h-12 rounded-lg bg-accent/10 flex items-center justify-center mx-auto mb-3">
                                        <Icon className="w-6 h-6 text-accent" />
                                    </div>
                                    <h3 className="font-display text-2xl text-ink mb-1">
                                        {plan.name}
                                    </h3>
                                    <p className="text-sm text-muted mb-4">{plan.description}</p>
                                    <div className="mb-2">
                                        <span className="text-4xl font-bold text-ink">${price}</span>
                                        {price > 0 && (
                                            <span className="text-muted">/{billingCycle === "monthly" ? "mo" : "yr"}</span>
                                        )}
                                    </div>
                                    {billingCycle === "annual" && price > 0 && (
                                        <p className="text-xs text-muted">
                                            Billed ${price * 12} annually
                                        </p>
                                    )}
                                </div>

                                <ul className="space-y-3 mb-6">
                                    {plan.features.map((feature, index) => (
                                        <li key={index} className="flex items-start gap-2 text-sm">
                                            <Check className="w-4 h-4 text-success shrink-0 mt-0.5" />
                                            <span className="text-ink">{feature}</span>
                                        </li>
                                    ))}
                                </ul>

                                <Button
                                    className="w-full"
                                    variant={plan.popular ? "default" : "outline"}
                                    disabled={plan.disabled}
                                >
                                    {plan.cta}
                                </Button>
                            </Card>
                        );
                    })}
                </div>

                {/* FAQ */}
                <Card className="p-8">
                    <h2 className="font-display text-2xl text-ink mb-6 text-center">
                        Frequently Asked Questions
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {[
                            {
                                q: "Can I change plans anytime?",
                                a: "Yes, you can upgrade or downgrade your plan at any time. Changes take effect immediately.",
                            },
                            {
                                q: "What payment methods do you accept?",
                                a: "We accept all major credit cards (Visa, Mastercard, Amex) and PayPal.",
                            },
                            {
                                q: "Is there a free trial?",
                                a: "Yes! The Free plan is available forever. Upgrade anytime to unlock more features.",
                            },
                            {
                                q: "Can I cancel my subscription?",
                                a: "Yes, you can cancel anytime. You'll retain access until the end of your billing period.",
                            },
                        ].map((faq, index) => (
                            <div key={index}>
                                <h3 className="font-medium text-ink mb-2">{faq.q}</h3>
                                <p className="text-sm text-muted">{faq.a}</p>
                            </div>
                        ))}
                    </div>
                </Card>
            </div>
        </div>
    );
}
