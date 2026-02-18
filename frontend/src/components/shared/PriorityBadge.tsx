import React from "react";
import type { Priority, PriorityLevel } from "@/types/dashboard";

const PRIORITY_CLASSES: Record<Priority | PriorityLevel, string> = {
    urgent: "priority-urgent",
    high: "priority-high",
    medium: "priority-medium",
    low: "priority-low",
    // New mappings
    do_now: "priority-urgent",
    do_today: "priority-high",
    can_wait: "priority-low",
};

const PRIORITY_LABELS: Record<Priority | PriorityLevel, string> = {
    urgent: "Urgent",
    high: "High",
    medium: "Medium",
    low: "Low",
    // New labels
    do_now: "Do Now",
    do_today: "Do Today",
    can_wait: "Can Wait",
};

interface PriorityBadgeProps {
    priority: Priority | PriorityLevel;
    className?: string;
}

export default function PriorityBadge({ priority, className = "" }: PriorityBadgeProps) {
    return (
        <span className={`priority-badge ${PRIORITY_CLASSES[priority]} ${className}`}>
            {PRIORITY_LABELS[priority]}
        </span>
    );
}
