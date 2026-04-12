'use client';

import React, { useState, useEffect, Suspense, useRef, useCallback } from 'react';
import Link from 'next/link';
import { useQueryClient } from '@tanstack/react-query';
import AppShell from '@/components/layout/AppShell';
import { api, endpoints } from '@/lib/api';
import { useThreads } from '@/hooks/useThreads';
import { useSmartSync } from '@/hooks/useSmartSync';
import { useRealtimeEvents } from '@/hooks/useRealtimeEvents';
import { useSearchParams } from 'next/navigation';
import { ThreadListItem } from '@/types/dashboard';

const MaterialSymbol = ({ icon, filled = false, className = "" }: { icon: string; filled?: boolean; className?: string }) => (
    <span 
        className={`material-symbols-outlined ${className}`}
        style={{ fontVariationSettings: `'FILL' ${filled ? 1 : 0}` }}
    >
        {icon}
    </span>
);

const INITIAL_LIMIT = 15;
const PAGE_SIZE = 5;

function findScrollParent(start: HTMLElement | null): HTMLElement | null {
    if (!start || typeof window === 'undefined') return null;
    let current: HTMLElement | null = start.parentElement;

    while (current) {
        const style = window.getComputedStyle(current);
        const overflow = `${style.overflow} ${style.overflowY} ${style.overflowX}`;
        if (/(auto|scroll|overlay)/i.test(overflow)) {
            return current;
        }
        current = current.parentElement;
    }

    return null;
}

function InboxContent() {
    const searchParams = useSearchParams();
    const [search, setSearch] = useState('');
    const [debouncedSearch, setDebouncedSearch] = useState('');
    const [busyThreadId, setBusyThreadId] = useState<string | null>(null);
    const [allThreads, setAllThreads] = useState<ThreadListItem[]>([]);
    const [currentOffset, setCurrentOffset] = useState(0);
    const [isLoadingMore, setIsLoadingMore] = useState(false);
    const [hasMore, setHasMore] = useState(true);
    const [prevSearch, setPrevSearch] = useState('');
    const [scrollDebugEnabled, setScrollDebugEnabled] = useState(false);
    const [scrollDebug, setScrollDebug] = useState({
        scrollTop: 0,
        clientHeight: 0,
        scrollHeight: 0,
        nearBottom: false,
        hasMore: true,
        isLoading: false,
        isLoadingMore: false,
        currentLimit: INITIAL_LIMIT,
        loadedThreads: 0,
    });
    const sentinelRef = useRef<HTMLDivElement>(null);
    const scrollContainerRef = useRef<HTMLDivElement>(null);
    const [scrollRoot, setScrollRoot] = useState<HTMLElement | null>(null);
    const queryClient = useQueryClient();
    const intentFilter = searchParams.get('intent') || undefined;
    const initialSearch = searchParams.get('q') || '';
    
    useEffect(() => {
        setSearch(initialSearch);
        setDebouncedSearch(initialSearch);
    }, [initialSearch]);

    useEffect(() => {
        const t = setTimeout(() => setDebouncedSearch(search), 400);
        return () => clearTimeout(t);
    }, [search]);

    useEffect(() => {
        if (typeof window === 'undefined') return;
        const params = new URLSearchParams(window.location.search);
        const enabled = params.get('scrollDebug') === '1';
        setScrollDebugEnabled(enabled);
    }, []);

    // Use true offset paging: first fetch is larger, then load fixed-size pages.
    const currentLimit = currentOffset === 0 ? INITIAL_LIMIT : PAGE_SIZE;
    const { data: threads, isLoading, error } = useThreads(intentFilter, debouncedSearch || undefined, currentOffset, currentLimit);
    
    const { syncState, triggerSync } = useSmartSync();
    useRealtimeEvents();

    const isSyncing = syncState === 'syncing' || syncState === 'checking';

    useEffect(() => {
        if (syncState !== 'done') return;
        // Re-anchor listing to first page so newly synced top threads render immediately.
        setCurrentOffset(0);
        setAllThreads([]);
        setHasMore(true);
        setIsLoadingMore(false);
    }, [syncState]);

    // Reset pagination when search changes
    useEffect(() => {
        if (debouncedSearch !== prevSearch) {
            setCurrentOffset(0);
            setAllThreads([]);
            setHasMore(true);
            setIsLoadingMore(false);
            setPrevSearch(debouncedSearch);
        }
    }, [debouncedSearch, prevSearch]);

    // Update allThreads when initial data loads or updates
    useEffect(() => {
        if (!threads) return;
        if (currentOffset === 0) {
            setAllThreads(threads);
        } else {
            setAllThreads((prev) => {
                const seen = new Set(prev.map((t) => t.thread_id));
                const next = threads.filter((t) => !seen.has(t.thread_id));
                return next.length ? [...prev, ...next] : prev;
            });
        }

        // If backend returns fewer than requested page size, there are no more rows.
        if (threads.length < currentLimit) {
            setHasMore(false);
        } else {
            setHasMore(true);
        }
        setIsLoadingMore(false);
    }, [threads, currentLimit, currentOffset]);

    const requestNextPage = useCallback(() => {
        if (!hasMore || isLoading || isLoadingMore) return;
        setIsLoadingMore(true);
        setCurrentOffset((prev) => prev + (prev === 0 ? INITIAL_LIMIT : PAGE_SIZE));
    }, [hasMore, isLoading, isLoadingMore]);

    const evaluateScroll = useCallback((el: HTMLElement) => {
        const remaining = el.scrollHeight - el.scrollTop - el.clientHeight;
        const nearBottom = remaining <= 180;

        if (scrollDebugEnabled) {
            setScrollDebug({
                scrollTop: Math.round(el.scrollTop),
                clientHeight: el.clientHeight,
                scrollHeight: el.scrollHeight,
                nearBottom,
                hasMore,
                isLoading,
                isLoadingMore,
                currentLimit,
                loadedThreads: allThreads.length,
            });
        }

        if (nearBottom) {
            requestNextPage();
        }
    }, [scrollDebugEnabled, hasMore, isLoading, isLoadingMore, currentLimit, allThreads.length, requestNextPage]);

    // Resolve the actual scrolling element (often AppShell's overflow container).
    useEffect(() => {
        const container = scrollContainerRef.current;
        if (!container) return;
        const parent = findScrollParent(container);
        setScrollRoot(parent ?? container);
    }, [allThreads.length]);

    // Listen on the true scroll root so near-bottom checks use real metrics.
    useEffect(() => {
        if (!scrollRoot) return;

        const onScroll = () => evaluateScroll(scrollRoot);

        scrollRoot.addEventListener('scroll', onScroll, { passive: true });
        onScroll();

        return () => {
            scrollRoot.removeEventListener('scroll', onScroll);
        };
    }, [scrollRoot, evaluateScroll]);

    // Intersection Observer for infinite scroll
    useEffect(() => {
        if (!sentinelRef.current) return;

        const observer = new IntersectionObserver(
            entries => {
                if (entries[0].isIntersecting && hasMore && !isLoading && !isLoadingMore) {
                    requestNextPage();
                }
            },
            {
                root: scrollRoot ?? null,
                rootMargin: '0px 0px 120px 0px',
                threshold: 0.1,
            }
        );

        observer.observe(sentinelRef.current);
        return () => observer.disconnect();
    }, [hasMore, isLoading, isLoadingMore, requestNextPage, scrollRoot]);

    const filtered = allThreads;

    const mutateThread = async (threadId: string, action: 'archive' | 'trash') => {
        setBusyThreadId(threadId);
        try {
            if (action === 'archive') {
                await api.post(endpoints.threadArchive(threadId));
            } else {
                await api.delete(endpoints.threadTrash(threadId));
            }

            await Promise.all([
                queryClient.invalidateQueries({ queryKey: ['threads'] }),
                queryClient.invalidateQueries({ queryKey: ['nav-counts'] }),
                queryClient.invalidateQueries({ queryKey: ['dashboard'] }),
            ]);
        } finally {
            setBusyThreadId((current) => (current === threadId ? null : current));
        }
    };

    return (
        <div className="flex flex-col h-full min-h-0 bg-surface-container-lowest">
            {/* Toolbar / Action Bar */}
            <div className="h-10 border-b border-outline-variant/10 flex items-center justify-between px-4 bg-white/50 backdrop-blur-sm sticky top-0 z-20">
                <div className="flex items-center gap-6">
                    <div className="flex items-center gap-3">
                        <input type="checkbox" className="w-4 h-4 rounded border-outline-variant text-primary focus:ring-primary cursor-pointer transition-all" />
                        <button className="p-1 hover:bg-surface-container rounded transition-colors">
                            <MaterialSymbol icon="arrow_drop_down" className="text-on-surface-variant" />
                        </button>
                    </div>
                    
                    <div className="h-6 w-[1px] bg-outline-variant/30" />
                    
                    <div className="flex items-center gap-1.5">
                        <button 
                            onClick={triggerSync} 
                            disabled={isSyncing}
                            className="p-2.5 hover:bg-primary-fixed/20 text-on-surface-variant hover:text-primary rounded-xl transition-all flex items-center gap-2 group"
                        >
                            <MaterialSymbol icon="sync" className={`text-xl ${isSyncing ? 'animate-spin text-primary' : 'group-hover:rotate-180 transition-transform duration-500'}`} />
                            <span className="text-xs font-bold uppercase tracking-wider hidden md:inline">Refresh</span>
                        </button>
                        
                        <button className="p-2.5 hover:bg-surface-container text-on-surface-variant rounded-xl transition-all flex items-center gap-2">
                            <MaterialSymbol icon="archive" className="text-xl" />
                            <span className="text-xs font-bold uppercase tracking-wider hidden md:inline">Archive</span>
                        </button>
                        
                        <button className="p-2.5 hover:bg-surface-container text-on-surface-variant rounded-xl transition-all flex items-center gap-2">
                            <MaterialSymbol icon="label" className="text-xl" />
                            <span className="text-xs font-bold uppercase tracking-wider hidden md:inline">Label</span>
                        </button>
                    </div>
                </div>

                <div className="flex items-center gap-4">
                    <div className="text-[10px] font-bold text-outline uppercase tracking-[0.15em]">
                        {filtered.length > 0 ? `1-${filtered.length}` : '0'} of {hasMore ? '...' : filtered.length}
                    </div>
                    <div className="flex gap-1">
                        <button className="p-2 hover:bg-surface-container rounded-lg text-outline disabled:opacity-20" disabled>
                            <MaterialSymbol icon="chevron_left" />
                        </button>
                        <button className="p-2 hover:bg-surface-container rounded-lg text-on-surface">
                            <MaterialSymbol icon="chevron_right" />
                        </button>
                    </div>
                </div>
            </div>

            {/* List Header (Column Labels) */}
            <div className="px-4 md:px-6 py-2 border-b border-outline-variant/5 bg-surface-container-lowest flex items-center gap-4 text-[10px] font-bold text-outline uppercase tracking-widest">
                <div className="w-12 shrink-0" />
                <div className="w-48 shrink-0">Sender</div>
                <div className="flex-1">Subject</div>
                <div className="w-52 shrink-0">AI Intelligence</div>
                <div className="w-24 text-right">Date</div>
            </div>

            {/* Thread List */}
            <div ref={scrollContainerRef} className="flex-1 min-h-0">
                {isLoading && filtered.length === 0 ? (
                    <div className="divide-y divide-outline-variant/5">
                        {[1, 2, 3, 4, 5, 6, 7].map((i) => (
                            <div key={i} className="p-4 flex items-center gap-4 animate-pulse">
                                <div className="w-12 h-4 bg-surface-container rounded" />
                                <div className="w-48 h-4 bg-surface-container rounded" />
                                <div className="flex-1 h-4 bg-surface-container rounded" />
                                <div className="w-24 h-4 bg-surface-container rounded" />
                            </div>
                        ))}
                    </div>
                ) : error ? (
                    <div className="p-12 text-center flex flex-col items-center gap-4">
                        <MaterialSymbol icon="error" className="text-error text-4xl" />
                        <p className="text-on-surface-variant font-bold">Failed to connect to Intelligence Layer.</p>
                        <button onClick={() => window.location.reload()} className="text-primary font-bold hover:underline">Retry</button>
                    </div>
                ) : filtered.length === 0 ? (
                    <div className="p-12 text-center flex flex-col items-center gap-5">
                        <div className="w-16 h-16 rounded-full bg-surface-container flex items-center justify-center text-outline">
                            <MaterialSymbol icon="inbox" className="text-4xl" />
                        </div>
                        <div className="space-y-1">
                            <p className="text-lg font-headline font-bold text-on-surface">Inbox at Peace</p>
                            <p className="text-sm text-on-surface-variant max-w-xs mx-auto">
                                All intelligence processed. Connect a new account or refresh to check for updates.
                            </p>
                        </div>
                        <button 
                            onClick={triggerSync}
                            className="px-6 py-3 bg-primary text-on-primary rounded-2xl font-bold flex items-center gap-2 shadow-lg shadow-primary/20 hover:scale-105 active:scale-95 transition-all"
                        >
                            <MaterialSymbol icon="sync" className={isSyncing ? 'animate-spin' : ''} />
                            Sync Now
                        </button>
                    </div>
                ) : (
                    <div className="divide-y divide-outline-variant/10">
                        {filtered.map((thread: ThreadListItem) => (
                            <ThreadRow
                                key={thread.thread_id}
                                thread={thread}
                                onArchive={(threadId) => mutateThread(threadId, 'archive')}
                                onTrash={(threadId) => mutateThread(threadId, 'trash')}
                                busy={busyThreadId === thread.thread_id}
                            />
                        ))}
                        
                        {/* Sentinel element for infinite scroll */}
                        <div ref={sentinelRef} className="h-20 flex items-center justify-center">
                            {isLoadingMore || (isLoading && filtered.length > 0) ? (
                                <div className="flex items-center gap-2 text-outline-variant">
                                    <MaterialSymbol icon="sync" className="animate-spin" />
                                    <span className="text-sm">Loading more...</span>
                                </div>
                            ) : hasMore ? (
                                <span className="text-xs text-outline-variant">Scroll for more</span>
                            ) : filtered.length > 0 ? (
                                <span className="text-xs text-outline-variant">No more messages</span>
                            ) : null}
                        </div>
                        {scrollDebugEnabled && (
                            <div className="px-4 pb-3 text-[11px] text-outline-variant font-mono">
                                scrollTop={scrollDebug.scrollTop} clientHeight={scrollDebug.clientHeight} scrollHeight={scrollDebug.scrollHeight} nearBottom={String(scrollDebug.nearBottom)} hasMore={String(scrollDebug.hasMore)} loading={String(scrollDebug.isLoading)} loadingMore={String(scrollDebug.isLoadingMore)} limit={scrollDebug.currentLimit} loaded={scrollDebug.loadedThreads}
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}

function ThreadRow({ thread, onArchive, onTrash, busy }: { thread: ThreadListItem; onArchive: (threadId: string) => void; onTrash: (threadId: string) => void; busy: boolean }) {
    const isUnread = (thread as any).is_unread ?? false;
    const isUrgent = thread.urgency_score >= 80;
    
    const participantName = thread.participants?.[0]?.split('<')[0]?.trim() || 'Internal';
    
    return (
        <div className={`group flex items-center gap-4 px-4 md:px-6 py-3.5 hover:bg-surface-container-low transition-all cursor-pointer relative ${isUnread ? 'bg-primary-fixed/5' : ''}`}>
            {/* Priority/Unread Indicator */}
            <div className="absolute left-0 top-0 bottom-0 w-[3px] bg-primary opacity-0 group-hover:opacity-100 transition-opacity" />
            
            {/* Selection & Actions */}
            <div className="flex items-center gap-3 shrink-0">
                <input type="checkbox" className="w-4 h-4 rounded border-outline-variant text-primary focus:ring-primary cursor-pointer" onClick={(e) => e.stopPropagation()} />
                <button className="text-outline hover:text-tertiary transition-colors" onClick={(e) => { e.stopPropagation(); e.preventDefault(); }}>
                    <MaterialSymbol icon="star" filled={isUrgent} className={isUrgent ? 'text-tertiary' : ''} />
                </button>
            </div>

            {/* Sender */}
            <div className={`w-48 shrink-0 truncate text-sm ${isUnread ? 'font-bold text-on-surface' : 'font-medium text-on-surface-variant'}`}>
                {participantName}
            </div>

            {/* Content & Intelligence */}
            <Link href={`/inbox/${thread.thread_id}`} className="flex-1 min-w-0 flex items-center gap-4">
                <div className="flex-1 min-w-0 flex flex-col gap-0.5">
                    <h3 className={`text-sm truncate ${isUnread ? 'font-bold text-on-surface' : 'font-medium text-on-surface-variant'}`}>
                        {thread.subject || '(No Subject)'}
                    </h3>
                    <div className="flex items-center gap-3 overflow-hidden">
                        <div className="px-2 py-0.5 bg-tertiary-fixed/30 text-tertiary font-bold text-[10px] rounded uppercase flex items-center gap-1 shrink-0">
                            <MaterialSymbol icon="psychology" filled className="text-[14px]" />
                            AI Summary
                        </div>
                        <p className="text-xs text-on-surface-variant/70 italic truncate">
                            {thread.summary || 'Analyzing thread context...'}
                        </p>
                    </div>
                </div>
            </Link>

            <div className="w-52 shrink-0 min-w-0 flex flex-col gap-1.5">
                <div className="flex items-center gap-2 flex-wrap">
                    <span className={`px-2 py-0.5 rounded-full text-[9px] font-black uppercase tracking-widest ${thread.urgency_score >= 80 ? 'bg-error-container text-error' : 'bg-primary-fixed/15 text-primary'}`}>
                        {thread.urgency_score >= 80 ? 'High signal' : 'Stable signal'}
                    </span>
                    <span className="text-[9px] font-black uppercase tracking-widest text-outline-variant">
                        {thread.intent || 'Unclassified'}
                    </span>
                </div>
                <p className="text-[10px] text-on-surface-variant italic truncate">
                    AI urgency score {thread.urgency_score}/100
                </p>
                <p className="text-[10px] font-medium text-outline-variant truncate">
                    {thread.has_attachments ? 'Attachment intelligence available' : 'No attachment context'}
                </p>
            </div>

            {/* Date/Time */}
            <div className="w-24 text-right shrink-0">
                <span className={`text-[11px] tabular-nums ${isUnread ? 'font-bold text-primary' : 'text-outline font-medium'}`}>
                    {formatTime(thread.last_updated)}
                </span>
            </div>

            {/* Inline Toggle Actions (Hover only) */}
            <div className="absolute right-6 top-1/2 -translate-y-1/2 flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-all scale-95 group-hover:scale-100">
                <div className="flex items-center gap-1 bg-white/90 backdrop-blur shadow-sm border border-outline-variant/10 rounded-xl p-1">
                    <button
                        disabled={busy}
                        onClick={(e) => { e.preventDefault(); e.stopPropagation(); onArchive(thread.thread_id); }}
                        className="p-1.5 hover:bg-surface-container rounded-lg text-outline hover:text-primary transition-colors disabled:opacity-50"
                    >
                        <MaterialSymbol icon="archive" className="text-lg" />
                    </button>
                    <button
                        disabled={busy}
                        onClick={(e) => { e.preventDefault(); e.stopPropagation(); onTrash(thread.thread_id); }}
                        className="p-1.5 hover:bg-surface-container rounded-lg text-outline hover:text-error transition-colors disabled:opacity-50"
                    >
                        <MaterialSymbol icon="delete" className="text-lg" />
                    </button>
                    <button className="p-1.5 hover:bg-surface-container rounded-lg text-outline hover:text-on-surface transition-colors" disabled={busy}>
                        <MaterialSymbol icon="mark_email_read" className="text-lg" />
                    </button>
                </div>
            </div>
        </div>
    );
}

function formatTime(isoDate: string): string {
    const normalized = isoDate.endsWith('Z') || isoDate.includes('+') ? isoDate : isoDate + 'Z';
    const date = new Date(normalized);
    const now = new Date();
    const isToday = date.toDateString() === now.toDateString();
    
    if (isToday) {
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
    return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
}

export default function InboxPage() {
    return (
        <AppShell title="Inbox Intelligence">
            <Suspense fallback={
                <div className="p-10 space-y-4 animate-pulse">
                    <div className="h-10 bg-surface-container rounded-full w-48" />
                    {[1, 2, 3, 4, 5, 6].map(i => (
                        <div key={i} className="h-16 bg-surface-container rounded-2xl w-full" />
                    ))}
                </div>
            }>
                <InboxContent />
            </Suspense>
        </AppShell>
    );
}
