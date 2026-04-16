"use client";

import React, { useEffect, useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Loader2, CheckCircle2, XCircle, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import gsap from "gsap";
import { getApiUrl } from "@/lib/config";

function CallbackContent() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
    const [message, setMessage] = useState("Securing your session...");

    useEffect(() => {
        const tl = gsap.timeline({ defaults: { ease: "power3.out" } });
        tl.fromTo(".callback-card", { y: 20, opacity: 0, scale: 0.98 }, { y: 0, opacity: 1, scale: 1, duration: 0.8 });

        const hashParams = new URLSearchParams(window.location.hash.replace(/^#/, ""));
        const fragmentToken = hashParams.get("access_token");
        const queryToken = searchParams.get("access_token");
        const token = fragmentToken || queryToken;
        const code = searchParams.get("code");
        const error = searchParams.get("error");

        const verifySessionWithRetry = async (tokenForHeader?: string | null) => {
            const maxAttempts = 8;
            for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
                try {
                    const res = await fetch(getApiUrl("/api/auth/me"), {
                        credentials: "include",
                        headers: {
                            ...(tokenForHeader ? { Authorization: `Bearer ${tokenForHeader}` } : {}),
                        },
                    });
                    if (res.ok) return true;
                } catch {
                    // keep retrying for transient DNS/network callback races
                }

                await new Promise((resolve) => setTimeout(resolve, 250 * attempt));
            }
            return false;
        };

        if (error) {
            setStatus("error");
            setMessage("Authentication failed. Please try again.");
            return;
        }

        if (token) {
            localStorage.setItem("access_token", token);
            // Clear fragment/query token from visible URL.
            window.history.replaceState({}, "", "/callback");

            const continueWithToken = async () => {
                const ok = await verifySessionWithRetry(token);
                if (!ok) {
                    setStatus("error");
                    setMessage("Session could not be restored. Please sign in again.");
                    return;
                }

                setStatus("success");
                setMessage("Session established. Redirecting to your dashboard...");
                setTimeout(() => {
                    router.push("/dashboard");
                }, 800);
            };

            continueWithToken();
            return;
        }

        if (code) {
            // Cookie-based fallback path: verify session then continue.
            const verifySession = async () => {
                const ok = await verifySessionWithRetry(null);
                if (ok) {
                    setStatus("success");
                    setMessage("Account connected successfully!");
                    gsap.to(".status-icon", { scale: 1.2, duration: 0.4, yoyo: true, repeat: 1 });
                    setTimeout(() => {
                        router.push("/dashboard");
                    }, 800);
                } else {
                    setStatus("error");
                    setMessage("Session could not be restored. Please sign in again.");
                }
            };

            verifySession();
        } else {
            setStatus("error");
            setMessage("Invalid callback parameters.");
        }
    }, [searchParams, router]);

    return (
        <div className="min-h-screen bg-paper flex items-center justify-center p-8 relative overflow-hidden">
            {/* Background Orbs */}
            <div className="absolute top-[-15%] left-[-10%] w-[700px] h-[700px] bg-[#C05E3C]/5 rounded-full blur-[100px] pointer-events-none" />
            <div className="absolute bottom-[-15%] right-[-8%] w-[600px] h-[600px] bg-[#7C5CFC]/5 rounded-full blur-[100px] pointer-events-none" />

            <Card className="callback-card max-w-md w-full p-10 text-center bg-white/80 backdrop-blur-md border-border/50 shadow-2xl shadow-ink/5 z-10">
                <div className="status-icon mb-8 flex justify-center">
                    {status === "loading" && (
                        <div className="w-16 h-16 rounded-2xl bg-accent/10 flex items-center justify-center relative">
                            <Loader2 className="w-8 h-8 text-accent animate-spin" />
                            <Sparkles className="absolute -top-2 -right-2 w-5 h-5 text-accent/40" />
                        </div>
                    )}

                    {status === "success" && (
                        <div className="w-16 h-16 rounded-2xl bg-success/10 flex items-center justify-center">
                            <CheckCircle2 className="w-8 h-8 text-success" />
                        </div>
                    )}

                    {status === "error" && (
                        <div className="w-16 h-16 rounded-2xl bg-danger/10 flex items-center justify-center">
                            <XCircle className="w-8 h-8 text-danger" />
                        </div>
                    )}
                </div>

                <h1 className="font-display text-2xl text-ink mb-3">
                    {status === "loading" ? "Finalizing Login" : status === "success" ? "You're in!" : "Connection Error"}
                </h1>

                <p className="text-muted-foreground text-sm mb-8 leading-relaxed">
                    {message}
                </p>

                {status === "error" && (
                    <div className="flex flex-col gap-3">
                        <Button className="w-full h-11" onClick={() => router.push("/login")}>
                            Try Again
                        </Button>
                        <Button variant="ghost" className="w-full h-11" onClick={() => router.push("/")}>
                            Return Home
                        </Button>
                    </div>
                )}

                {status === "success" && (
                    <div className="flex items-center justify-center gap-2 text-xs text-muted font-mono animate-pulse">
                        <div className="w-1 h-1 rounded-full bg-success" />
                        REDIRECTING TO DASHBOARD
                    </div>
                )}
            </Card>
        </div>
    );
}

export default function CallbackPage() {
    return (
        <Suspense fallback={
            <div className="min-h-screen bg-paper flex items-center justify-center">
                <Loader2 className="w-8 h-8 text-accent animate-spin opacity-20" />
            </div>
        }>
            <CallbackContent />
        </Suspense>
    );
}
