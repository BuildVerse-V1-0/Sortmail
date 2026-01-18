"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { clsx } from "clsx";

const navigation = [
    { name: "Dashboard", href: "/dashboard", icon: "📊" },
    { name: "Tasks", href: "/dashboard/tasks", icon: "✅" },
    { name: "Threads", href: "/dashboard/threads", icon: "📧" },
    { name: "Waiting For", href: "/dashboard/waiting", icon: "⏳" },
    { name: "Settings", href: "/dashboard/settings", icon: "⚙️" },
];

export function Sidebar() {
    const pathname = usePathname();

    return (
        <aside className="w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700">
            <div className="p-4">
                <Link href="/dashboard" className="text-2xl font-bold text-primary-600">
                    SortMail
                </Link>
            </div>

            <nav className="mt-4 px-2">
                {navigation.map((item) => (
                    <Link
                        key={item.name}
                        href={item.href}
                        className={clsx(
                            "flex items-center gap-3 px-4 py-3 rounded-lg mb-1 transition-colors",
                            pathname === item.href
                                ? "bg-primary-50 text-primary-700 dark:bg-primary-900 dark:text-primary-200"
                                : "text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-700"
                        )}
                    >
                        <span>{item.icon}</span>
                        <span>{item.name}</span>
                    </Link>
                ))}
            </nav>

            <div className="absolute bottom-4 left-4 right-4">
                <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                        Connected to Gmail
                    </p>
                    <p className="text-sm font-medium truncate">user@example.com</p>
                </div>
            </div>
        </aside>
    );
}
