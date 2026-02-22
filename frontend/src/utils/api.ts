const RAW_URL = process.env.NEXT_PUBLIC_API_URL || 'https://sortmail-production.up.railway.app';
const API_URL = RAW_URL.replace(/^http:\/\/(?!localhost)/, 'https://');

export const api = {
    async fetch<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
        const response = await fetch(`${API_URL}${endpoint}`, {
            ...options,
            credentials: 'include',
            headers: { 'Content-Type': 'application/json', ...(options.headers ?? {}) },
        });
        if (!response.ok) throw new Error(`API Error: ${response.status}`);
        return response.json();
    },
    getMe: () => api.fetch('/api/auth/me'),
    getTasks: () => api.fetch('/api/tasks/'),
    getThreads: () => api.fetch('/api/threads/'),
    getThread: (id: string) => api.fetch(`/api/threads/${id}`),
    generateDraft: (threadId: string, tone = 'normal') =>
        api.fetch('/api/drafts/', { method: 'POST', body: JSON.stringify({ thread_id: threadId, tone }) }),
};
