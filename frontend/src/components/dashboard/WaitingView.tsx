import React, { useState } from 'react';
import { WaitingItem } from '@/types/dashboard';
import { Clock, Send, CheckCircle, MoreHorizontal } from 'lucide-react';

const MOCK_WAITING: WaitingItem[] = [
    { id: 'w1', recipient: 'Sarah Connor', subject: 'Re: Budget Projections', sentDate: '2 days ago', daysPending: 2, avatar: 'https://picsum.photos/id/64/100/100' },
    { id: 'w2', recipient: 'Vendor Support', subject: 'Ticket #99281', sentDate: '5 days ago', daysPending: 5, avatar: 'https://picsum.photos/id/15/100/100' },
    { id: 'w3', recipient: 'Marketing Team', subject: 'Asset Request', sentDate: '1 week ago', daysPending: 7, avatar: 'https://picsum.photos/id/129/100/100' },
];

const WaitingView: React.FC = () => {
    const [items, setItems] = useState(MOCK_WAITING);
    const [nudgingId, setNudgingId] = useState<string | null>(null);

    const handleNudge = (id: string) => {
        setNudgingId(id);
        // Simulate AI Nudge generation
        setTimeout(() => {
            setNudgingId(null);
            alert("AI Nudge draft created and placed in drafts.");
        }, 1500);
    };

    return (
        <div className="h-full p-8 overflow-y-auto custom-scrollbar">
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-white mb-2">Waiting For</h1>
                <p className="text-zinc-400">Threads where you are awaiting a reply.</p>
            </div>

            <div className="space-y-4 max-w-3xl">
                {items.map((item) => (
                    <div key={item.id} className="glass-panel p-5 rounded-xl flex items-center justify-between group hover:bg-[#18181B]">
                        <div className="flex items-center gap-4">
                            <div className="relative">
                                <img src={item.avatar} alt={item.recipient} className="w-10 h-10 rounded-full grayscale opacity-70 group-hover:grayscale-0 group-hover:opacity-100 transition-all" />
                                <div className="absolute -bottom-1 -right-1 bg-zinc-900 rounded-full border border-zinc-700 p-0.5">
                                    <Clock size={12} className={item.daysPending > 4 ? "text-rose-500" : "text-amber-500"} />
                                </div>
                            </div>
                            <div>
                                <h3 className="font-semibold text-zinc-200">{item.recipient}</h3>
                                <p className="text-sm text-zinc-500">{item.subject}</p>
                            </div>
                        </div>

                        <div className="flex items-center gap-6">
                            <div className={`px-3 py-1 rounded-full text-xs font-medium border ${item.daysPending > 4
                                ? 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                                : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                                }`}>
                                {item.daysPending} days pending
                            </div>

                            <div className="flex gap-2">
                                <button
                                    onClick={() => handleNudge(item.id)}
                                    disabled={nudgingId === item.id}
                                    className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium rounded-lg flex items-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    {nudgingId === item.id ? (
                                        <>Generating...</>
                                    ) : (
                                        <><Send size={12} /> Nudge</>
                                    )}
                                </button>
                                <button className="p-1.5 text-zinc-500 hover:text-white rounded-lg hover:bg-zinc-800 transition-colors">
                                    <CheckCircle size={16} />
                                </button>
                            </div>
                        </div>
                    </div>
                ))}

                {items.length === 0 && (
                    <div className="text-center py-20 text-zinc-500">
                        No pending threads. You&apos;re all caught up!
                    </div>
                )}
            </div>
        </div>
    );
};

export default WaitingView;
