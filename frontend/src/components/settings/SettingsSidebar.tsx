"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
    User,
    Brain,
    Bell,
    Shield,
    CreditCard,
    LayoutGrid,
} from "lucide-react";

const SETTINGS_NAV = [
    { label: "Overview", href: "/settings", icon: LayoutGrid },
    { label: "Accounts", href: "/settings/accounts", icon: User },
    { label: "AI & Intelligence", href: "/settings/ai", icon: Brain },
    { label: "Notifications", href: "/settings/notifications", icon: Bell },
    { label: "Privacy & Data", href: "/settings/privacy", icon: Shield },
    { label: "Billing & Plans", href: "/settings/billing", icon: CreditCard },
];

export default function SettingsSidebar() {
    const pathname = usePathname();

    return (
        <nav className="w-64 shrink-0 space-y-1">
            {SETTINGS_NAV.map((item) => {
                const isActive = pathname === item.href;
                const Icon = item.icon;
                return (
                    <Link
                        key={item.href}
                        href={item.href}
                        className={`
                            flex items-center gap-3 px-3 py-2 rounded-md transition-colors
                            ${isActive
                                ? "bg-accent/10 text-accent font-medium"
                                : "text-muted hover:bg-paper-mid hover:text-ink"
                            }
                        `}
                    >
                        <Icon size={18} className={isActive ? "text-accent" : "text-muted"} />
                        <span className="text-sm">{item.label}</span>
                    </Link>
                );
            })}
        </nav>
    );
}
