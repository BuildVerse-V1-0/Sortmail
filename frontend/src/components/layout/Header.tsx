"use client";

export function Header() {
    return (
        <header className="h-16 bg-card border-b border-border flex items-center justify-between px-6">
            <div className="flex items-center gap-4">
                <button className="btn-primary">
                    Sync Emails
                </button>
            </div>

            <div className="flex items-center gap-4">
                <span className="text-sm text-muted-foreground">Last sync: 5 min ago</span>
                <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                    <span className="text-sm font-medium text-primary">U</span>
                </div>
            </div>
        </header>
    );
}
