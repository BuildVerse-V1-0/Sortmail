"use client";

import React from "react";
import { Search, Bell, User } from "lucide-react";
import Link from "next/link";

interface TopbarProps {
    title: string;
    subtitle?: string;
}

export default function Topbar({ title, subtitle }: TopbarProps) {
    return (
        <header className="h-[56px] border-b border-border-light bg-white/80 backdrop-blur-sm flex items-center px-6 justify-between sticky top-0 z-10">
            <div>
                {subtitle && (
                    <span className="text-xs font-mono text-muted uppercase tracking-widest">{subtitle} /</span>
                )}
                <h1 className="text-lg font-display text-ink leading-tight">{title}</h1>
            </div>

            <div className="flex items-center gap-3">
                {/* Search Trigger */}
                <Link href="/search">
                    <button className="btn-ghost" title="Search (⌘K)">
                        <Search size={16} />
                        <span className="text-xs text-muted hidden sm:inline">⌘K</span>
                    </button>
                </Link>

                {/* Notifications */}
                <Link href="/notifications">
                    <button className="btn-ghost relative" title="Notifications">
                        <Bell size={16} />
                        <span className="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 bg-danger rounded-full border-2 border-white" />
                    </button>
                </Link>

                {/* Avatar */}
                <Link href="/settings">
                    <div className="w-8 h-8 rounded-full bg-paper-deep flex items-center justify-center border border-border-light cursor-pointer hover:border-ink-light transition-colors">
                        <User size={14} className="text-ink-light" />
                    </div>
                </Link>
            </div>
        </header>
    );
}
