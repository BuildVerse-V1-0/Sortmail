"use client";

import React, { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { ArrowRight, Loader2, Shield, Eye, Github, Sparkles } from "lucide-react";
import Link from "next/link";

export default function LoginPage() {
    const containerRef = useRef<HTMLDivElement>(null);
    const [loading, setLoading] = useState<"google" | "outlook" | null>(null);

    const handleGoogleLogin = async () => {
        try {
            setLoading("google");
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/google`);
            const data = await response.json();
            if (data.auth_url) {
                window.location.href = data.auth_url;
            } else {
                console.error("No auth_url returned", data);
                setLoading(null);
            }
        } catch (error) {
            console.error("Failed to initiate Google login", error);
            setLoading(null);
        }
    };

    useEffect(() => {
        const tl = gsap.timeline({ defaults: { ease: "power3.out" } });

        // Hero text entrance
        tl.fromTo(".hero-headline", { y: 40, opacity: 0 }, { y: 0, opacity: 1, duration: 0.8 });
        tl.fromTo(".hero-sub", { y: 20, opacity: 0 }, { y: 0, opacity: 1, duration: 0.6 }, "-=0.4");
        tl.fromTo(".hero-trust", { y: 15, opacity: 0 }, { y: 0, opacity: 1, duration: 0.5 }, "-=0.3");

        // Auth card entrance
        tl.fromTo(".auth-card", { y: 30, opacity: 0, scale: 0.97 }, { y: 0, opacity: 1, scale: 1, duration: 0.7 }, "-=0.5");
        tl.fromTo(".auth-item", { y: 10, opacity: 0 }, { y: 0, opacity: 1, stagger: 0.08, duration: 0.4 }, "-=0.3");
    }, []);

    const handleLogin = (provider: "google" | "outlook") => {
        setLoading(provider);
        setTimeout(() => {
            window.location.href = `${process.env.NEXT_PUBLIC_API_URL || ""}/api/auth/${provider}`;
        }, 800);
    };

    return (
        <main ref={containerRef} className="min-h-screen w-full bg-paper flex items-center justify-center relative overflow-hidden">
            {/* Subtle warm gradient orbs */}
            <div className="absolute top-[-15%] left-[-10%] w-[700px] h-[700px] bg-[#C05E3C]/5 rounded-full blur-[100px] pointer-events-none" />
            <div className="absolute bottom-[-15%] right-[-8%] w-[600px] h-[600px] bg-[#7C5CFC]/5 rounded-full blur-[100px] pointer-events-none" />

            <div className="max-w-5xl w-full mx-auto px-6 flex flex-col lg:flex-row items-center gap-16 py-12">
                {/* ── Left: Hero Copy ─────────────────────────── */}
                <div className="flex-1 text-center lg:text-left max-w-xl">
                    <h1 className="hero-headline font-display text-5xl lg:text-6xl text-ink leading-[1.1] mb-6">
                        Your inbox,{" "}
                        <span className="italic text-accent">finally</span>{" "}
                        under control.
                    </h1>

                    <p className="hero-sub text-lg text-ink-light leading-relaxed mb-8 max-w-md mx-auto lg:mx-0">
                        SortMail reads your threads, extracts what matters, and drafts replies — so you can focus on decisions, not email.
                    </p>

                    {/* Trust Indicators */}
                    <div className="hero-trust flex flex-wrap justify-center lg:justify-start gap-4 text-sm text-muted">
                        <div className="flex items-center gap-2">
                            <Shield size={14} className="text-success" />
                            <span>Read-only OAuth</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <Eye size={14} className="text-success" />
                            <span>No auto-send</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <Github size={14} className="text-success" />
                            <span>Open source</span>
                        </div>
                    </div>

                    {/* Social Proof */}
                    <div className="hero-trust mt-8 flex items-center gap-3 justify-center lg:justify-start">
                        <div className="flex -space-x-2">
                            {["SC", "LT", "DT"].map((init, i) => (
                                <div
                                    key={i}
                                    className="w-8 h-8 rounded-full bg-paper-deep border-2 border-white flex items-center justify-center text-xs font-mono font-semibold text-ink-light"
                                >
                                    {init}
                                </div>
                            ))}
                        </div>
                        <span className="text-sm text-muted">Trusted by 1,200+ professionals</span>
                    </div>
                </div>

                {/* ── Right: Auth Card ────────────────────────── */}
                <div className="auth-card w-full max-w-[400px] card p-8">
                    {/* Branding */}
                    <div className="auth-item flex flex-col items-center mb-8">
                        <div className="w-12 h-12 rounded-xl bg-accent flex items-center justify-center mb-4">
                            <Sparkles size={22} className="text-white" />
                        </div>
                        <h2 className="text-xl font-display text-ink">Get Started</h2>
                        <p className="text-sm text-muted mt-1">Connect your email in 30 seconds.</p>
                    </div>

                    {/* OAuth Buttons */}
                    <div className="space-y-3">
                        <button
                            onClick={handleGoogleLogin}
                            disabled={loading !== null}
                            className="auth-item w-full h-12 rounded-lg border border-border-light bg-white hover:bg-paper-mid disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-3 text-sm font-medium text-ink transition-all active:scale-[0.98]"
                        >
                            {loading === "google" ? (
                                <Loader2 size={18} className="animate-spin text-muted" />
                            ) : (
                                <>
                                    <svg className="w-5 h-5" viewBox="0 0 24 24">
                                        <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                                        <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                                        <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                                        <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
                                    </svg>
                                    <span>Continue with Google</span>
                                </>
                            )}
                        </button>

                        <button
                            onClick={() => handleLogin("outlook")}
                            disabled={loading !== null}
                            className="auth-item w-full h-12 rounded-lg border border-border-light bg-white hover:bg-paper-mid disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-3 text-sm font-medium text-ink transition-all active:scale-[0.98]"
                        >
                            {loading === "outlook" ? (
                                <Loader2 size={18} className="animate-spin text-muted" />
                            ) : (
                                <>
                                    <svg className="w-5 h-5" viewBox="0 0 24 24">
                                        <path fill="#0078D4" d="M24 7.387v10.478c0 .23-.08.424-.238.576a.806.806 0 01-.595.234h-8.167v-6.29l1.604 1.17a.327.327 0 00.428-.013l4.968-4.155v8.31h6.91l-2.986-11.004V6.69l-1.924-1.6V1.675z" />
                                    </svg>
                                    <span>Continue with Outlook</span>
                                </>
                            )}
                        </button>
                    </div>

                    {/* Divider */}
                    <div className="auth-item flex items-center gap-3 my-6">
                        <div className="flex-1 h-px bg-border-light" />
                        <span className="text-xs text-muted font-mono">OR</span>
                        <div className="flex-1 h-px bg-border-light" />
                    </div>

                    {/* Magic Link */}
                    <div className="auth-item">
                        <input
                            type="email"
                            placeholder="Enter your work email"
                            className="w-full h-12 px-4 rounded-lg border border-border-light bg-white text-sm text-ink placeholder:text-muted focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent/20 transition-all"
                        />
                        <button className="btn-primary w-full mt-3 h-12">
                            Send Magic Link
                            <ArrowRight size={16} />
                        </button>
                    </div>

                    {/* Footer */}
                    <p className="auth-item text-center text-xs text-muted mt-6">
                        By continuing, you agree to our{" "}
                        <Link href="#" className="underline hover:text-ink-light">Terms</Link> and{" "}
                        <Link href="#" className="underline hover:text-ink-light">Privacy Policy</Link>.
                    </p>
                </div>
            </div>
        </main>
    );
}
