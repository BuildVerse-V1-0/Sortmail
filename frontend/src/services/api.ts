import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request Interceptor: Inject Token
api.interceptors.request.use(
    (config) => {
        const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null;
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response Interceptor: Handle Errors (401)
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            // Token expired or invalid
            if (typeof window !== 'undefined') {
                localStorage.removeItem('auth_token');
                // Redirect to login if not already there
                if (!window.location.pathname.startsWith('/login')) {
                    window.location.href = '/login';
                }
            }
        }
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
