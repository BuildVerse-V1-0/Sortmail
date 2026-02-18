"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { useRouter } from "next/navigation";

interface User {
    id: string;
    email: string;
    name: string;
    avatar?: string;
}

interface AuthContextType {
    user: User | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    login: () => Promise<void>;
    logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const router = useRouter();

    // Mock session check on mount
    useEffect(() => {
        const checkSession = async () => {
            // Simulate network delay
            await new Promise((resolve) => setTimeout(resolve, 500));

            // Check localStorage
            const storedUser = localStorage.getItem("sortmail_user");
            if (storedUser) {
                setUser(JSON.parse(storedUser));
            }
            setIsLoading(false);
        };

        checkSession();
    }, []);

    const login = async () => {
        setIsLoading(true);
        // Simulate API call
        await new Promise((resolve) => setTimeout(resolve, 1000));

        const mockUser: User = {
            id: "user-123",
            email: "you@company.com",
            name: "Demo User",
            avatar: "/placeholder-user.jpg"
        };

        setUser(mockUser);
        localStorage.setItem("sortmail_user", JSON.stringify(mockUser));
        setIsLoading(false);
        router.push("/dashboard");
    };

    const logout = async () => {
        setIsLoading(true);
        await new Promise((resolve) => setTimeout(resolve, 500));

        setUser(null);
        localStorage.removeItem("sortmail_user");
        setIsLoading(false);
        router.push("/login");
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
