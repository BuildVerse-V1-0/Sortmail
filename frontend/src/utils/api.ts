import { getApiUrl } from '@/lib/config';

export const api = {
    async fetch<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
        const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
        const response = await fetch(getApiUrl(endpoint), {
            ...options,
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                ...(token ? { Authorization: `Bearer ${token}` } : {}),
                ...(options.headers ?? {}),
            },
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
