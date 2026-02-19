"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { useRouter } from "next/navigation";

// Define the User type based on backend response
interface User {
    id: string;
    email: string;
    name: string;
    avatar?: string;
    picture_url?: string; // Backend uses picture_url
}

interface AuthContextType {
    user: User | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    login: () => void; // Redirects to Google
    logout: () => void;
    checkSession: () => Promise<boolean>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// API URL from env or default
const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://sortmail-production.up.railway.app";

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const router = useRouter();

    // Fetch user from backend using HttpOnly Cookie
    const checkSession = async () => {
        try {
            const res = await fetch(`${API_URL}/api/auth/me`, {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                },
                credentials: "include", // Important: Send Cookies
            });

            if (res.ok) {
                const userData = await res.json();
                setUser(userData);
                return true;
            } else {
                console.log("No active session (401)");
                setUser(null);
                return false;
            }
        } catch (error) {
            console.error("Auth check error", error);
            setUser(null);
            return false;
        }
    };

    // Initial Session Check
    useEffect(() => {
        const initAuth = async () => {
            await checkSession();
            setIsLoading(false);
        };
        initAuth();
    }, []);

    // Redirect to Backend OAuth endpoint
    const login = () => {
        window.location.href = `${API_URL}/api/auth/google`;
    };

    const logout = async () => {
        try {
            await fetch(`${API_URL}/api/auth/logout`, { method: "POST", credentials: "include" });
        } catch (e) {
            console.error("Logout failed", e);
        }
        setUser(null);
        router.push("/login");
    };

    return (
        <AuthContext.Provider value={{ user, isAuthenticated: !!user, isLoading, login, logout, checkSession }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return context;
}
