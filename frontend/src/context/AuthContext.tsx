"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { useRouter, useSearchParams } from "next/navigation";

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
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// API URL from env or default
const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://sortmail-production.up.railway.app";

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const router = useRouter();
    const searchParams = useSearchParams();

    // Fetch user from backend using token
    const fetchUser = async (token: string) => {
        try {
            const res = await fetch(`${API_URL}/api/auth/me`, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });

            if (res.ok) {
                const userData = await res.json();
                setUser(userData);
                return true;
            } else {
                console.error("Failed to fetch user", res.status);
                localStorage.removeItem("sortmail_token");
                return false;
            }
        } catch (error) {
            console.error("Auth fetch error", error);
            localStorage.removeItem("sortmail_token");
            return false;
        }
    };

    useEffect(() => {
        const initAuth = async () => {
            // 1. Check URL for token (OAuth callback)
            const urlToken = searchParams?.get("token");

            if (urlToken) {
                console.log("🔗 Token found in URL, authenticating...");
                localStorage.setItem("sortmail_token", urlToken);

                // Fetch user immediately
                const success = await fetchUser(urlToken);
                if (success) {
                    console.log("✅ OAuth Login Success");
                    router.replace("/dashboard"); // Clean URL and redirect
                } else {
                    setIsLoading(false);
                }
            }
            // 2. Check LocalStorage (Session restore)
            else {
                const storedToken = localStorage.getItem("sortmail_token");
                if (storedToken) {
                    await fetchUser(storedToken);
                }
            }
            setIsLoading(false);
        };

        initAuth();
    }, [searchParams, router]);

    // Redirect to Backend OAuth endpoint
    const login = () => {
        window.location.href = `${API_URL}/api/auth/google`;
    };

    const logout = () => {
        localStorage.removeItem("sortmail_token");
        setUser(null);
        router.push("/login"); // or home
    };

    return (
        <AuthContext.Provider value={{ user, isAuthenticated: !!user, isLoading, login, logout }}>
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
