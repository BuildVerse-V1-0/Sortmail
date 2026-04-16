"use client";

import React from "react";
import { AuthProvider } from "@/context/AuthContext";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useRealtimeEvents } from "@/hooks/useRealtimeEvents";
import { useAuth } from "@/context/AuthContext";
import { usePathname } from "next/navigation";

const queryClient = new QueryClient();

function GlobalRealtimeListener() {
    const { isAuthenticated } = useAuth();
    const pathname = usePathname();
    const publicPaths = [
        '/login', '/privacy', '/terms', '/onboarding', '/help',
        '/callback', '/magic-link-sent', '/verify', '/reset-password'
    ];
    const isPublicPath = publicPaths.some((path) => pathname?.startsWith(path));

    useRealtimeEvents(Boolean(isAuthenticated && !isPublicPath));
    return null;
}

export function Providers({ children }: { children: React.ReactNode }) {
    return (
        <QueryClientProvider client={queryClient}>
            <AuthProvider>
                <GlobalRealtimeListener />
                {children}
            </AuthProvider>
        </QueryClientProvider>
    );
}
