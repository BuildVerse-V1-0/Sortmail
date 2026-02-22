import axios from 'axios';

const RAW_URL = process.env.NEXT_PUBLIC_API_URL || 'https://sortmail-production.up.railway.app';
const API_URL = RAW_URL.replace(/^http:\/\/(?!localhost)/, 'https://');

export const api = axios.create({
    baseURL: API_URL,
    withCredentials: true,
    headers: { 'Content-Type': 'application/json' },
});

export const endpoints = {
    dashboard: '/api/dashboard',
    threads: '/api/threads',
    tasks: '/api/tasks',
    drafts: '/api/drafts',
    waitingFor: '/api/reminders',
    emailSync: '/api/emails/sync',
    emailSyncStatus: '/api/emails/sync/status',

    authMe: '/api/auth/me',
    updateProfile: '/api/auth/users/me',
    notifications: '/api/notifications',
    notificationPrefs: '/api/notifications/preferences',
    creditsMe: '/api/credits/me',
    creditsTransactions: '/api/credits/me/transactions',
    contacts: '/api/threads/contacts',
    calendarSuggestions: '/api/tasks/calendar-suggestions',
    connectedAccounts: '/api/connected-accounts',
    adminUsers: '/api/admin/users',
    adminCreditsAdjust: '/api/admin/credits/adjust',
};
