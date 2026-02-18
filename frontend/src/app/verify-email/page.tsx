"use client";

import React, { useEffect, useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { CheckCircle, XCircle, Mail, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

function VerifyEmailContent() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const [status, setStatus] = useState<"verifying" | "success" | "error" | "resend">("verifying");
    const [email, setEmail] = useState("");

    useEffect(() => {
        const token = searchParams.get("token");

        if (!token) {
            setStatus("error");
            return;
        }

        // Simulate email verification
        setTimeout(() => {
            // Simulate success (in real app, verify token with backend)
            setStatus("success");
            setTimeout(() => {
                router.push("/dashboard");
            }, 2000);
        }, 1500);
    }, [searchParams, router]);

    const handleResend = () => {
        console.log("Resending verification email to:", email);
        setStatus("success");
    };

    return (
        <div className="min-h-screen bg-paper flex items-center justify-center p-8">
            <Card className="max-w-md w-full p-8 text-center">
                {status === "verifying" && (
                    <>
                        <Loader2 className="w-16 h-16 text-accent mx-auto mb-4 animate-spin" />
                        <h1 className="font-display text-2xl text-ink mb-2">
                            Verifying Email...
                        </h1>
                        <p className="text-muted">Please wait while we verify your email address</p>
                    </>
                )}

                {status === "success" && (
                    <>
                        <CheckCircle className="w-16 h-16 text-success mx-auto mb-4" />
                        <h1 className="font-display text-2xl text-ink mb-2">
                            Email Verified!
                        </h1>
                        <p className="text-muted mb-4">
                            Your email has been successfully verified
                        </p>
                        <p className="text-sm text-muted">Redirecting to dashboard...</p>
                    </>
                )}

                {status === "error" && (
                    <>
                        <XCircle className="w-16 h-16 text-danger mx-auto mb-4" />
                        <h1 className="font-display text-2xl text-ink mb-2">
                            Verification Failed
                        </h1>
                        <p className="text-muted mb-6">
                            The verification link is invalid or has expired
                        </p>
                        <Button onClick={() => setStatus("resend")} className="w-full">
                            Resend Verification Email
                        </Button>
                    </>
                )}

                {status === "resend" && (
                    <>
                        <Mail className="w-16 h-16 text-accent mx-auto mb-4" />
                        <h1 className="font-display text-2xl text-ink mb-2">
                            Resend Verification
                        </h1>
                        <p className="text-muted mb-6">
                            Enter your email address to receive a new verification link
                        </p>
                        <div className="space-y-4">
                            <Input
                                type="email"
                                placeholder="your.email@example.com"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                            />
                            <Button onClick={handleResend} className="w-full" disabled={!email}>
                                Send Verification Email
                            </Button>
                        </div>
                    </>
                )}
            </Card>
        </div>
    );
}

export default function VerifyEmailPage() {
    return (
        <Suspense fallback={
            <div className="min-h-screen bg-paper flex items-center justify-center p-8">
                <Card className="max-w-md w-full p-8 text-center">
                    <Loader2 className="w-16 h-16 text-accent mx-auto mb-4 animate-spin" />
                    <h1 className="font-display text-2xl text-ink mb-2">Loading...</h1>
                </Card>
            </div>
        }>
            <VerifyEmailContent />
        </Suspense>
    );
}
