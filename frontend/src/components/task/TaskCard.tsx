import { clsx } from "clsx";

interface Task {
    id: string;
    title: string;
    priority: "do_now" | "do_today" | "can_wait";
    priorityScore: number;
    explanation: string;
    deadline: string | null;
    effort: "quick" | "deep_work";
}

export function TaskCard({ task }: { task: Task }) {
    const priorityStyles = {
        do_now: "priority-badge priority-do-now",
        do_today: "priority-badge priority-do-today",
        can_wait: "priority-badge priority-can-wait",
    };

    const priorityLabels = {
        do_now: "Do Now",
        do_today: "Do Today",
        can_wait: "Can Wait",
    };

    return (
        <div className="p-4 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-colors">
            <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                        <span className={priorityStyles[task.priority]}>
                            {priorityLabels[task.priority]}
                        </span>
                        {task.effort === "deep_work" && (
                            <span className="text-xs text-gray-500">🧠 Deep work</span>
                        )}
                    </div>

                    <h3 className="font-medium">{task.title}</h3>

                    <p className="text-sm text-gray-500 mt-1">{task.explanation}</p>
                </div>

                {task.deadline && (
                    <div className="text-right">
                        <p className="text-xs text-gray-500">Deadline</p>
                        <p className="text-sm font-medium">{task.deadline}</p>
                    </div>
                )}
            </div>
        </div>
    );
}
