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

const RAW = process.env.NEXT_PUBLIC_API_URL || 'https://sortmail-production.up.railway.app';
const API_BASE = RAW.replace(/^http:\/\/(?!localhost)/, 'https://');

export function useRealtimeEvents() {
    const queryClient = useQueryClient();
    const esRef = useRef<EventSource | null>(null);

    useEffect(() => {
        // Only one connection per component life
        if (esRef.current) return;

        const url = `${API_BASE}/api/events/stream`;
        const es = new EventSource(url, { withCredentials: true });
        esRef.current = es;

        // intel_ready: AI finished analyzing a thread → refresh thread list for updated summary/intent
        es.addEventListener('intel_ready', (e) => {
            try {
                const data = JSON.parse(e.data);
                console.log('[SSE] intel_ready:', data.thread_id, data.intent, `score=${data.urgency_score}`);
                // Invalidate threads so updated summary/intent shows in inbox
                queryClient.invalidateQueries({ queryKey: ['threads'] });
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
            } catch { /* ignore */ }
        });

        // sync_status: sync started/ended
        es.addEventListener('sync_status', () => {
            queryClient.invalidateQueries({ queryKey: ['syncStatus'] });
        });

        es.onerror = () => {
            // EventSource auto-reconnects — no need to handle manually
        };

        return () => {
            es.close();
            esRef.current = null;
        };
    }, [queryClient]);
}
