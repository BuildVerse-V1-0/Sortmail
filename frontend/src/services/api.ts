import axios from 'axios';
import { config } from '@/lib/config';

const API_URL = config.apiUrl || undefined;

export const api = axios.create({
    baseURL: API_URL,
    withCredentials: true,
    headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
    if (typeof window !== 'undefined') {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers = config.headers ?? {};
            config.headers.Authorization = `Bearer ${token}`;
        }
    }
    return config;
});

api.interceptors.request.use((config) => {
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
});

api.interceptors.response.use(
    (response) => response,
    (error: any) => {
        console.error(`❌ API Error: ${error.config?.url}`, error.response?.status);
        return Promise.reject(error);
    }
);

export const dashboardApi = {
    getStats: async () => (await api.get('/api/dashboard/stats')).data,
};

export const threadsApi = {
    getThreads: async () => (await api.get('/api/threads')).data,
    getThread: async (id: string) => (await api.get(`/api/threads/${id}`)).data,
    getIntel: async (id: string) => (await api.get(`/api/threads/${id}/intel`)).data,
};
