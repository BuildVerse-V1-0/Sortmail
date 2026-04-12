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

import { useEffect, useRef, useState, useCallback } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { api, endpoints } from '@/lib/api';

export type SyncState = 'idle' | 'checking' | 'syncing' | 'done' | 'error' | 'no_account';

export function useSmartSync() {
    const queryClient = useQueryClient();
    const [syncState, setSyncState] = useState<SyncState>('idle');
    const [lastSyncAt, setLastSyncAt] = useState<string | null>(null);
    const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);
    const hasRun = useRef(false);

    const stopPolling = useCallback(() => {
        if (pollRef.current) {
            clearInterval(pollRef.current);
            pollRef.current = null;
        }
    }, []);

    const refreshInboxQueries = useCallback(async () => {
        await Promise.all([
            queryClient.invalidateQueries({ queryKey: ['threads'] }),
            queryClient.invalidateQueries({ queryKey: ['nav-counts'] }),
            queryClient.invalidateQueries({ queryKey: ['dashboard'] }),
            queryClient.refetchQueries({ queryKey: ['threads'], type: 'active' }),
        ]);
    }, [queryClient]);

    const triggerSync = useCallback(async () => {
        try {
            setSyncState('syncing');
            await api.post(endpoints.emailSync);

            // Poll sync/status until backend reports real completion.
            // Avoid early "done" when background task has not yet flipped to SYNCING.
            let attempts = 0;
            const syncStartedAt = Date.now();
            const maxWaitMs = 5 * 60 * 1000;
            const baselineLastSyncAt = lastSyncAt;
            let sawSyncing = false;

            pollRef.current = setInterval(async () => {
                attempts++;
                try {
                    const { data } = await api.get(endpoints.emailSyncStatus);
                    setLastSyncAt(data.last_sync_at);
                    const remoteStatus = String(data.status || '').toUpperCase();

                    if (remoteStatus === 'SYNCING') {
                        sawSyncing = true;
                        return;
                    }

                    if (remoteStatus === 'FAILED') {
                        stopPolling();
                        setSyncState('error');
                        return;
                    }

                    const timedOut = Date.now() - syncStartedAt > maxWaitMs;
                    const lastSyncChanged = Boolean(data.last_sync_at && data.last_sync_at !== baselineLastSyncAt);

                    if (remoteStatus === 'IDLE' && (sawSyncing || lastSyncChanged || timedOut)) {
                        stopPolling();
                        setSyncState('done');
                        await refreshInboxQueries();
                        return;
                    }

                    if (timedOut || attempts > 150) {
                        stopPolling();
                        // Fail safe: refresh anyway so UI catches any completed writes.
                        await refreshInboxQueries();
                        setSyncState('done');
                    }
                } catch {
                    stopPolling();
                    setSyncState('error');
                }
            }, 3000);
        } catch {
            setSyncState('error');
        }
    }, [stopPolling, refreshInboxQueries, lastSyncAt]);

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
                const remoteStatus = String(data.status || '').toUpperCase();

                if (data.needs_sync || remoteStatus === 'FAILED') {
                    await triggerSync();
                } else {
                    setSyncState('idle');
                }
            } catch {
                setSyncState('error');
            }
        })();

        return () => stopPolling();
    }, [triggerSync, stopPolling]);

    return { syncState, lastSyncAt, triggerSync };
}
