/**
 * API Client (utils/api.ts)
 * Legacy class-based client — coerces http:// to https:// for all non-localhost URLs.
 */

const _raw = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_URL = /localhost|127\.0\.0\.1/.test(_raw)
    ? _raw
    : _raw.replace(/^http:\/\//, 'https://');

class ApiClient {
    private async fetch<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
        const headers: Record<string, string> = {
            'Content-Type': 'application/json',
            ...((options.headers as Record<string, string>) || {}),
        };

        const response = await fetch(`${API_URL}${endpoint}`, {
            ...options,
            headers,
            credentials: 'include',
        });

        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }

        return response.json();
    }

    async getMe() { return this.fetch('/api/auth/me'); }
    async getTasks() { return this.fetch('/api/tasks/'); }
    async updateTask(taskId: string, status: string) {
        return this.fetch(`/api/tasks/${taskId}`, { method: 'PATCH', body: JSON.stringify({ status }) });
    }
    async getThreads() { return this.fetch('/api/threads/'); }
    async getThread(threadId: string) { return this.fetch(`/api/threads/${threadId}`); }
    async generateDraft(threadId: string, tone: string = 'normal') {
        return this.fetch('/api/drafts/', { method: 'POST', body: JSON.stringify({ thread_id: threadId, tone }) });
    }
}

export const api = new ApiClient();
