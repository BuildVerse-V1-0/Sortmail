/**
 * useSmartSync — DB-first inbox sync strategy
 *
 * Flow:
 *  1. Load threads from DB via React Query (instant — no Gmail call)
 *  2. Fetch /emails/sync/status — checks last_sync_at from ConnectedAccount
 *  3. If needs_sync=true (stale > 5 min or never synced) → POST /emails/sync (background, non-blocking)
 *  4. Poll sync-status until done → invalidate thread cache → UI refreshes
 *
 * This means:
 *  - UI shows emails instantly from DB
 *  - New emails appear silently in the background
 *  - No hammering Gmail API on every page load
 */

import { useEffect, useRef, useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { api, endpoints } from '@/lib/api';

export type SyncState = 'idle' | 'checking' | 'syncing' | 'done' | 'error' | 'no_account';

export function useSmartSync() {
    const queryClient = useQueryClient();
    const [syncState, setSyncState] = useState<SyncState>('idle');
    const [lastSyncAt, setLastSyncAt] = useState<string | null>(null);
    const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);
    const hasRun = useRef(false);

    const stopPolling = () => {
        if (pollRef.current) {
            clearInterval(pollRef.current);
            pollRef.current = null;
        }
    };

    const invalidateThreads = () => {
        queryClient.invalidateQueries({ queryKey: ['threads'] });
    };

    const triggerSync = async () => {
        try {
            setSyncState('syncing');
            await api.post(endpoints.emailSync);

            // Poll sync/status every 3s until status is idle/failed
            let attempts = 0;
            pollRef.current = setInterval(async () => {
                attempts++;
                try {
                    const { data } = await api.get(endpoints.emailSyncStatus);
                    setLastSyncAt(data.last_sync_at);
                    if (data.status === 'idle' || data.status === 'failed' || attempts > 20) {
                        stopPolling();
                        setSyncState(data.status === 'failed' ? 'error' : 'done');
                        invalidateThreads(); // Refresh threads from DB with new emails
                    }
                } catch {
                    stopPolling();
                    setSyncState('error');
                }
            }, 3000);
        } catch {
            setSyncState('error');
        }
    };

    useEffect(() => {
        if (hasRun.current) return;
        hasRun.current = true;

        (async () => {
            try {
                setSyncState('checking');
                const { data } = await api.get(endpoints.emailSyncStatus);

                if (!data.has_account) {
                    setSyncState('no_account');
                    return;
                }

                setLastSyncAt(data.last_sync_at);

                if (data.needs_sync) {
                    await triggerSync();
                } else {
                    setSyncState('idle');
                }
            } catch {
                setSyncState('error');
            }
        })();

        return () => stopPolling();
    }, []);

    return { syncState, lastSyncAt, triggerSync };
}
