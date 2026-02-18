"use client";

import React, { useEffect, useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Loader2, CheckCircle, XCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

function CallbackContent() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
    const [message, setMessage] = useState("Connecting your account...");

    useEffect(() => {
        // Simulate OAuth callback processing
        const code = searchParams.get("code");
        const error = searchParams.get("error");

        if (error) {
            setStatus("error");
            setMessage("Failed to connect your account. Please try again.");
            return;
        }

        if (code) {
            // Simulate API call to exchange code for tokens
            setTimeout(() => {
                setStatus("success");
                setMessage("Account connected successfully!");
                setTimeout(() => {
                    router.push("/onboarding");
                }, 1500);
            }, 2000);
        } else {
            setStatus("error");
            setMessage("Invalid callback. Missing authorization code.");
        }
    }, [searchParams, router]);

    return (
        <div className="min-h-screen bg-paper flex items-center justify-center p-8">
            <Card className="max-w-md w-full p-8 text-center">
                {status === "loading" && (
                    <>
                        <Loader2 className="w-16 h-16 text-accent mx-auto mb-4 animate-spin" />
                        <h1 className="font-display text-2xl text-ink mb-2">
                            Connecting...
                        </h1>
                        <p className="text-muted">{message}</p>
                    </>
                )}

                {status === "success" && (
                    <>
                        <CheckCircle className="w-16 h-16 text-success mx-auto mb-4" />
                        <h1 className="font-display text-2xl text-ink mb-2">
                            Success!
                        </h1>
                        <p className="text-muted mb-4">{message}</p>
                        <p className="text-sm text-muted">Redirecting to onboarding...</p>
                    </>
                )}

                {status === "error" && (
                    <>
                        <XCircle className="w-16 h-16 text-danger mx-auto mb-4" />
                        <h1 className="font-display text-2xl text-ink mb-2">
                            Connection Failed
                        </h1>
                        <p className="text-muted mb-6">{message}</p>
                        <div className="flex gap-3 justify-center">
                            <Button onClick={() => router.push("/login")}>
                                Try Again
                            </Button>
                            <Button variant="outline" onClick={() => router.push("/")}>
                                Go Home
                            </Button>
                        </div>
                    </>
                )}
            </Card>
        </div>
    );
}

export default function CallbackPage() {
    return (
        <Suspense fallback={
            <div className="min-h-screen bg-paper flex items-center justify-center p-8">
                <Card className="max-w-md w-full p-8 text-center">
                    <Loader2 className="w-16 h-16 text-accent mx-auto mb-4 animate-spin" />
                    <h1 className="font-display text-2xl text-ink mb-2">Loading...</h1>
                </Card>
            </div>
        }>
            <CallbackContent />
        </Suspense>
    );
}
