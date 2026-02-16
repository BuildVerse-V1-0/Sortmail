
import React, { useEffect, useRef } from 'react';
import { Email, Urgency } from '@/types/dashboard';
import { AlertCircle, Clock, CheckCircle2, Zap, ArrowRight, CornerUpLeft, Sparkles } from 'lucide-react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

interface PriorityListProps {
    emails: Email[];
    onOpenAction: (email: Email) => void;
}

const PriorityList: React.FC<PriorityListProps> = ({ emails, onOpenAction }) => {
    const containerRef = useRef<HTMLDivElement>(null);
    const scanLineRef = useRef<HTMLDivElement>(null);

    // Filter for high/medium priority predominantly
    const sortedEmails = [...emails].sort((a, b) => {
        const urgencyMap = { [Urgency.HIGH]: 3, [Urgency.MEDIUM]: 2, [Urgency.LOW]: 1 };
        return urgencyMap[b.urgency] - urgencyMap[a.urgency];
    });

    useEffect(() => {
        // Pulse/Scan effect
        const scanTl = gsap.timeline({ repeat: -1, repeatDelay: 5 });
        scanTl.fromTo(scanLineRef.current,
            { top: '-20%', opacity: 0 },
            { top: '120%', opacity: 0.5, duration: 2.5, ease: "power1.inOut" }
        );

        // ScrollTrigger Reveal
        const ctx = gsap.context(() => {
            const cards = gsap.utils.toArray('.priority-card');
            gsap.set(cards, { y: 50, opacity: 0 });

            ScrollTrigger.batch(cards as Element[], {
                onEnter: batch => gsap.to(batch, { y: 0, opacity: 1, stagger: 0.05, duration: 0.3, ease: "power2.out" }),
                scroller: containerRef.current
            });
        }, containerRef);

        return () => ctx.revert();
    }, []);

    return (
        <div ref={containerRef} className="h-full relative overflow-y-auto custom-scrollbar p-8">
            {/* Scanning Line Overlay */}
            <div
                ref={scanLineRef}
                className="fixed left-20 lg:left-64 right-0 h-32 bg-gradient-to-b from-transparent via-indigo-500/10 to-transparent pointer-events-none z-0"
            />

            <div className="flex justify-between items-end mb-10 relative z-10">
                <div>
                    <h1 className="text-3xl font-bold text-white mb-2">Priority Action List</h1>
                    <p className="text-zinc-400">AI-sorted by urgency. {emails.filter(e => e.urgency === 'High').length} items require immediate attention.</p>
                </div>
                <button className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-medium transition-colors shadow-[0_0_15px_rgba(79,70,229,0.3)]">
                    <Zap size={16} /> Auto-Process Top 3
                </button>
            </div>

            <div className="space-y-6 max-w-4xl mx-auto relative z-10 pb-20">
                {sortedEmails.map((email) => (
                    <div
                        key={email.id}
                        className="priority-card glass-panel rounded-2xl p-6 group transition-all duration-300 hover:border-indigo-500/30 hover:bg-[#18181B]/80"
                    >
                        <div className="flex justify-between items-start mb-4">
                            <div className="flex items-center gap-4">
                                <div className="relative">
                                    <img src={email.avatar} alt={email.sender} className="w-12 h-12 rounded-full border border-zinc-600" />
                                    <div className={`absolute -bottom-1 -right-1 p-1 rounded-full border border-[#18181B] ${email.urgency === 'High' ? 'bg-rose-500 text-white' :
                                        email.urgency === 'Medium' ? 'bg-amber-500 text-black' : 'bg-emerald-500 text-white'
                                        }`}>
                                        {email.urgency === 'High' ? <AlertCircle size={10} /> : email.urgency === 'Medium' ? <Clock size={10} /> : <CheckCircle2 size={10} />}
                                    </div>
                                </div>
                                <div>
                                    <h3 className="text-lg font-semibold text-zinc-100">{email.subject}</h3>
                                    <p className="text-sm text-zinc-400">{email.sender} • {email.timestamp}</p>
                                </div>
                            </div>
                            <button
                                onClick={() => onOpenAction(email)}
                                className="px-4 py-2 bg-[#27272a] hover:bg-indigo-600 text-zinc-300 hover:text-white rounded-lg text-sm font-medium transition-all flex items-center gap-2 group-hover:translate-x-1"
                            >
                                Review <ArrowRight size={16} />
                            </button>
                        </div>

                        {/* AI TL;DR Section */}
                        <div className="bg-[#09090B]/50 rounded-xl p-4 border border-zinc-800 mb-4">
                            <div className="flex items-center gap-2 mb-2">
                                <Sparkles size={14} className="text-indigo-400" />
                                <span className="text-xs font-bold text-indigo-400 uppercase tracking-wide">AI Summary</span>
                            </div>
                            <p className="text-zinc-300 text-sm leading-relaxed">
                                {email.aiTldr || email.preview}
                            </p>
                        </div>

                        <div className="flex items-center gap-3">
                            <button
                                onClick={() => onOpenAction(email)}
                                className="text-xs flex items-center gap-1.5 text-zinc-500 hover:text-zinc-300 transition-colors"
                            >
                                <CornerUpLeft size={14} /> Quick Reply
                            </button>
                            <span className="text-zinc-700">|</span>
                            <button className="text-xs text-zinc-500 hover:text-zinc-300 transition-colors">
                                Snooze 1h
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default PriorityList;
