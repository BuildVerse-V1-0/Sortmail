import React from 'react';
import { Search, Filter, X } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select';

interface TaskFiltersProps {
    searchQuery: string;
    onSearchChange: (query: string) => void;
    priorityFilter: string;
    onPriorityChange: (value: string) => void;
    statusFilter: string;
    onStatusChange: (value: string) => void;
    onClearFilters: () => void;
}

export function TaskFilters({
    searchQuery,
    onSearchChange,
    priorityFilter,
    onPriorityChange,
    statusFilter,
    onStatusChange,
    onClearFilters
}: TaskFiltersProps) {
    const hasActiveFilters = searchQuery || priorityFilter !== 'all' || statusFilter !== 'all';

    return (
        <div className="flex flex-col md:flex-row gap-4 items-center justify-between py-4">
            <div className="relative w-full md:w-96">
                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                    placeholder="Search tasks..."
                    value={searchQuery}
                    onChange={(e) => onSearchChange(e.target.value)}
                    className="pl-9 bg-surface-card"
                />
            </div>

            <div className="flex items-center gap-2 w-full md:w-auto overflow-x-auto pb-2 md:pb-0">
                <Select value={priorityFilter} onValueChange={onPriorityChange}>
                    <SelectTrigger className="w-[140px] bg-surface-card">
                        <div className="flex items-center gap-2">
                            <Filter className="h-3.5 w-3.5 text-muted-foreground" />
                            <SelectValue placeholder="Priority" />
                        </div>
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="all">All Priorities</SelectItem>
                        <SelectItem value="do_now">Do Now</SelectItem>
                        <SelectItem value="do_today">Do Today</SelectItem>
                        <SelectItem value="can_wait">Can Wait</SelectItem>
                    </SelectContent>
                </Select>

                <Select value={statusFilter} onValueChange={onStatusChange}>
                    <SelectTrigger className="w-[140px] bg-surface-card">
                        <SelectValue placeholder="Status" />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="all">All Statuses</SelectItem>
                        <SelectItem value="pending">Todo</SelectItem>
                        <SelectItem value="in_progress">In Progress</SelectItem>
                        <SelectItem value="completed">Done</SelectItem>
                    </SelectContent>
                </Select>

                {hasActiveFilters && (
                    <Button
                        variant="ghost"
                        size="sm"
                        onClick={onClearFilters}
                        className="text-muted-foreground hover:text-ink"
                    >
                        <X className="h-4 w-4 mr-1" />
                        Clear
                    </Button>
                )}
            </div>
        </div>
    );
}
