import axios from 'axios';

const RAW_API_URL = (() => {
    const url = process.env.NEXT_PUBLIC_API_URL;
    if (!url && process.env.NODE_ENV === 'production') {
        // Hard error in production — missing env var would silently send to localhost
        throw new Error('NEXT_PUBLIC_API_URL must be set in production');
    }
    return url || 'http://localhost:8000';
})();

// Force HTTPS if page is already on HTTPS (guards against http:// env var)
const API_URL =
    typeof window !== 'undefined' && window.location.protocol === 'https:'
        ? RAW_API_URL.replace(/^http:\/\//, 'https://')
        : RAW_API_URL;

export const api = axios.create({
    baseURL: API_URL,
    withCredentials: true, // Required: sends HttpOnly auth cookie cross-origin
    headers: {
        'Content-Type': 'application/json',
    },
});

export const endpoints = {
    // Core
    dashboard: '/api/dashboard',
    threads: '/api/threads',
    tasks: '/api/tasks',
    drafts: '/api/drafts',
    waitingFor: '/api/reminders',
    emailSync: '/api/emails/sync',
    // User
    authMe: '/api/auth/me',
    updateProfile: '/api/auth/users/me',
    // Notifications
    notifications: '/api/notifications',
    notificationPrefs: '/api/notifications/preferences',
    // Credits
    creditsMe: '/api/credits/me',
    creditsTransactions: '/api/credits/me/transactions',
    // Contacts & Calendar
    contacts: '/api/threads/contacts',
    calendarSuggestions: '/api/tasks/calendar-suggestions',
    // Accounts
    connectedAccounts: '/api/connected-accounts',
    // Admin
    adminUsers: '/api/admin/users',
    adminCreditsAdjust: '/api/admin/credits/adjust',
};

