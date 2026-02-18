"use client";

import React, { useState } from "react";
import { XCircle, ArrowLeft, MessageSquare } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import Link from "next/link";
import { useRouter } from "next/navigation";

export default function CheckoutCancelPage() {
    const router = useRouter();
    const [feedback, setFeedback] = useState("");
    const [submitted, setSubmitted] = useState(false);

    const handleSubmitFeedback = () => {
        console.log("Feedback:", feedback);
        setSubmitted(true);
    };

    return (
        <div className="min-h-screen bg-paper flex items-center justify-center p-8">
            <Card className="max-w-md w-full p-8">
                <div className="text-center mb-6">
                    <div className="w-20 h-20 rounded-full bg-warning/10 flex items-center justify-center mx-auto mb-4">
                        <XCircle className="w-12 h-12 text-warning" />
                    </div>
                    <h1 className="font-display text-3xl text-ink mb-2">
                        Payment Cancelled
                    </h1>
                    <p className="text-muted">
                        Your payment was cancelled. No charges were made to your account.
                    </p>
                </div>

                {!submitted ? (
                    <>
                        {/* Feedback */}
                        <div className="mb-6">
                            <Label className="text-sm text-ink mb-2 block">
                                Help us improve (optional)
                            </Label>
                            <Textarea
                                placeholder="What made you cancel? Any feedback is appreciated..."
                                value={feedback}
                                onChange={(e) => setFeedback(e.target.value)}
                                rows={4}
                            />
                        </div>

                        {/* Actions */}
                        <div className="space-y-3">
                            {feedback && (
                                <Button
                                    onClick={handleSubmitFeedback}
                                    variant="outline"
                                    className="w-full gap-2"
                                >
                                    <MessageSquare className="w-4 h-4" />
                                    Submit Feedback
                                </Button>
                            )}
                            <Link href="/upgrade">
                                <Button className="w-full gap-2">
                                    <ArrowLeft className="w-4 h-4" />
                                    Return to Plans
                                </Button>
                            </Link>
                            <Link href="/dashboard">
                                <Button variant="outline" className="w-full">
                                    Go to Dashboard
                                </Button>
                            </Link>
                        </div>
                    </>
                ) : (
                    <>
                        <div className="text-center mb-6">
                            <p className="text-ink mb-2">Thank you for your feedback!</p>
                            <p className="text-sm text-muted">
                                We appreciate you taking the time to help us improve.
                            </p>
                        </div>
                        <div className="space-y-3">
                            <Link href="/upgrade">
                                <Button className="w-full gap-2">
                                    <ArrowLeft className="w-4 h-4" />
                                    Return to Plans
                                </Button>
                            </Link>
                            <Link href="/dashboard">
                                <Button variant="outline" className="w-full">
                                    Go to Dashboard
                                </Button>
                            </Link>
                        </div>
                    </>
                )}

                {/* Support */}
                <p className="text-center text-sm text-muted mt-6">
                    Questions? <Link href="/support" className="text-accent hover:underline">Contact Support</Link>
                </p>
            </Card>
        </div>
    );
}
