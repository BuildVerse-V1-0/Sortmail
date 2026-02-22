import axios from 'axios';

const _raw = (() => {
    const url = process.env.NEXT_PUBLIC_API_URL;
    if (!url && process.env.NODE_ENV === 'production') {
        throw new Error('NEXT_PUBLIC_API_URL must be set in production');
    }
    return url || 'http://localhost:8000';
})();

// Replace http:// with https:// for all non-localhost URLs
// (works at module init during SSR — no window dependency)
const API_URL = /localhost|127\.0\.0\.1/.test(_raw)
    ? _raw
    : _raw.replace(/^http:\/\//, 'https://');

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

