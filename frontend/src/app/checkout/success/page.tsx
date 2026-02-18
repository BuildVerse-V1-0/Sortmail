"use client";

import React from "react";
import { CheckCircle, Download, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import Link from "next/link";

export default function CheckoutSuccessPage() {
    return (
        <div className="min-h-screen bg-paper flex items-center justify-center p-8">
            <Card className="max-w-2xl w-full p-8">
                <div className="text-center mb-8">
                    <div className="w-20 h-20 rounded-full bg-success/10 flex items-center justify-center mx-auto mb-4">
                        <CheckCircle className="w-12 h-12 text-success" />
                    </div>
                    <h1 className="font-display text-3xl text-ink mb-2">
                        Payment Successful!
                    </h1>
                    <p className="text-muted">
                        Welcome to SortMail Pro. Your subscription is now active.
                    </p>
                </div>

                {/* Plan Details */}
                <Card className="p-6 mb-6 bg-accent/5 border-accent/20">
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <p className="text-xs text-muted mb-1">Plan</p>
                            <p className="font-medium text-ink">Pro Plan</p>
                        </div>
                        <div>
                            <p className="text-xs text-muted mb-1">Amount</p>
                            <p className="font-medium text-ink">$19.00/month</p>
                        </div>
                        <div>
                            <p className="text-xs text-muted mb-1">Next Billing</p>
                            <p className="font-medium text-ink">March 17, 2026</p>
                        </div>
                        <div>
                            <p className="text-xs text-muted mb-1">Payment Method</p>
                            <p className="font-medium text-ink">Visa •••• 4242</p>
                        </div>
                    </div>
                </Card>

                {/* Next Steps */}
                <div className="mb-6">
                    <h2 className="font-display text-xl text-ink mb-4">What&apos;s Next?</h2>
                    <div className="space-y-3">
                        {[
                            "Connect additional email accounts (up to 3)",
                            "Enable auto-draft replies in AI settings",
                            "Set up calendar integration",
                            "Explore advanced AI features",
                        ].map((step, index) => (
                            <div key={index} className="flex items-start gap-3">
                                <div className="w-6 h-6 rounded-full bg-accent/10 text-accent flex items-center justify-center shrink-0 mt-0.5">
                                    <span className="text-xs font-bold">{index + 1}</span>
                                </div>
                                <p className="text-ink">{step}</p>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Actions */}
                <div className="flex gap-3">
                    <Link href="/dashboard" className="flex-1">
                        <Button className="w-full gap-2">
                            Go to Dashboard
                            <ArrowRight className="w-4 h-4" />
                        </Button>
                    </Link>
                    <Button variant="outline" className="gap-2">
                        <Download className="w-4 h-4" />
                        Download Receipt
                    </Button>
                </div>

                {/* Support */}
                <p className="text-center text-sm text-muted mt-6">
                    Need help? <Link href="/support" className="text-accent hover:underline">Contact Support</Link>
                </p>
            </Card>
        </div>
    );
}
