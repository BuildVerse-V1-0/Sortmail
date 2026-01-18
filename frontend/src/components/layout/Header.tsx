"use client";

export function Header() {
    return (
        <header className="h-16 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between px-6">
            <div className="flex items-center gap-4">
                <button className="btn-primary">
                    Sync Emails
                </button>
            </div>

            <div className="flex items-center gap-4">
                <span className="text-sm text-gray-500">Last sync: 5 min ago</span>
                <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center">
                    <span className="text-sm font-medium text-primary-700">U</span>
                </div>
            </div>
        </header>
    );
}
