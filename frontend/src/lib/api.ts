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

// Intercept 401 Unauthorized globally to boot unauthenticated users to the login screen
if (typeof window !== 'undefined') {
    api.interceptors.response.use(
        (response) => response,
        (error) => {
            if (error.response?.status === 401) {
                // Prevent infinite redirect loops on public paths
                const publicPaths = [
                    '/login', '/privacy', '/terms', '/onboarding', '/help',
                    '/callback', '/magic-link-sent', '/verify', '/reset-password'
                ];
                const currentPath = window.location.pathname;

                if (!publicPaths.some(path => currentPath.startsWith(path)) && currentPath !== '/') {
                    window.location.replace('/login');
                }
            }
            return Promise.reject(error);
        }
    );
}


export const endpoints = {
    dashboard: '/api/dashboard',
    threads: '/api/threads',
    threadArchive: (id: string) => `/api/threads/${id}/archive`,
    threadTrash: (id: string) => `/api/threads/${id}`,
    tasks: '/api/tasks',
    drafts: '/api/drafts',
    chat: '/api/ai/chat',
    waitingFor: '/api/reminders',
    emailSync: '/api/emails/sync',
    emailSyncStatus: '/api/emails/sync/status',
    eventStream: '/api/events/stream',
    authMe: '/api/auth/me',
    updateProfile: '/api/auth/users/me',
    notifications: '/api/notifications',
    notificationsUnreadCount: '/api/notifications/unread-count',
    notificationPrefs: '/api/notifications/preferences',
    settings: '/api/settings',
    settingsAIPreferences: '/api/settings/preferences/ai',
    settingsPrivacyPreferences: '/api/settings/preferences/privacy',
    bin: '/api/bin',
    creditsMe: '/api/credits/me',
    creditsTransactions: '/api/credits/me/transactions',
    contacts: '/api/contacts',
    contactByEmail: (email: string) => `/api/contacts/by-email/${email}`,
    contactThreads: (id: string) => `/api/contacts/${id}/threads`,
    contactUnsubscribe: (id: string) => `/api/contacts/${id}/unsubscribe`,
    contactTags: (id: string) => `/api/contacts/${id}/tags`,
    contactTagRemove: (id: string, tagId: string) => `/api/contacts/${id}/tags/${tagId}`,
    tags: '/api/tags',
    adminUser: (id: string) => `/api/admin/users/${id}`,
    draftApprove: (id: string) => `/api/drafts/${id}/approve`,
    draftSchedule: (id: string) => `/api/drafts/${id}/schedule`,
    draftRegenerate: (id: string) => `/api/drafts/${id}/regenerate`,

    calendarSuggestions: '/api/tasks/calendar-suggestions',
    connectedAccounts: '/api/connected-accounts',
    adminUsers: '/api/admin/users',
    adminMetricsOverview: '/api/admin/metrics/overview',
    adminMetricsApp: '/api/admin/metrics/app',
    adminMetricsRedis: '/api/admin/metrics/redis',
    adminMetricsRedisDetail: '/api/admin/metrics/redis/detail',
    adminMetricsQueue: '/api/admin/metrics/queue',
    adminMetricsAIUsage: '/api/admin/metrics/ai-usage',
    adminMetricsEconomics: '/api/admin/metrics/economics',
    adminMetricsEconomicsTrends: '/api/admin/metrics/economics/trends',
    adminCreditsAdjust: '/api/admin/credits/adjust',
    adminCreditsSummary: '/api/admin/credits/summary',
    adminCreditsTransactions: '/api/admin/credits/transactions',
    helpCategories: '/api/help/categories',
    helpArticle: (slug: string) => `/api/help/articles/${slug}`,
    teamMembers: '/api/settings/team',
    rules: '/api/settings/rules',
    integrations: '/api/settings/integrations',
    sessions: '/api/settings/sessions',
    developer: '/api/settings/developer',
    billingPlan: '/api/settings/billing/plan',
    privacyPolicy: '/api/legal/privacy',
    termsOfService: '/api/legal/terms',
    landingContent: '/api/content/landing',
    onboardingSteps: '/api/onboarding/steps',
    onboardingTips: '/api/onboarding/tips',
    userProfile: '/api/app/profile',
    navCounts: '/api/threads/counts',
    search: '/api/search',
    appStatus: '/api/app/status',
};
