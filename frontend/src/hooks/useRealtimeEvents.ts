/**
 * useRealtimeEvents — SSE hook for real-time inbox updates
 *
 * Subscribes to /api/events/stream (Server-Sent Events).
 * When the backend publishes 'intel_ready' or 'new_emails',
 * React Query cache is invalidated so the inbox refreshes automatically.
 *
 * Usage: call once at app root or per-page (idempotent — one connection per mount)
 */

import { useEffect, useRef } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { getApiUrl } from '@/lib/config';

type NotificationPrefs = {
    push_enabled?: boolean;
    quiet_hours_start?: string | null;
    quiet_hours_end?: string | null;
};

function inQuietHours(start?: string | null, end?: string | null): boolean {
    if (!start || !end) return false;
    const toMinutes = (value: string) => {
        const [h, m] = value.split(':').map(Number);
        if (!Number.isFinite(h) || !Number.isFinite(m)) return null;
        return h * 60 + m;
    };
    const startMin = toMinutes(start);
    const endMin = toMinutes(end);
    if (startMin === null || endMin === null) return false;

    const now = new Date();
    const nowMin = now.getHours() * 60 + now.getMinutes();
    if (startMin === endMin) return true;
    if (startMin < endMin) return nowMin >= startMin && nowMin < endMin;
    return nowMin >= startMin || nowMin < endMin;
}

export function useRealtimeEvents(enabled = true) {
    const queryClient = useQueryClient();
    const esRef = useRef<EventSource | null>(null);

    useEffect(() => {
        if (!enabled) {
            if (esRef.current) {
                esRef.current.close();
                esRef.current = null;
            }
            return;
        }

        // Only one connection per component life
        if (esRef.current) return;

        const url = getApiUrl('/api/events/stream');
        const es = new EventSource(url, { withCredentials: true });
        esRef.current = es;

        // intel_ready: AI finished analyzing a thread → refresh thread list for updated summary/intent
        es.addEventListener('intel_ready', (e) => {
            try {
                const data = JSON.parse(e.data);
                console.log('[SSE] intel_ready:', data.thread_id, data.intent, `score=${data.urgency_score}`);
                // Invalidate threads so updated summary/intent shows in inbox
                queryClient.invalidateQueries({ queryKey: ['threads'] });
                queryClient.invalidateQueries({ queryKey: ['dashboard'] });
                queryClient.invalidateQueries({ queryKey: ['nav-counts'] });
                // Also invalidate the specific thread detail if cached
                if (data.thread_id) {
                    queryClient.invalidateQueries({ queryKey: ['thread', data.thread_id] });
                }
            } catch { /* ignore parse errors */ }
        });

        // new_emails: incremental sync found new threads
        es.addEventListener('new_emails', (e) => {
            try {
                const data = JSON.parse(e.data);
                console.log('[SSE] new_emails:', data.count);
                queryClient.invalidateQueries({ queryKey: ['threads'] });
                queryClient.invalidateQueries({ queryKey: ['dashboard'] });
                queryClient.invalidateQueries({ queryKey: ['nav-counts'] });
            } catch { /* ignore */ }
        });

        // sync_status: sync started/ended
        es.addEventListener('sync_status', () => {
            queryClient.invalidateQueries({ queryKey: ['syncStatus'] });
        });

        // notification_new: backend synthesized or emitted new notifications
        es.addEventListener('notification_new', (e) => {
            try {
                const data = JSON.parse(e.data || '{}');
                queryClient.invalidateQueries({ queryKey: ['notifications'] });
                queryClient.invalidateQueries({ queryKey: ['notifications-unread-count'] });
                queryClient.invalidateQueries({ queryKey: ['notification-preferences'] });
                queryClient.invalidateQueries({ queryKey: ['notification-prefs'] });

                const prefs =
                    (queryClient.getQueryData(['notification-prefs']) as NotificationPrefs | undefined) ||
                    (queryClient.getQueryData(['notification-preferences']) as NotificationPrefs | undefined);
                const canPush = (prefs?.push_enabled ?? false) && !inQuietHours(prefs?.quiet_hours_start, prefs?.quiet_hours_end);

                if (canPush && typeof window !== 'undefined' && 'Notification' in window && Notification.permission === 'granted') {
                    const count = data?.count ?? 1;
                    new Notification('SortMail notifications', {
                        body: `${count} new notification${count > 1 ? 's' : ''} available.`,
                    });
                }
            } catch {
                queryClient.invalidateQueries({ queryKey: ['notifications'] });
                queryClient.invalidateQueries({ queryKey: ['notifications-unread-count'] });
            }
        });

        // notification_updated: read/dismiss actions from this or other sessions
        es.addEventListener('notification_updated', () => {
            queryClient.invalidateQueries({ queryKey: ['notifications'] });
            queryClient.invalidateQueries({ queryKey: ['notifications-unread-count'] });
            queryClient.invalidateQueries({ queryKey: ['nav-counts'] });
        });

        es.onerror = () => {
            // EventSource auto-reconnects — no need to handle manually
        };

        return () => {
            es.close();
            esRef.current = null;
        };
    }, [enabled, queryClient]);
}
