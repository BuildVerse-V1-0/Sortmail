"use client";

import React from "react";
import AppShell from "@/components/layout/AppShell";
import SettingsSidebar from "@/components/settings/SettingsSidebar";

export default function SettingsLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <AppShell title="Settings">
            <div className="max-w-6xl mx-auto py-8 px-6 flex flex-col md:flex-row gap-8">
                <SettingsSidebar />
                <div className="flex-1 min-w-0">
                    {children}
                </div>
            </div>
        </AppShell>
    );
}
