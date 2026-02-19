import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add auth interceptor if needed
api.interceptors.request.use((config) => {
    // const token = localStorage.getItem('sortmail_token');
    // if (token) {
    //     config.headers.Authorization = `Bearer ${token}`;
    // }
    return config;
});

export const endpoints = {
    dashboard: '/dashboard',
    threads: '/threads',
    tasks: '/tasks',
    drafts: '/drafts',
    waitingFor: '/waiting-for',
};
