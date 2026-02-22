import axios from 'axios';

const RAW_URL = process.env.NEXT_PUBLIC_API_URL || 'https://sortmail-production.up.railway.app';
const API_URL = RAW_URL.replace(/^http:\/\/(?!localhost)/, 'https://');

export const api = axios.create({
    baseURL: API_URL,
    withCredentials: true,
    headers: { 'Content-Type': 'application/json' },
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
