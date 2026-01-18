import { TaskCard } from "@/components/task/TaskCard";

// Mock data - will be replaced with API call
const mockTasks = [
    {
        id: "task-001",
        title: "Reply to Sarah - Contract Review",
        priority: "do_now" as const,
        priorityScore: 85,
        explanation: "Key client + deadline Friday",
        deadline: "Friday EOD",
        effort: "quick" as const,
    },
    {
        id: "task-002",
        title: "Schedule call with investor",
        priority: "do_today" as const,
        priorityScore: 70,
        explanation: "Scheduling request pending",
        deadline: null,
        effort: "quick" as const,
    },
    {
        id: "task-003",
        title: "Review Q4 report attachment",
        priority: "can_wait" as const,
        priorityScore: 40,
        explanation: "FYI email, no action required",
        deadline: null,
        effort: "deep_work" as const,
    },
];

export function PriorityList() {
    return (
        <div className="card">
            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                <h2 className="text-lg font-semibold">Priority Tasks</h2>
            </div>

            <div className="divide-y divide-gray-200 dark:divide-gray-700">
                {mockTasks.map((task) => (
                    <TaskCard key={task.id} task={task} />
                ))}
            </div>

            {mockTasks.length === 0 && (
                <div className="p-8 text-center text-gray-500">
                    <p>No tasks yet. Sync your emails to get started.</p>
                </div>
            )}
        </div>
    );
}
