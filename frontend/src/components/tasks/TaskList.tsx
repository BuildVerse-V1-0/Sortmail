import React from 'react';
import { TaskDTOv1 } from '@/types/dashboard';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import PriorityBadge from '@/components/shared/PriorityBadge';
import { AlertTriangle, ChevronRight, Mail, LayoutList } from 'lucide-react';

interface TaskListProps {
    tasks: TaskDTOv1[];
    onTaskClick: (taskId: string) => void;
}

const STATUS_BADGES: Record<string, { label: string; className: string }> = {
    pending: { label: 'To Do', className: 'bg-slate-100 text-slate-700 border-slate-200' },
    in_progress: { label: 'In Progress', className: 'bg-blue-50 text-blue-700 border-blue-200' },
    completed: { label: 'Done', className: 'bg-emerald-50 text-emerald-700 border-emerald-200' },
};

export function TaskList({ tasks, onTaskClick }: TaskListProps) {
    if (tasks.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center py-16 text-muted-foreground bg-surface-card rounded-xl border border-dashed border-border-light">
                <LayoutList className="h-12 w-12 opacity-20 mb-4" />
                <p className="font-display text-lg opacity-60">No tasks found</p>
                <p className="text-sm opacity-50">Try adjusting your filters</p>
            </div>
        );
    }

    return (
        <div className="flex flex-col gap-2">
            {tasks.map((task) => (
                <Card
                    key={task.task_id}
                    className="cursor-pointer hover:shadow-md transition-all duration-200 group border-l-4"
                    style={{ borderLeftColor: task.priority === 'do_now' ? 'var(--danger)' : 'transparent' }}
                    onClick={() => onTaskClick(task.task_id)}
                >
                    <CardContent className="p-4 flex items-center justify-between gap-4">
                        <div className="flex items-start gap-4 flex-1 min-w-0">
                            <div className="flex flex-col gap-2 shrink-0 w-28">
                                <PriorityBadge priority={task.priority} className="w-fit" />
                                <Badge variant="outline" className={`w-fit text-[10px] font-mono ${STATUS_BADGES[task.status]?.className || ''}`}>
                                    {STATUS_BADGES[task.status]?.label || task.status}
                                </Badge>
                            </div>

                            <div className="flex-1 min-w-0">
                                <h4 className="font-semibold text-ink leading-snug group-hover:text-primary transition-colors font-body text-[15px]">
                                    {task.title}
                                </h4>
                                <p className="text-sm text-ink-light truncate mt-1">
                                    {task.description}
                                </p>
                                <div className="flex items-center gap-3 mt-2 text-xs text-muted-foreground">
                                    {task.effort === 'deep_work' && (
                                        <span className="font-mono bg-paper-mid px-1.5 py-0.5 rounded text-[10px] uppercase tracking-wide font-medium">DEEP WORK</span>
                                    )}
                                    <span className="flex items-center gap-1.5 opacity-80">
                                        <Mail className="h-3 w-3" />
                                        Task via Email
                                    </span>
                                </div>
                            </div>
                        </div>

                        <div className="flex items-center gap-8 shrink-0 pl-4 border-l border-border-light/50 h-full">
                            <div className="text-right min-w-[100px]">
                                {task.deadline ? (
                                    <>
                                        <div className={`text-sm font-semibold font-mono flex items-center justify-end gap-1.5 ${new Date(task.deadline) < new Date() ? 'text-danger' : 'text-ink'}`}>
                                            {new Date(task.deadline) < new Date() && <AlertTriangle className="h-3.5 w-3.5" />}
                                            {new Date(task.deadline).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                                        </div>
                                        <div className="text-[10px] uppercase tracking-wider text-muted-foreground mt-0.5 font-medium">
                                            Deadline
                                        </div>
                                    </>
                                ) : (
                                    <span className="text-sm text-muted-foreground">—</span>
                                )}
                            </div>
                            <ChevronRight className="h-5 w-5 text-border-mid group-hover:text-primary transition-colors" />
                        </div>
                    </CardContent>
                </Card>
            ))}
        </div>
    );
}
