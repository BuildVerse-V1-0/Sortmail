import axios from 'axios';

const API_URL = ""; // Relative path to leverage Next.js Rewrites (Proxy)

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
    (error) => {
        // We removed the auto-redirect here to prevent race conditions.
        // AuthContext handles the global auth state.
        return Promise.reject(error);
    }
);

// API Methods
export const authApi = {
    getGoogleAuthUrl: () => api.get('/api/auth/google').then(res => res.data),
    logout: () => api.post('/api/auth/logout'),
    getCurrentUser: () => api.get('/api/auth/me').then(res => res.data),
};

export const threadsApi = {
    // We'll replace the mock data calls with these
    getThreads: (page = 1, limit = 50) => api.get(`/api/threads?page=${page}&limit=${limit}`).then(res => res.data),
    getThread: (id: string) => api.get(`/api/threads/${id}`).then(res => res.data),
};

export const dashboardApi = {
    getStats: () => api.get('/api/dashboard/stats').then(res => res.data),
}
