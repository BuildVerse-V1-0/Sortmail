"use client";

import React, { useState } from "react";
import { Search, Mail, TrendingUp, Clock, User } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";
import AppShell from "@/components/layout/AppShell";

interface Contact {
    email: string;
    name: string;
    totalEmails: number;
    lastContact: string;
    avgResponseTime: string;
}

const mockContacts: Contact[] = [
    {
        email: "sarah.chen@techcorp.com",
        name: "Sarah Chen",
        totalEmails: 47,
        lastContact: "2026-02-16",
        avgResponseTime: "2h",
    },
    {
        email: "mike.johnson@startup.io",
        name: "Mike Johnson",
        totalEmails: 32,
        lastContact: "2026-02-15",
        avgResponseTime: "4h",
    },
    {
        email: "emma.wilson@agency.com",
        name: "Emma Wilson",
        totalEmails: 28,
        lastContact: "2026-02-14",
        avgResponseTime: "1h",
    },
    {
        email: "david.lee@consulting.com",
        name: "David Lee",
        totalEmails: 19,
        lastContact: "2026-02-13",
        avgResponseTime: "6h",
    },
    {
        email: "lisa.martinez@corp.com",
        name: "Lisa Martinez",
        totalEmails: 15,
        lastContact: "2026-02-12",
        avgResponseTime: "3h",
    },
];

type SortOption = "most_emails" | "recent" | "alphabetical";

export default function ContactsPage() {
    const [searchQuery, setSearchQuery] = useState("");
    const [sortBy, setSortBy] = useState<SortOption>("most_emails");
    const [contacts, setContacts] = useState(mockContacts);

    const handleSearch = (query: string) => {
        setSearchQuery(query);
        if (query.trim()) {
            const filtered = mockContacts.filter(
                (contact) =>
                    contact.name.toLowerCase().includes(query.toLowerCase()) ||
                    contact.email.toLowerCase().includes(query.toLowerCase())
            );
            setContacts(filtered);
        } else {
            setContacts(mockContacts);
        }
    };

    const handleSort = (option: SortOption) => {
        setSortBy(option);
        const sorted = [...contacts].sort((a, b) => {
            switch (option) {
                case "most_emails":
                    return b.totalEmails - a.totalEmails;
                case "recent":
                    return new Date(b.lastContact).getTime() - new Date(a.lastContact).getTime();
                case "alphabetical":
                    return a.name.localeCompare(b.name);
                default:
                    return 0;
            }
        });
        setContacts(sorted);
    };

    const getInitials = (name: string) => {
        return name
            .split(" ")
            .map((n) => n[0])
            .join("")
            .toUpperCase();
    };

    return (
        <AppShell title="Contacts">
            <div className="flex flex-col h-full bg-paper">
                {/* Header */}
                <div className="border-b border-border bg-white px-8 py-6">
                    <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-3">
                            <User className="w-6 h-6 text-muted" />
                            <h1 className="font-display text-2xl text-ink">Contacts</h1>
                            <Badge variant="secondary" className="text-xs">
                                {contacts.length}
                            </Badge>
                        </div>
                    </div>

                    {/* Search & Sort */}
                    <div className="flex items-center gap-4">
                        <div className="relative flex-1 max-w-md">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
                            <Input
                                type="text"
                                placeholder="Search contacts..."
                                value={searchQuery}
                                onChange={(e) => handleSearch(e.target.value)}
                                className="pl-10 h-10"
                            />
                        </div>
                        <div className="flex items-center gap-2">
                            <span className="text-xs text-muted font-mono uppercase tracking-wide">
                                Sort:
                            </span>
                            {[
                                { id: "most_emails", label: "Most Emails" },
                                { id: "recent", label: "Recent" },
                                { id: "alphabetical", label: "A-Z" },
                            ].map((option) => (
                                <button
                                    key={option.id}
                                    onClick={() => handleSort(option.id as SortOption)}
                                    className={`
                                        px-3 py-1.5 rounded-md text-xs font-medium transition-colors
                                        ${sortBy === option.id
                                            ? "bg-accent text-white"
                                            : "bg-white border border-border text-ink hover:bg-paper"
                                        }
                                    `}
                                >
                                    {option.label}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Contacts List */}
                <div className="flex-1 overflow-y-auto px-8 py-6">
                    {contacts.length === 0 ? (
                        <div className="flex flex-col items-center justify-center h-full text-center">
                            <User className="w-16 h-16 text-muted mb-4" />
                            <h2 className="font-display text-xl text-ink mb-2">
                                No contacts found
                            </h2>
                            <p className="text-muted max-w-md">
                                Try adjusting your search query.
                            </p>
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-w-6xl">
                            {contacts.map((contact) => (
                                <Link key={contact.email} href={`/contacts/${encodeURIComponent(contact.email)}`}>
                                    <Card className="p-4 hover:shadow-md transition-shadow cursor-pointer h-full">
                                        <div className="flex items-start gap-3">
                                            <Avatar className="w-12 h-12 shrink-0">
                                                <AvatarFallback className="bg-accent text-white font-medium">
                                                    {getInitials(contact.name)}
                                                </AvatarFallback>
                                            </Avatar>
                                            <div className="flex-1 min-w-0">
                                                <h3 className="font-medium text-ink truncate mb-0.5">
                                                    {contact.name}
                                                </h3>
                                                <p className="text-xs text-muted truncate mb-3">
                                                    {contact.email}
                                                </p>
                                                <div className="space-y-1.5">
                                                    <div className="flex items-center gap-2 text-xs">
                                                        <Mail className="w-3 h-3 text-muted" />
                                                        <span className="text-ink font-medium">
                                                            {contact.totalEmails}
                                                        </span>
                                                        <span className="text-muted">emails</span>
                                                    </div>
                                                    <div className="flex items-center gap-2 text-xs">
                                                        <Clock className="w-3 h-3 text-muted" />
                                                        <span className="text-muted">
                                                            Avg response: {contact.avgResponseTime}
                                                        </span>
                                                    </div>
                                                    <div className="flex items-center gap-2 text-xs">
                                                        <TrendingUp className="w-3 h-3 text-muted" />
                                                        <span className="text-muted">
                                                            Last: {new Date(contact.lastContact).toLocaleDateString()}
                                                        </span>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </Card>
                                </Link>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </AppShell>
    );
}
