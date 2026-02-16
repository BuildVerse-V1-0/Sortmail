"use client";

import React, { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { Command, ArrowRight, Loader2, CheckCircle2 } from "lucide-react";
import Link from "next/link";

export default function LoginPage() {
    const containerRef = useRef<HTMLDivElement>(null);
    const [loading, setLoading] = useState<"google" | "outlook" | null>(null);

    useEffect(() => {
        const tl = gsap.timeline();

        // Background elements
        tl.fromTo(".bg-orb",
            { scale: 0.8, opacity: 0 },
            { scale: 1, opacity: 1, duration: 1.5, ease: "power2.out", stagger: 0.2 }
        );

        // Card entrance
        tl.fromTo(".auth-card",
            { y: 30, opacity: 0, scale: 0.95 },
            { y: 0, opacity: 1, scale: 1, duration: 0.8, ease: "power3.out" },
            "-=1.0"
        );

        // Content stagger
        tl.fromTo(".auth-item",
            { y: 10, opacity: 0 },
            { y: 0, opacity: 1, stagger: 0.1, duration: 0.5, ease: "power2.out" },
            "-=0.4"
        );
    }, []);

    const handleLogin = (provider: "google" | "outlook") => {
        setLoading(provider);
        // Simulate redirect delay
        setTimeout(() => {
            window.location.href = `${process.env.NEXT_PUBLIC_API_URL || ''}/api/auth/${provider}`;
        }, 800);
    };

    return (
        <main ref={containerRef} className="min-h-screen w-full bg-[#09090B] flex items-center justify-center relative overflow-hidden font-sans selection:bg-indigo-500/30 text-zinc-100">
            {/* Ambient Background */}
            <div className="bg-orb absolute top-[-20%] left-[-10%] w-[800px] h-[800px] bg-indigo-600/10 rounded-full blur-[120px] pointer-events-none" />
            <div className="bg-orb absolute bottom-[-20%] right-[-10%] w-[800px] h-[800px] bg-purple-600/10 rounded-full blur-[120px] pointer-events-none" />

            {/* Auth Card */}
            <div className="auth-card relative w-full max-w-[420px] mx-4 p-1 rounded-2xl bg-gradient-to-b from-white/10 to-white/5 shadow-2xl backdrop-blur-xl border border-white/10">
                <div className="bg-[#09090B]/80 backdrop-blur-md rounded-xl p-8 sm:p-10 border border-white/5 relative overflow-hidden group">

                    {/* Top Glow Overlay */}
                    <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-indigo-500 to-transparent opacity-50" />

                    {/* Branding */}
                    <div className="auth-item flex flex-col items-center mb-10">
                        <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-indigo-600 to-purple-700 flex items-center justify-center shadow-[0_0_20px_rgba(79,70,229,0.3)] mb-4 group-hover:scale-105 transition-transform duration-500">
                            <Command size={28} className="text-white" />
                        </div>
                        <h1 className="text-3xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-b from-white to-zinc-400">
                            SortMail
                        </h1>
                        <p className="text-zinc-500 text-sm mt-2 text-center max-w-[260px]">
                            Your intelligent, AI-powered email workspace.
                        </p>
                    </div>

                    {/* Actions */}
                    <div className="space-y-4">
                        <button
                            onClick={() => handleLogin('google')}
                            disabled={loading !== null}
                            className="auth-item w-full bg-white text-black hover:bg-zinc-200 disabled:opacity-70 disabled:cursor-not-allowed h-12 rounded-lg font-medium text-sm flex items-center justify-center gap-3 transition-all transform active:scale-[0.98] group/btn relative overflow-hidden"
                        >
                            {loading === 'google' ? (
                                <Loader2 size={18} className="animate-spin text-zinc-600" />
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
                            onClick={() => handleLogin('outlook')}
                            disabled={loading !== null}
                            className="auth-item w-full bg-[#18181B] border border-[#27272a] hover:border-zinc-600 text-zinc-200 hover:text-white disabled:opacity-70 disabled:cursor-not-allowed h-12 rounded-lg font-medium text-sm flex items-center justify-center gap-3 transition-all transform active:scale-[0.98]"
                        >
                            {loading === 'outlook' ? (
                                <Loader2 size={18} className="animate-spin" />
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

                    <div className="auth-item mt-8 pt-8 border-t border-white/5">
                        <div className="flex items-center justify-center gap-6 text-xs text-zinc-500">
                            <div className="flex items-center gap-2">
                                <CheckCircle2 size={14} className="text-emerald-500/70" />
                                <span>SOC2 Compliant</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <CheckCircle2 size={14} className="text-emerald-500/70" />
                                <span>End-to-End Encrypted</span>
                            </div>
                        </div>
                    </div>

                    <div className="auth-item mt-6 text-center">
                        <p className="text-[10px] text-zinc-600">
                            By continuing, you agree to our <Link href="#" className="underline hover:text-zinc-400">Terms</Link> and <Link href="#" className="underline hover:text-zinc-400">Privacy Policy</Link>.
                        </p>
                    </div>

                </div>
            </div>

            {/* Corner Info */}
            <div className="absolute bottom-8 right-8 text-right hidden sm:block opacity-40 hover:opacity-100 transition-opacity">
                <p className="text-xs text-zinc-500 font-mono">Build v1.0.4</p>
                <p className="text-xs text-zinc-600">SortMail Inc.</p>
            </div>
        </main>
    );
}
