/**
 * API Client
 * Centralized API calls to backend
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class ApiClient {
    private token: string | null = null;

    setToken(token: string) {
        this.token = token;
    }

    private async fetch<T>(
        endpoint: string,
        options: RequestInit = {}
    ): Promise<T> {
        const headers: Record<string, string> = {
            "Content-Type": "application/json",
            ...((options.headers as Record<string, string>) || {}),
        };

        if (this.token) {
            headers["Authorization"] = `Bearer ${this.token}`;
        }

        const response = await fetch(`${API_URL}${endpoint}`, {
            ...options,
            headers,
        });

        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }

        return response.json();
    }

    // Auth
    async getMe() {
        return this.fetch("/api/auth/me");
    }

    // Tasks
    async getTasks() {
        return this.fetch("/api/tasks/");
    }

    async updateTask(taskId: string, status: string) {
        return this.fetch(`/api/tasks/${taskId}`, {
            method: "PATCH",
            body: JSON.stringify({ status }),
        });
    }

    // Threads
    async getThreads() {
        return this.fetch("/api/threads/");
    }

    async getThread(threadId: string) {
        return this.fetch(`/api/threads/${threadId}`);
    }

    // Drafts
    async generateDraft(threadId: string, tone: string = "normal") {
        return this.fetch("/api/drafts/", {
            method: "POST",
            body: JSON.stringify({ thread_id: threadId, tone }),
        });
    }
}

export const api = new ApiClient();
