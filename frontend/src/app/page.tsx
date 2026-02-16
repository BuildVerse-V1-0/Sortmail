import Link from "next/link";

export default function Home() {
    return (
        <main className="min-h-screen bg-gradient-to-b from-gray-50 to-white dark:from-gray-900 dark:to-gray-800">
            {/* Hero Section */}
            <div className="max-w-6xl mx-auto px-4 py-20">
                <div className="text-center">
                    <h1 className="text-5xl font-bold text-gray-900 dark:text-white mb-6">
                        <span className="text-primary-600">Sort</span>Mail
                    </h1>

                    <p className="text-xl text-gray-600 dark:text-gray-300 mb-8 max-w-2xl mx-auto">
                        AI-powered intelligence layer for Gmail & Outlook.
                        Summarize threads, extract tasks, and draft replies — automatically.
                    </p>

                    <div className="flex gap-4 justify-center">
                        <Link
                            href="/login"
                            className="btn-primary text-lg px-8 py-3"
                        >
                            Get Started
                        </Link>
                        <a
                            href="#features"
                            className="btn-secondary text-lg px-8 py-3"
                        >
                            Learn More
                        </a>
                    </div>
                </div>

                {/* Features Grid */}
                <div id="features" className="mt-24 grid md:grid-cols-3 gap-8">
                    <FeatureCard
                        title="📧 Executive Briefings"
                        description="Get 2-3 sentence summaries of any email thread, instantly."
                    />
                    <FeatureCard
                        title="📎 Attachment Intelligence"
                        description="Automatically summarize PDFs, contracts, and documents."
                    />
                    <FeatureCard
                        title="✅ Smart Tasks"
                        description="Convert emails into prioritized tasks with deadlines."
                    />
                    <FeatureCard
                        title="📝 Draft Copilot"
                        description="Generate contextual replies with the right tone."
                    />
                    <FeatureCard
                        title="⏳ Follow-up Tracking"
                        description="Know exactly who owes you a response."
                    />
                    <FeatureCard
                        title="🔒 Privacy First"
                        description="Your data stays yours. Never sold, never shared."
                    />
                </div>
            </div>
        </main>
    );
}

function FeatureCard({ title, description }: { title: string; description: string }) {
    return (
        <div className="card p-6">
            <h3 className="text-lg font-semibold mb-2">{title}</h3>
            <p className="text-gray-600 dark:text-gray-400">{description}</p>
        </div>
    );
}
