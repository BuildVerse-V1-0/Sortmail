import axios from 'axios';

const _raw = (() => {
    const url = process.env.NEXT_PUBLIC_API_URL;
    if (!url && process.env.NODE_ENV === 'production') {
        throw new Error('NEXT_PUBLIC_API_URL must be set in production');
    }
    return url || 'http://localhost:8000';
})();
const API_URL = /localhost|127\.0\.0\.1/.test(_raw)
    ? _raw
    : _raw.replace(/^http:\/\//, 'https://');

export const api = axios.create({
    baseURL: API_URL,
    withCredentials: true, // Essential for HttpOnly Cookie Auth
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request Interceptor: Debug Logs
api.interceptors.request.use((config) => {
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
});

// Response Interceptor: Handle Errors
api.interceptors.response.use(
    (response) => {
        console.log(`✅ API Success: ${response.config.url}`);
        return response;
    },
    (error: any) => {
        console.error(`❌ API Error: ${error.config?.url}`, error.response?.status);
        // We removed the auto-redirect here to prevent race conditions.
        // AuthContext handles the global auth state.
        return Promise.reject(error);
    }
);

export const dashboardApi = {
    getStats: async () => {
        const response = await api.get('/api/dashboard/stats');
        return response.data;
    },
};
