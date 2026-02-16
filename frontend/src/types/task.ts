/**
 * Task Types
 * Matches backend TaskDTOv1 contract
 */

export type PriorityLevel = "do_now" | "do_today" | "can_wait";
export type EffortLevel = "quick" | "deep_work";
export type TaskStatus = "pending" | "in_progress" | "completed" | "dismissed";
export type TaskType = "reply" | "schedule" | "review" | "followup";

export interface Task {
    task_id: string;
    thread_id: string;
    user_id: string;
    title: string;
    description: string | null;
    task_type: TaskType;
    priority: PriorityLevel;
    priority_score: number;
    priority_explanation: string;
    effort: EffortLevel;
    deadline: string | null;
    deadline_source: string | null;
    status: TaskStatus;
    created_at: string;
    updated_at: string;
}
