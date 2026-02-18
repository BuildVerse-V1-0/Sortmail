"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
    LayoutDashboard,
    Inbox,
    Search,
    Users,
    CheckSquare,
    FileEdit,
    Clock,
    Calendar,
    Settings,
    LogOut,
    ChevronLeft,
    ChevronRight,
} from "lucide-react";

const NAV_ITEMS = [
    { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
    { label: "Inbox", href: "/inbox", icon: Inbox, badge: 47 },
    { label: "Search", href: "/search", icon: Search },
    { label: "Contacts", href: "/contacts", icon: Users },
    { label: "Tasks", href: "/tasks", icon: CheckSquare, badge: 8 },
    { label: "Drafts", href: "/drafts", icon: FileEdit },
    { label: "Follow-ups", href: "/followups", icon: Clock, badge: 12 },
    { label: "Calendar", href: "/calendar", icon: Calendar },
];

const BOTTOM_ITEMS = [
    { label: "Settings", href: "/settings", icon: Settings },
];

interface SidebarProps {
    collapsed?: boolean;
    onToggle?: () => void;
}

export default function Sidebar({ collapsed = false, onToggle }: SidebarProps) {
    const pathname = usePathname();

    return (
        <aside
            className="flex flex-col bg-surface text-white transition-all duration-300 ease-in-out shrink-0 overflow-hidden"
            style={{ width: collapsed ? 'var(--sidebar-col)' : 'var(--sidebar-w)' }}
        >
            {/* Logo */}
            <div className="flex items-center gap-3 px-4 h-[56px] shrink-0">
                <div className="w-8 h-8 rounded bg-accent flex items-center justify-center shrink-0 shadow-sm">
                    <span className="font-display italic text-white text-xl translate-y-[-1px]">S</span>
                </div>
                {!collapsed && (
                    <span className="font-display italic text-xl text-white tracking-wide opacity-0 animate-fade-in" style={{ animationFillMode: 'forwards' }}>
                        SortMail
                    </span>
                )}
            </div>

            {/* Main Nav */}
            <nav className="flex-1 py-6 px-3 space-y-1 overflow-y-auto scrollbar-hide">
                {NAV_ITEMS.map((item) => {
                    const isActive = pathname === item.href || pathname?.startsWith(item.href + "/");
                    const Icon = item.icon;

                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={`
                                flex items-center gap-3 px-3 py-2 rounded-md transition-all duration-200 group
                                ${isActive ? "bg-white/10 text-white" : "text-white/60 hover:bg-white/5 hover:text-white"}
                                ${collapsed ? "justify-center" : ""}
                            `}
                            title={collapsed ? item.label : undefined}
                        >
                            <Icon size={18} strokeWidth={2} className="shrink-0" />
                            {!collapsed && (
                                <>
                                    <span className="flex-1 text-[13px] font-medium tracking-wide truncate">{item.label}</span>
                                    {item.badge && (
                                        <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded-sm bg-white/20 text-white min-w-[20px] text-center">
                                            {item.badge}
                                        </span>
                                    )}
                                </>
                            )}
                        </Link>
                    );
                })}
            </nav>

            {/* Bottom Section */}
            <div className="py-4 px-3 space-y-1 mt-auto">
                {/* Connection Status */}
                {!collapsed && (
                    <div className="flex items-center gap-2 px-3 py-2 text-[11px] font-mono text-success tracking-wide uppercase">
                        <span className="w-1.5 h-1.5 rounded-full bg-success animate-pulse"></span>
                        Online
                    </div>
                )}

                {BOTTOM_ITEMS.map((item) => {
                    const isActive = pathname === item.href;
                    const Icon = item.icon;
                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={`
                                    flex items-center gap-3 px-3 py-2 rounded-md transition-all duration-200
                                    ${isActive ? "bg-white/10 text-white" : "text-white/60 hover:bg-white/5 hover:text-white"}
                                    ${collapsed ? "justify-center" : ""}
                                `}
                            title={collapsed ? item.label : undefined}
                        >
                            <Icon size={18} strokeWidth={2} className="shrink-0" />
                            {!collapsed && <span className="flex-1 text-[13px] font-medium tracking-wide">{item.label}</span>}
                        </Link>
                    );
                })}

                {/* Collapse Toggle */}
                {onToggle && (
                    <button
                        onClick={onToggle}
                        className="w-full flex items-center gap-3 px-3 py-2 rounded-md text-white/40 hover:text-white hover:bg-white/5 transition-colors cursor-pointer"
                        title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
                    >
                        {collapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
                        {!collapsed && <span className="text-[13px] font-medium">Collapse</span>}
                    </button>
                )}

                {/* User Profile & Sign Out */}
                {!collapsed && (
                    <div className="mt-4 pt-4 border-t border-white/10 flex items-center gap-3 px-1">
                        <div className="w-8 h-8 rounded-full bg-surface-3/20 border border-white/10 shrink-0 relative">
                            {/* Avatar placeholder */}
                            <div className="absolute inset-0 flex items-center justify-center text-[10px] font-bold text-white/80">IR</div>
                        </div>
                        <div className="flex-1 min-w-0">
                            <div className="text-[12px] font-medium text-white truncate">Isabella R.</div>
                            <div className="text-[10px] text-white/50 truncate">Pro Plan</div>
                        </div>
                        <button className="text-white/40 hover:text-white transition-colors" title="Sign Out">
                            <LogOut size={14} />
                        </button>
                    </div>
                )}
            </div>
        </aside>
    );
}
