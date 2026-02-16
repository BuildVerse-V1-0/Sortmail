import React, { useEffect } from 'react';
import gsap from 'gsap';
import { Clock, TrendingUp, BarChart, Tag, Mail } from 'lucide-react';

const StatsView: React.FC = () => {
    useEffect(() => {
        // Staggered Bento Entrance
        gsap.from(".bento-item", {
            y: 30,
            opacity: 0,
            duration: 0.6,
            stagger: 0.1,
            ease: "power2.out"
        });

        // Animated Counter
        const counterObj = { val: 0 };
        gsap.to(counterObj, {
            val: 12.5,
            duration: 2,
            ease: "power2.out",
            onUpdate: () => {
                const el = document.getElementById('hours-saved');
                if (el) el.innerText = counterObj.val.toFixed(1);
            }
        });

        // Bar Chart Animation
        gsap.from(".stat-bar", {
            height: 0,
            duration: 1,
            stagger: 0.1,
            ease: "bounce.out"
        });

    }, []);

    const tags = ["Project Alpha", "Q3 Budget", "Hiring", "Design System", "Invoices", "Support", "Partnerships", "Legal"];

    return (
        <div className="h-full p-8 overflow-y-auto custom-scrollbar">
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-white mb-2">Insights & Analytics</h1>
                <p className="text-zinc-400">Weekly performance and email volume metrics.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 grid-rows-2 h-[600px]">

                {/* Time Saved - Animated Counter */}
                <div className="bento-item col-span-1 lg:col-span-2 row-span-1 bento-card p-8 flex flex-col justify-center relative overflow-hidden">
                    <div className="absolute top-0 right-0 p-8 opacity-5">
                        <Clock size={150} />
                    </div>
                    <div className="flex items-center gap-3 text-emerald-400 mb-2">
                        <Clock size={20} />
                        <span className="font-semibold uppercase tracking-wider">Time Saved This Week</span>
                    </div>
                    <div className="flex items-end gap-2">
                        <span id="hours-saved" className="text-7xl font-bold text-white tracking-tighter">0.0</span>
                        <span className="text-2xl text-zinc-500 mb-2 font-medium">Hours</span>
                    </div>
                    <p className="text-zinc-400 mt-4 text-sm max-w-xs">Based on average reading/writing speed vs. AI automation usage.</p>
                </div>

                {/* Email Volume - Bar Chart */}
                <div className="bento-item col-span-1 lg:col-span-2 row-span-1 bento-card p-6 flex flex-col">
                    <div className="flex justify-between items-center mb-6">
                        <div className="flex items-center gap-2 text-indigo-400">
                            <BarChart size={20} />
                            <span className="font-semibold uppercase tracking-wider">Email Volume</span>
                        </div>
                        <select className="bg-zinc-900 border border-zinc-700 text-xs rounded-lg px-2 py-1 text-zinc-400 focus:outline-none">
                            <option>This Week</option>
                        </select>
                    </div>
                    <div className="flex-1 flex items-end justify-between gap-2 px-2">
                        {[40, 65, 30, 85, 50, 20, 10].map((h, i) => (
                            <div key={i} className="flex flex-col items-center gap-2 w-full">
                                <div className="w-full bg-zinc-800 rounded-t-sm h-32 relative overflow-hidden">
                                    <div
                                        className="stat-bar absolute bottom-0 left-0 right-0 bg-indigo-500/80 hover:bg-indigo-400 transition-colors rounded-t-sm"
                                        style={{ height: `${h}%` }}
                                    />
                                </div>
                                <span className="text-[10px] text-zinc-500 uppercase">{['M', 'T', 'W', 'T', 'F', 'S', 'S'][i]}</span>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Common Topics - Word Cloud / Tag Group */}
                <div className="bento-item col-span-1 lg:col-span-2 row-span-1 bento-card p-6">
                    <div className="flex items-center gap-2 text-rose-400 mb-6">
                        <Tag size={20} />
                        <span className="font-semibold uppercase tracking-wider">Trending Topics</span>
                    </div>
                    <div className="flex flex-wrap gap-2">
                        {tags.map((tag, i) => (
                            <span
                                key={i}
                                className="px-3 py-1.5 bg-zinc-800/50 border border-zinc-700 text-zinc-300 rounded-full text-sm hover:border-zinc-500 hover:text-white transition-colors cursor-default"
                            >
                                #{tag}
                            </span>
                        ))}
                        <span className="px-3 py-1.5 border border-dashed border-zinc-700 text-zinc-500 rounded-full text-sm">+4 more</span>
                    </div>
                </div>

                {/* Drafts Automated */}
                <div className="bento-item col-span-1 row-span-1 bento-card p-6 flex flex-col justify-between">
                    <div className="flex items-center gap-2 text-amber-400">
                        <Mail size={20} />
                        <span className="font-semibold uppercase tracking-wider">Drafts</span>
                    </div>
                    <div>
                        <span className="text-5xl font-bold text-white">142</span>
                        <p className="text-zinc-500 text-sm mt-1">AI Drafts generated</p>
                    </div>
                    <div className="w-full bg-zinc-800 h-1.5 rounded-full overflow-hidden mt-2">
                        <div className="bg-amber-400 h-full w-[70%]" />
                    </div>
                </div>

                {/* Efficiency Score */}
                <div className="bento-item col-span-1 row-span-1 bento-card p-6 flex flex-col justify-between bg-gradient-to-br from-indigo-900/20 to-purple-900/20">
                    <div className="flex items-center gap-2 text-indigo-400">
                        <TrendingUp size={20} />
                        <span className="font-semibold uppercase tracking-wider">Efficiency</span>
                    </div>
                    <div>
                        <span className="text-5xl font-bold text-white">Top 5%</span>
                        <p className="text-zinc-400 text-sm mt-1">Compared to org average</p>
                    </div>
                </div>

            </div>
        </div>
    );
};

export default StatsView;
