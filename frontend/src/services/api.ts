import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
    baseURL: API_URL,
    withCredentials: true, // Essential for HttpOnly Cookie Auth
    headers: {
        'Content-Type': 'application/json',
    },
});

// Response Interceptor: Handle Errors
api.interceptors.response.use(
    (response) => response,
    (error: any) => {
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
