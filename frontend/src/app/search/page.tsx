"use client";

import React, { useState } from "react";
import { Search as SearchIcon, X, Calendar, Paperclip, User, AlertCircle } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import Link from "next/link";
import { mockThreadListItems } from "@/data/mockData";
import type { ThreadListItem } from "@/types/dashboard";
import AppShell from "@/components/layout/AppShell";

const FILTER_OPTIONS = [
    { id: "has_attachments", label: "Has Attachments", icon: Paperclip },
    { id: "urgent", label: "Urgent", icon: AlertCircle },
    { id: "unread", label: "Unread", icon: User },
];

export default function SearchPage() {
    const [searchQuery, setSearchQuery] = useState("");
    const [activeFilters, setActiveFilters] = useState<string[]>([]);
    const [results, setResults] = useState<ThreadListItem[]>([]);

    const handleSearch = (query: string) => {
        setSearchQuery(query);
        if (query.trim()) {
            // Filter mock data based on search query
            const filtered = mockThreadListItems.filter(
                (thread) =>
                    thread.subject.toLowerCase().includes(query.toLowerCase()) ||
                    thread.summary.toLowerCase().includes(query.toLowerCase())
            );
            setResults(filtered);
        } else {
            setResults([]);
        }
    };

    const toggleFilter = (filterId: string) => {
        setActiveFilters((prev) =>
            prev.includes(filterId)
                ? prev.filter((f) => f !== filterId)
                : [...prev, filterId]
        );
    };

    const clearFilters = () => {
        setActiveFilters([]);
        setSearchQuery("");
        setResults([]);
    };

    const getIntentColor = (intent: string) => {
        switch (intent) {
            case "urgent":
                return "bg-tag-urgent text-white";
            case "action_required":
                return "bg-tag-high text-white";
            case "fyi":
                return "bg-tag-low text-white";
            default:
                return "bg-muted text-ink";
        }
    };

    return (
        <AppShell title="Search">
            <div className="flex flex-col h-full bg-paper">
                {/* Header */}
                <div className="border-b border-border bg-white px-8 py-6">
                    <div className="flex items-center gap-3 mb-4">
                        <SearchIcon className="w-6 h-6 text-muted" />
                        <h1 className="font-display text-2xl text-ink">Search</h1>
                    </div>

                    {/* Search Input */}
                    <div className="relative max-w-2xl">
                        <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
                        <Input
                            type="text"
                            placeholder="Search emails, tasks, contacts..."
                            value={searchQuery}
                            onChange={(e) => handleSearch(e.target.value)}
                            className="pl-10 pr-10 h-12 text-base"
                        />
                        {searchQuery && (
                            <button
                                onClick={() => handleSearch("")}
                                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted hover:text-ink"
                            >
                                <X className="w-4 h-4" />
                            </button>
                        )}
                    </div>

                    {/* Filters */}
                    <div className="flex items-center gap-2 mt-4">
                        <span className="text-xs text-muted font-mono uppercase tracking-wide">
                            Filters:
                        </span>
                        {FILTER_OPTIONS.map((filter) => {
                            const Icon = filter.icon;
                            const isActive = activeFilters.includes(filter.id);
                            return (
                                <button
                                    key={filter.id}
                                    onClick={() => toggleFilter(filter.id)}
                                    className={`
                                        flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-colors
                                        ${isActive
                                            ? "bg-accent text-white"
                                            : "bg-white border border-border text-ink hover:bg-paper"
                                        }
                                    `}
                                >
                                    <Icon className="w-3 h-3" />
                                    {filter.label}
                                </button>
                            );
                        })}
                        {(activeFilters.length > 0 || searchQuery) && (
                            <Button
                                variant="ghost"
                                size="sm"
                                onClick={clearFilters}
                                className="text-xs text-muted hover:text-ink"
                            >
                                Clear all
                            </Button>
                        )}
                    </div>
                </div>

                {/* Results */}
                <div className="flex-1 overflow-y-auto px-8 py-6">
                    {!searchQuery && results.length === 0 && (
                        <div className="flex flex-col items-center justify-center h-full text-center">
                            <SearchIcon className="w-16 h-16 text-muted mb-4" />
                            <h2 className="font-display text-xl text-ink mb-2">
                                Search your emails
                            </h2>
                            <p className="text-muted max-w-md">
                                Find emails, tasks, and contacts quickly. Use filters to narrow down results.
                            </p>
                        </div>
                    )}

                    {searchQuery && results.length === 0 && (
                        <div className="flex flex-col items-center justify-center h-full text-center">
                            <SearchIcon className="w-16 h-16 text-muted mb-4" />
                            <h2 className="font-display text-xl text-ink mb-2">
                                No results found
                            </h2>
                            <p className="text-muted max-w-md">
                                Try adjusting your search query or filters.
                            </p>
                        </div>
                    )}

                    {results.length > 0 && (
                        <div className="max-w-4xl">
                            <p className="text-xs text-muted font-mono uppercase tracking-wide mb-4">
                                {results.length} result{results.length !== 1 ? "s" : ""}
                            </p>
                            <div className="space-y-2">
                                {results.map((thread) => (
                                    <Link key={thread.thread_id} href={`/inbox/${thread.thread_id}`}>
                                        <Card className="p-4 hover:shadow-md transition-shadow cursor-pointer">
                                            <div className="flex items-start justify-between gap-4">
                                                <div className="flex-1 min-w-0">
                                                    <div className="flex items-center gap-2 mb-1">
                                                        <h3 className="font-medium text-ink truncate">
                                                            {thread.subject}
                                                        </h3>
                                                        {thread.has_attachments && (
                                                            <Paperclip className="w-3 h-3 text-muted shrink-0" />
                                                        )}
                                                    </div>
                                                    <p className="text-sm text-muted line-clamp-2 mb-2">
                                                        {thread.summary}
                                                    </p>
                                                    <div className="flex items-center gap-2">
                                                        <Badge
                                                            variant="secondary"
                                                            className={`text-xs ${getIntentColor(thread.intent)}`}
                                                        >
                                                            {thread.intent.replace("_", " ")}
                                                        </Badge>
                                                        <span className="text-xs text-muted">
                                                            {new Date(thread.last_updated).toLocaleDateString()}
                                                        </span>
                                                    </div>
                                                </div>
                                            </div>
                                        </Card>
                                    </Link>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </AppShell>
    );
}
