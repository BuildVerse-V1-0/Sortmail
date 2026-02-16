
import React, { useEffect } from 'react';
import gsap from 'gsap';
import { Sparkles, Activity, ArrowRight, Mail } from 'lucide-react';
import { Email } from '@/types/dashboard';

interface DashboardViewProps {
    emails: Email[];
    briefingText: string;
}

const DashboardView: React.FC<DashboardViewProps> = ({ emails, briefingText }) => {

    useEffect(() => {
        const tl = gsap.timeline();

        // Header
        tl.fromTo(".dash-header", { y: -20, opacity: 0 }, { y: 0, opacity: 1, duration: 0.4 });

        // Briefing Card
        tl.fromTo(".briefing-card",
            { y: 20, opacity: 0, scale: 0.95 },
            { y: 0, opacity: 1, scale: 1, duration: 0.4, ease: "power2.out" },
            "-=0.2"
        );

        // Bullet points reveal
        tl.fromTo(".briefing-point",
            { x: -10, opacity: 0 },
            { x: 0, opacity: 1, stagger: 0.05, duration: 0.3 },
            "-=0.1"
        );

        // Activity Feed
        tl.fromTo(".activity-item",
            { y: 10, opacity: 0 },
            { y: 0, opacity: 1, stagger: 0.05, duration: 0.3 },
            "-=0.2"
        );
    }, []);

    const recentActivity = emails.slice(0, 4);
    const briefingPoints = briefingText ? briefingText.split('\n').filter(l => l.trim().length > 0).slice(0, 3) : ["Generating insights...", "Analyzing priorities..."];

    return (
        <div className="h-full p-8 overflow-y-auto custom-scrollbar">
            <div className="dash-header mb-8">
                <h1 className="text-3xl font-bold text-white mb-2">Good Morning, Alex</h1>
                <p className="text-zinc-400">Here is what is happening in your inbox today.</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Executive Briefing Card */}
                <div className="col-span-2 briefing-card relative group">
                    <div className="absolute -inset-0.5 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-2xl opacity-20 group-hover:opacity-40 transition duration-500 blur"></div>
                    <div className="relative h-full bg-[#18181B] border border-[#27272a] rounded-xl p-8 overflow-hidden">
                        <div className="absolute top-0 right-0 p-4 opacity-10">
                            <Sparkles size={120} className="text-indigo-500" />
                        </div>

                        <div className="flex items-center gap-2 mb-6 text-indigo-400">
                            <Sparkles size={20} />
                            <span className="font-semibold uppercase tracking-wider text-xs">Daily Executive Briefing</span>
                        </div>

                        <div className="space-y-4">
                            {briefingPoints.map((point, i) => (
                                <div key={i} className="briefing-point flex gap-3 items-start">
                                    <div className="mt-2.5 w-1.5 h-1.5 rounded-full bg-indigo-500 shrink-0 shadow-[0_0_8px_rgba(99,102,241,0.6)]" />
                                    <p className="text-zinc-200 text-lg leading-relaxed font-normal">{point.replace(/^[-*]\s/, '')}</p>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Quick Actions / Side Stats */}
                <div className="col-span-1 space-y-4">
                    <div className="briefing-card bg-[#18181B] border border-[#27272a] rounded-xl p-6 flex flex-col items-center justify-center text-center h-[180px]">
                        <div className="w-12 h-12 rounded-full bg-emerald-500/10 flex items-center justify-center mb-3">
                            <Mail size={24} className="text-emerald-500" />
                        </div>
                        <span className="text-4xl font-bold text-white mb-1">{emails.length}</span>
                        <span className="text-sm text-zinc-500">Unread Emails</span>
                    </div>

                    <div className="briefing-card bg-indigo-600 rounded-xl p-6 flex flex-col justify-between h-[180px] relative overflow-hidden group cursor-pointer">
                        <div className="relative z-10">
                            <h3 className="text-white font-bold text-lg mb-1">Process Priority</h3>
                            <p className="text-indigo-200 text-sm">3 High Urgency items</p>
                        </div>
                        <div className="relative z-10 flex items-center gap-2 text-white font-medium">
                            Start Mode <ArrowRight size={16} />
                        </div>
                        <div className="absolute -right-4 -bottom-4 bg-white/10 w-24 h-24 rounded-full group-hover:scale-150 transition-transform duration-500" />
                    </div>
                </div>
            </div>

            {/* Recent Activity Feed */}
            <div className="mt-10">
                <div className="flex items-center gap-2 mb-6 text-zinc-400">
                    <Activity size={18} />
                    <h2 className="text-sm font-semibold uppercase tracking-wider">Recent Activity</h2>
                </div>

                <div className="space-y-3">
                    {recentActivity.map((email) => (
                        <div key={email.id} className="activity-item bg-[#18181B] border border-[#27272a] p-4 rounded-xl flex items-center justify-between hover:border-zinc-600 transition-colors cursor-pointer group">
                            <div className="flex items-center gap-4">
                                <img src={email.avatar} alt={email.sender} className="w-10 h-10 rounded-full border border-zinc-700" />
                                <div>
                                    <h4 className="text-zinc-200 font-medium group-hover:text-indigo-300 transition-colors">{email.subject}</h4>
                                    <p className="text-zinc-500 text-sm">Analyzed from {email.sender}</p>
                                </div>
                            </div>
                            <div className="text-right">
                                <span className={`text-xs px-2 py-1 rounded-full ${email.urgency === 'High' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' :
                                    'bg-zinc-800 text-zinc-400'
                                    }`}>
                                    {email.urgency} Priority
                                </span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default DashboardView;
