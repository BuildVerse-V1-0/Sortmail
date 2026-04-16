import { createContext, useContext, useEffect, useState, ReactNode, useCallback } from "react";
import { useRouter } from "next/navigation";
import { User } from "@/types";
import { api } from "../services/api";
import { getApiUrl } from "@/lib/config";

interface AuthContextType {
    user: User | null;
    isLoading: boolean;
    login: () => void;
    logout: () => void;
    checkSession: () => Promise<boolean>;
    isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const router = useRouter();

    const redirectToLogin = useCallback(() => {
        if (typeof window === "undefined") return;

        const currentPath = window.location.pathname;
        const publicPaths = [
            '/login', '/privacy', '/terms', '/onboarding', '/help',
            '/callback', '/magic-link-sent', '/verify', '/reset-password'
        ];

        if (!publicPaths.some((path) => currentPath.startsWith(path)) && currentPath !== '/') {
            router.replace('/login');
        }
    }, [router]);

    const checkSession = useCallback(async () => {
        const checkOnce = async (): Promise<boolean> => {
            const url = getApiUrl("/api/auth/me");
            const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
            const res = await fetch(url, {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                    ...(token ? { Authorization: `Bearer ${token}` } : {}),
                },
                credentials: "include"
            });

            if (res.ok) {
                const userData = await res.json();
                setUser(userData);
                return true;
            }

            setUser(null);
            if (res.status === 401) {
                redirectToLogin();
            }
            return false;
        };

        try {
            console.log("🔍 Checking Session...");
            return await checkOnce();
        } catch (error) {
            // OAuth callback and flaky DNS can race briefly; retry once before failing.
            try {
                await new Promise((resolve) => setTimeout(resolve, 350));
                return await checkOnce();
            } catch (retryError) {
                console.error("Session check failed", retryError);
                setUser(null);
                return false;
            }
        } finally {
            setIsLoading(false);
        }
    }, [redirectToLogin]);

    useEffect(() => {
        checkSession();
    }, [checkSession]);

    const login = () => {
        window.location.href = getApiUrl("/api/auth/google");
    };

    const logout = async () => {
        try {
            await api.post('/api/auth/logout');
            if (typeof window !== "undefined") {
                localStorage.removeItem("access_token");
            }
            setUser(null);
            router.push('/login');
        } catch (error) {
            console.error("Logout failed", error);
        }
    };

    return (
        <AuthContext.Provider value={{ 
            user, 
            isLoading, 
            isAuthenticated: !!user, 
            login, 
            logout, 
            checkSession 
        }}>
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
