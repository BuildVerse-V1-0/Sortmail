import React from 'react';
import { TaskDTOv1 } from '@/types/dashboard';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import PriorityBadge from '@/components/shared/PriorityBadge';
import { Clock, AlertTriangle, CheckCircle2, Circle, ArrowRightCircle } from 'lucide-react';

interface TaskKanbanProps {
    tasks: TaskDTOv1[];
    onTaskClick: (taskId: string) => void;
}

function KanbanColumn({ title, tasks, icon: Icon, onTaskClick }: { title: string; tasks: TaskDTOv1[]; icon: React.ElementType; onTaskClick: (id: string) => void }) {
    return (
        <div className="flex-1 min-w-[300px] h-full flex flex-col gap-4">
            <div className="flex items-center justify-between px-1">
                <div className="flex items-center gap-2 font-display text-lg text-ink font-semibold">
                    <Icon className="h-5 w-5 text-muted-foreground" />
                    <h3>{title}</h3>
                </div>
                <Badge variant="secondary" className="px-2 py-0.5 text-xs font-mono">
                    {tasks.length}
                </Badge>
            </div>

            <div className="flex flex-col gap-3 overflow-y-auto pr-2 pb-4 scrollbar-thin flex-1 bg-surface/30 rounded-xl p-3 border border-border/50">
                {tasks.map((task) => (
                    <Card
                        key={task.task_id}
                        className="cursor-pointer hover:shadow-md transition-all duration-200 border-l-4 group"
                        style={{ borderLeftColor: task.priority === 'do_now' ? 'var(--danger)' : 'transparent' }}
                        onClick={() => onTaskClick(task.task_id)}
                    >
                        <CardContent className="p-4 space-y-3">
                            <div className="flex justify-between items-start gap-2">
                                <PriorityBadge priority={task.priority} />
                                {task.effort === 'deep_work' && (
                                    <span className="text-[10px] uppercase font-mono font-medium text-muted-foreground bg-paper-mid px-1.5 py-0.5 rounded tracking-wider">
                                        Deep Work
                                    </span>
                                )}
                            </div>

                            <div>
                                <h4 className="font-semibold text-[15px] text-ink leading-snug line-clamp-2 group-hover:text-primary transition-colors font-body">
                                    {task.title}
                                </h4>
                                <p className="text-xs text-ink-light mt-1.5 line-clamp-2 leading-relaxed">
                                    {task.description}
                                </p>
                            </div>

                            <div className="flex items-center justify-between text-xs text-muted-foreground pt-3 border-t border-border-light">
                                <div className="flex items-center gap-1.5 font-medium">
                                    {task.deadline ? (
                                        <>
                                            <Clock className="h-3.5 w-3.5" />
                                            <span className={new Date(task.deadline) < new Date() ? 'text-danger' : ''}>
                                                {new Date(task.deadline).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                                            </span>
                                        </>
                                    ) : (
                                        <span className="opacity-50">No deadline</span>
                                    )}
                                </div>
                                {task.deadline && new Date(task.deadline) < new Date() && (
                                    <span className="text-danger font-bold flex items-center gap-1 text-[10px] uppercase tracking-wide">
                                        <AlertTriangle className="h-3 w-3" />
                                        Overdue
                                    </span>
                                )}
                            </div>
                        </CardContent>
                    </Card>
                ))}
                {tasks.length === 0 && (
                    <div className="h-32 flex items-center justify-center text-muted-foreground text-sm italic border-2 border-dashed border-border-light rounded-lg bg-white/50">
                        No tasks
                    </div>
                )}
            </div>
        </div>
    );
}

export function TaskKanban({ tasks, onTaskClick }: TaskKanbanProps) {
    const todoTasks = tasks.filter(t => t.status === 'pending');
    const inProgressTasks = tasks.filter(t => t.status === 'in_progress');
    const doneTasks = tasks.filter(t => t.status === 'completed');

    return (
        <div className="flex gap-6 overflow-x-auto pb-2 h-full">
            <KanbanColumn
                title="To Do"
                tasks={todoTasks}
                icon={Circle}
                onTaskClick={onTaskClick}
            />
            <KanbanColumn
                title="In Progress"
                tasks={inProgressTasks}
                icon={ArrowRightCircle}
                onTaskClick={onTaskClick}
            />
            <KanbanColumn
                title="Done"
                tasks={doneTasks}
                icon={CheckCircle2}
                onTaskClick={onTaskClick}
            />
        </div>
    );
}
