'use client';

import React, { useState, useMemo } from 'react';
import AppShell from '@/components/layout/AppShell';
import { TaskFilters } from '@/components/tasks/TaskFilters';
import { TaskKanban } from '@/components/tasks/TaskKanban';
import { TaskList } from '@/components/tasks/TaskList';
import { useTasks } from '@/hooks/useTasks';
import { Button } from '@/components/ui/button';
import { LayoutGrid, List as ListIcon, Plus } from 'lucide-react';
import { TaskDTOv1 } from '@/types/dashboard';

export default function TasksPage() {
    const [view, setView] = useState<'board' | 'list'>('board');
    const [searchQuery, setSearchQuery] = useState('');
    const [priorityFilter, setPriorityFilter] = useState('all');
    const [statusFilter, setStatusFilter] = useState('all');

    const { data: tasks, isLoading, error } = useTasks();

    const filteredTasks = useMemo(() => {
        if (!tasks) return [];
        return tasks.filter((task: TaskDTOv1) => {
            const matchesSearch = task.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                (task.description?.toLowerCase().includes(searchQuery.toLowerCase()) ?? false);
            const matchesPriority = priorityFilter === 'all' || task.priority === priorityFilter;
            const matchesStatus = statusFilter === 'all' || task.status === statusFilter;
            return matchesSearch && matchesPriority && matchesStatus;
        });
    }, [searchQuery, priorityFilter, statusFilter, tasks]);

    const handleClearFilters = () => {
        setSearchQuery('');
        setPriorityFilter('all');
        setStatusFilter('all');
    };

    const handleTaskClick = (taskId: string) => {
        console.log('Task clicked:', taskId);
        // TODO: Open task detail modal
    };

    if (isLoading) {
        return (
            <AppShell title="Tasks">
                <div className="flex flex-col h-[calc(100vh-64px)] overflow-hidden">
                    <div className="p-6">
                        <div className="h-12 w-64 bg-paper-mid animate-pulse rounded-lg mb-6" />
                        <div className="flex gap-4">
                            {[1, 2, 3].map(i => (
                                <div key={i} className="flex-1 h-96 bg-paper-mid animate-pulse rounded-xl" />
                            ))}
                        </div>
                    </div>
                </div>
            </AppShell>
        );
    }

    if (error) {
        return (
            <AppShell title="Tasks">
                <div className="p-8 text-center text-danger">
                    Failed to load tasks.
                </div>
            </AppShell>
        );
    }

    return (
        <AppShell title="Tasks">
            <div className="flex flex-col h-[calc(100vh-64px)] overflow-hidden">
                <div className="flex flex-col gap-4 px-6 pt-6 pb-2 shrink-0">
                    <div className="flex items-center justify-between">
                        <div>
                            <h1 className="font-display text-3xl text-ink">Tasks</h1>
                            <p className="text-ink-light mt-1">Manage your actionable items from emails.</p>
                        </div>
                        <div className="flex items-center gap-3">
                            <div className="bg-surface-card p-1 rounded-lg border border-border-light flex items-center">
                                <Button
                                    variant={view === 'board' ? 'secondary' : 'ghost'}
                                    size="sm"
                                    onClick={() => setView('board')}
                                    className="h-8 w-8 p-0"
                                >
                                    <LayoutGrid className="h-4 w-4" />
                                </Button>
                                <Button
                                    variant={view === 'list' ? 'secondary' : 'ghost'}
                                    size="sm"
                                    onClick={() => setView('list')}
                                    className="h-8 w-8 p-0"
                                >
                                    <ListIcon className="h-4 w-4" />
                                </Button>
                            </div>
                            <Button className="gap-2 bg-accent hover:bg-accent-hover text-white">
                                <Plus className="h-4 w-4" />
                                Add Task
                            </Button>
                        </div>
                    </div>

                    <TaskFilters
                        searchQuery={searchQuery}
                        onSearchChange={setSearchQuery}
                        priorityFilter={priorityFilter}
                        onPriorityChange={setPriorityFilter}
                        statusFilter={statusFilter}
                        onStatusChange={setStatusFilter}
                        onClearFilters={handleClearFilters}
                    />
                </div>

                <div className="flex-1 overflow-hidden px-6 pb-6">
                    {view === 'board' ? (
                        <TaskKanban tasks={filteredTasks} onTaskClick={handleTaskClick} />
                    ) : (
                        <div className="h-full overflow-y-auto pr-2 scrollbar-thin">
                            <TaskList tasks={filteredTasks} onTaskClick={handleTaskClick} />
                        </div>
                    )}
                </div>
            </div>
        </AppShell>
    );
}
