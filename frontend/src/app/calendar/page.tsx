'use client';

import React, { useState } from 'react';
import AppShell from '@/components/layout/AppShell';
import { mockCalendarSuggestions } from '@/data/mockData';
import { CalendarSuggestionV1 } from '@/types/dashboard';
import { Calendar } from '@/components/ui/calendar';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Calendar as CalendarIcon, Clock, MapPin, Check, X, ExternalLink, ArrowRight } from 'lucide-react';
import { format } from 'date-fns';
import Image from 'next/image';

export default function CalendarPage() {
    const [date, setDate] = useState<Date | undefined>(new Date());
    const [suggestions, setSuggestions] = useState<CalendarSuggestionV1[]>(mockCalendarSuggestions);

    // Get days with suggestions for the calendar highlights
    const suggestionDates = suggestions.map(s => new Date(s.suggested_time));

    const handleDismiss = (id: string) => {
        setSuggestions(prev => prev.filter(s => s.suggestion_id !== id));
    };

    const handleAccept = (id: string) => {
        // Logic to add to real calendar would go here
        console.log('Accepted suggestion:', id);
        handleDismiss(id); // Remove from suggestions list for now
    };

    return (
        <AppShell title="Calendar Suggestions">
            <div className="flex flex-col h-full overflow-hidden">
                <div className="px-8 py-6 border-b border-border-light bg-surface-card/30">
                    <h1 className="font-display text-3xl text-ink">Calendar Suggestions</h1>
                    <p className="text-ink-light mt-1">AI detected events from your emails.</p>
                </div>

                <div className="flex flex-col lg:flex-row h-full overflow-hidden">
                    {/* Left Panel: Suggestions List */}
                    <div className="flex-1 overflow-y-auto p-8 space-y-6 scrollbar-thin">
                        {suggestions.length > 0 ? (
                            suggestions.map((suggestion) => (
                                <Card key={suggestion.suggestion_id} className="hover:shadow-md transition-shadow group border-l-4 border-l-ai">
                                    <CardContent className="p-5">
                                        <div className="flex justify-between items-start mb-2">
                                            <Badge variant="secondary" className="bg-ai-soft text-ai-purple hover:bg-ai-soft/80">
                                                {suggestion.confidence * 100}% Confidence
                                            </Badge>
                                            <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                                <Button size="sm" variant="ghost" onClick={() => handleDismiss(suggestion.suggestion_id)}>
                                                    <X className="h-4 w-4 text-muted-foreground hover:text-ink" />
                                                </Button>
                                            </div>
                                        </div>

                                        <h3 className="text-lg font-medium text-ink mb-1">{suggestion.title}</h3>

                                        <div className="space-y-2 mb-4">
                                            <div className="flex items-center gap-2 text-sm text-ink-light">
                                                <CalendarIcon className="h-4 w-4 text-muted-foreground" />
                                                {format(new Date(suggestion.suggested_time), 'EEEE, MMMM d, yyyy')}
                                            </div>
                                            <div className="flex items-center gap-2 text-sm text-ink-light">
                                                <Clock className="h-4 w-4 text-muted-foreground" />
                                                {format(new Date(suggestion.suggested_time), 'h:mm a')} • {suggestion.duration_minutes} min
                                            </div>
                                            {suggestion.location && (
                                                <div className="flex items-center gap-2 text-sm text-ink-light">
                                                    <MapPin className="h-4 w-4 text-muted-foreground" />
                                                    {suggestion.location}
                                                </div>
                                            )}
                                        </div>

                                        <div className="bg-paper-mid rounded-lg p-3 text-xs text-muted-foreground mb-4">
                                            Extracted from: <span className="italic">&quot;{suggestion.extracted_from}&quot;</span>
                                        </div>

                                        <div className="flex gap-3">
                                            <Button className="flex-1 gap-2 bg-ai hover:bg-ai/90 text-white" onClick={() => handleAccept(suggestion.suggestion_id)}>
                                                <Check className="h-4 w-4" />
                                                Add to Calendar
                                            </Button>
                                            <Button variant="outline" className="flex-1 gap-2">
                                                <ExternalLink className="h-4 w-4" />
                                                View Email
                                            </Button>
                                        </div>
                                    </CardContent>
                                </Card>
                            ))
                        ) : (
                            <div className="text-center py-12 border-2 border-dashed border-border-light rounded-xl bg-paper-mid/30">
                                <p className="text-muted-foreground">No pending suggestions.</p>
                            </div>
                        )}
                    </div>

                    {/* Right Panel: Calendar */}
                    <div className="lg:w-[400px] border-l border-border-light bg-surface-card p-6 overflow-y-auto">
                        <div className="mb-6">
                            <Calendar
                                mode="single"
                                selected={date}
                                onSelect={setDate}
                                className="rounded-md border shadow-sm bg-paper mx-auto"
                                modifiers={{
                                    suggestion: suggestionDates
                                }}
                                modifiersStyles={{
                                    suggestion: {
                                        fontWeight: 'bold',
                                        textDecoration: 'underline',
                                        color: 'var(--ai-purple)'
                                    }
                                }}
                            />
                        </div>

                        <div className="space-y-4">
                            <h3 className="font-medium text-ink">External Calendars</h3>
                            <Button variant="outline" className="w-full justify-start gap-2 h-12">
                                <Image
                                    src="https://upload.wikimedia.org/wikipedia/commons/a/a5/Google_Calendar_icon_%282020%29.svg"
                                    className="h-5 w-5 py-0.5"
                                    alt="Google"
                                    width={20}
                                    height={20}
                                    unoptimized
                                />
                                Open Google Calendar
                                <ArrowRight className="h-4 w-4 ml-auto text-muted-foreground" />
                            </Button>
                            <Button variant="outline" className="w-full justify-start gap-2 h-12">
                                <Image
                                    src="https://upload.wikimedia.org/wikipedia/commons/d/df/Microsoft_Office_Outlook_%282018%E2%80%93present%29.svg"
                                    className="h-5 w-5 py-0.5"
                                    alt="Outlook"
                                    width={20}
                                    height={20}
                                    unoptimized
                                />
                                Open Outlook Calendar
                                <ArrowRight className="h-4 w-4 ml-auto text-muted-foreground" />
                            </Button>
                        </div>
                    </div>
                </div>
            </div>
        </AppShell>
    );
}
