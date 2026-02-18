
import React, { useState, useEffect, useRef, useLayoutEffect } from 'react';
import { LegacyEmail, LegacyTask } from '@/types/dashboard';
// gsap v3.14 types don't expose .fromTo/.to on default export — cast for IDE compat
// eslint-disable-next-line
import _gsap from 'gsap';
const gsap = _gsap as any;
import {
    Sparkles, X, CheckSquare, MessageSquare, Calendar,
    Send, RotateCw, Copy, FileText, Image, Table, File,
    Cpu, Layers, CornerDownRight
} from 'lucide-react';

interface IntelligencePanelProps {
    email: LegacyEmail | null;
    onClose: () => void;
    onAddTask: (task: LegacyTask) => void;
}

const IntelligencePanel: React.FC<IntelligencePanelProps> = ({ email, onClose, onAddTask }) => {
    const panelRef = useRef<HTMLDivElement>(null);
    const contentRef = useRef<HTMLDivElement>(null);

    const [loading, setLoading] = useState(false);
    const [analysis, setAnalysis] = useState<{ summary: string[], actionItems: string[] } | null>(null);
    const [draft, setDraft] = useState<string>('');
    const [activeTab, setActiveTab] = useState<'brief' | 'draft'>('brief');
    const [draftLoading, setDraftLoading] = useState(false);

    // Attachment Intelligence State
    const [activeAttachmentId, setActiveAttachmentId] = useState<string | null>(null);
    const [attachmentSummary, setAttachmentSummary] = useState<string>("");
    const [isReadingAttachment, setIsReadingAttachment] = useState(false);

    // Panel Entry/Exit Animation
    useEffect(() => {
        if (email) {
            gsap.fromTo(panelRef.current,
                { x: '100%', opacity: 0.5 },
                { x: '0%', opacity: 1, duration: 0.3, ease: "power3.out" }
            );
            // Reset state for new email
            setAnalysis(null);
            setDraft('');
            setActiveTab('brief');

            // Reset attachment state
            if (email.attachments && email.attachments.length > 0) {
                setActiveAttachmentId(email.attachments[0].id);
            } else {
                setActiveAttachmentId(null);
            }
            setAttachmentSummary("");

            // Start Analysis Simulation
            runAnalysisSimulation(email);
        }
    }, [email]);

    // Handle Attachment Switching & "Reading" Animation
    useEffect(() => {
        if (activeAttachmentId && email?.attachments) {
            const attachment = email.attachments.find(a => a.id === activeAttachmentId);
            if (attachment) {
                setIsReadingAttachment(true);
                setAttachmentSummary(""); // Clear previous text for typewriter effect

                // Animate the active card
                gsap.fromTo(`#att-card-${activeAttachmentId}`,
                    { boxShadow: "0 0 0px rgba(99, 102, 241, 0)" },
                    {
                        boxShadow: "0 0 15px rgba(99, 102, 241, 0.4)",
                        borderColor: "rgba(129, 140, 248, 0.5)",
                        duration: 0.4,
                        yoyo: true,
                        repeat: 1
                    }
                );

                // Simulate AI Processing time then trigger Typewriter
                setTimeout(() => {
                    setIsReadingAttachment(false);
                    // Mock data based on file type for demo
                    const mockSummary = attachment.type === 'pdf'
                        ? "This document outlines the Q3 financial projections with a focus on GPU expenditure. It highlights a 15% variance in the original budget due to supply chain constraints. Recommended reallocation from the marketing budget to cover the deficit."
                        : attachment.type === 'img'
                            ? "Visual mockups for the 'Winter Glow' campaign. Contains 3 variants of the landing page hero section. Key visual elements include frost textures and neon accents consistent with the new brand guidelines."
                            : "Detailed line items for the provided service agreement. Total billable hours amount to 42.5 for the month of September. Includes breakdown of server maintenance and emergency downtime support.";

                    typewriteText(mockSummary);
                }, 600);
            }
        }
    }, [activeAttachmentId, email]);

    const typewriteText = (text: string) => {
        const obj = { length: 0 };
        gsap.to(obj, {
            length: text.length,
            duration: 1.5,
            ease: "none",
            onUpdate: () => {
                setAttachmentSummary(text.substring(0, Math.ceil(obj.length)));
            }
        });
    };

    // Stagger entrance for briefing details
    useLayoutEffect(() => {
        if (!isReadingAttachment && attachmentSummary.length > 5) {
            gsap.fromTo(".att-detail-item",
                { y: 15, opacity: 0 },
                { y: 0, opacity: 1, duration: 0.4, stagger: 0.1, ease: "back.out(1.2)" }
            );
        }
    }, [isReadingAttachment, attachmentSummary]);

    // Mock Analysis Simulation
    const runAnalysisSimulation = async (currentEmail: LegacyEmail) => {
        setLoading(true);
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 1500));
        setAnalysis({
            summary: [
                "User is requesting urgent review of Q3 goals.",
                "Requires approval for budget reallocation.",
                "Meeting requested for Thursday."
            ],
            actionItems: [
                "Review Q3 Goal Document",
                "Approve Budget Variance",
                "Schedule Meeting for Thursday"
            ]
        });
        setLoading(false);
    };

    // Reveal animation for main analysis content
    useEffect(() => {
        if (analysis && !loading) {
            gsap.fromTo(".reveal-item",
                { y: 10, opacity: 0 },
                { y: 0, opacity: 1, duration: 0.3, stagger: 0.05, ease: "power2.out" }
            );
        }
    }, [analysis, loading]);

    const handleCreateTask = (item: string) => {
        if (!email) return;
        const newTask: LegacyTask = {
            id: Date.now().toString(),
            title: item,
            description: '',
            sourceEmailId: email.id,
            status: 'todo'
        };
        onAddTask(newTask);
    };

    const handleDraft = async (tone: 'formal' | 'casual' | 'meeting') => {
        if (!email) return;
        setDraftLoading(true);
        setActiveTab('draft');
        // Simulate draft generation
        await new Promise(resolve => setTimeout(resolve, 1500));
        setDraft(`Hi ${email.sender.split(' ')[0]},\n\nThanks for reaching out about this. I've reviewed the attached documents and the Q3 projections look solid.\n\nLet's schedule a time to discuss the details. How does Thursday fast track?\n\nBest,\nUser`);
        setDraftLoading(false);
    };

    const getIconForType = (type: string) => {
        switch (type) {
            case 'img': return <Image size={16} className="text-purple-400" />;
            case 'sheet': return <Table size={16} className="text-emerald-400" />;
            case 'pdf': return <FileText size={16} className="text-rose-400" />;
            default: return <File size={16} className="text-blue-400" />;
        }
    };

    const getEntitiesForAttachment = () => {
        // Mock entities based on random logic for demo
        return [
            { label: 'Deadline', value: 'Oct 15', color: 'text-rose-400 border-rose-500/20 bg-rose-500/10' },
            { label: 'Value', value: '$12.5k', color: 'text-emerald-400 border-emerald-500/20 bg-emerald-500/10' },
            { label: 'Status', value: 'Pending', color: 'text-amber-400 border-amber-500/20 bg-amber-500/10' },
        ];
    };

    if (!email) return null;

    return (
        <div
            ref={panelRef}
            className="fixed right-0 top-0 bottom-0 w-full md:w-[480px] bg-[#09090B] border-l border-[#27272a] shadow-2xl z-30 flex flex-col"
        >
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-[#27272a] bg-[#09090B]/95 backdrop-blur z-10">
                <div className="flex items-center gap-2 text-indigo-400">
                    <Sparkles size={18} />
                    <span className="font-semibold text-sm tracking-wide uppercase">Intelligence Panel</span>
                </div>
                <button onClick={onClose} className="text-zinc-400 hover:text-white transition-colors">
                    <X size={20} />
                </button>
            </div>

            <div className="flex-1 overflow-y-auto custom-scrollbar" ref={contentRef}>

                {/* Original Email Context */}
                <div className="p-6 border-b border-[#27272a] bg-[#18181B]/50">
                    <h2 className="text-lg font-bold text-white mb-1 leading-tight">{email.subject}</h2>
                    <div className="flex items-center gap-2 mt-2">
                        <img src={email.avatar} className="w-6 h-6 rounded-full grayscale opacity-80" />
                        <span className="text-sm text-zinc-400">From <span className="text-zinc-200">{email.sender}</span></span>
                    </div>
                </div>

                {/* Attachment Intelligence Section */}
                {email.attachments && email.attachments.length > 0 && (
                    <div className="p-6 border-b border-[#27272a] bg-[#09090B] relative">
                        <div className="flex items-center gap-2 mb-4">
                            <Cpu size={16} className="text-indigo-500" />
                            <h3 className="text-xs font-bold text-zinc-300 uppercase tracking-wider">Attachment Intelligence</h3>
                        </div>

                        {/* File Selector */}
                        <div className="flex gap-3 overflow-x-auto pb-4 custom-scrollbar mb-4">
                            {email.attachments.map(att => (
                                <button
                                    key={att.id}
                                    id={`att-card-${att.id}`}
                                    onClick={() => setActiveAttachmentId(att.id)}
                                    className={`
                    flex items-center gap-3 p-3 rounded-lg border min-w-[160px] transition-all duration-300
                    ${activeAttachmentId === att.id
                                            ? 'bg-[#18181B] border-indigo-500/50'
                                            : 'bg-[#18181B]/40 border-[#27272a] hover:bg-[#18181B]'}
                  `}
                                >
                                    <div className={`p-2 rounded-md bg-[#09090B] border border-[#27272a] ${activeAttachmentId === att.id ? 'animate-pulse' : ''}`}>
                                        {getIconForType(att.type)}
                                    </div>
                                    <div className="text-left overflow-hidden">
                                        <p className="text-xs font-medium text-zinc-200 truncate w-24">{att.name}</p>
                                        <p className="text-[10px] text-zinc-500">{att.size}</p>
                                    </div>
                                </button>
                            ))}
                        </div>

                        {/* Active Briefing Area */}
                        <div className="bg-[#18181B]/30 border border-[#27272a] rounded-xl p-5 min-h-[180px] relative transition-all duration-500">
                            {isReadingAttachment ? (
                                <div className="flex flex-col items-center justify-center h-full py-8 space-y-3">
                                    <div className="w-8 h-8 rounded-full border-2 border-indigo-500/20 border-t-indigo-500 animate-spin" />
                                    <p className="text-xs text-indigo-400 font-mono animate-pulse">Scanning Document...</p>
                                </div>
                            ) : (
                                <>
                                    <div className="flex items-center justify-between mb-3">
                                        <div className="flex items-center gap-2">
                                            <Layers size={14} className="text-indigo-400" />
                                            <span className="text-xs font-bold text-indigo-300 uppercase tracking-widest">Deep Summary</span>
                                        </div>
                                        <span className="text-[10px] text-zinc-600 font-mono">AI-PROCESSED</span>
                                    </div>

                                    <p className="text-sm text-zinc-300 leading-relaxed font-light mb-6 min-h-[60px]">
                                        {attachmentSummary}
                                        <span className="inline-block w-1.5 h-4 bg-indigo-500 ml-1 animate-pulse align-middle" />
                                    </p>

                                    {/* Entity Highlights */}
                                    <div className="flex flex-wrap gap-2 mb-6">
                                        {getEntitiesForAttachment().map((ent, i) => (
                                            <div key={i} className={`att-detail-item px-3 py-1 rounded-full border text-[10px] font-medium flex items-center gap-2 ${ent.color}`}>
                                                <span className="opacity-70 uppercase tracking-wider">{ent.label}:</span>
                                                <span>{ent.value}</span>
                                            </div>
                                        ))}
                                    </div>

                                    <button
                                        onClick={() => handleDraft('formal')}
                                        className="att-detail-item w-full py-2 bg-[#27272a] hover:bg-indigo-600/20 hover:text-indigo-300 text-zinc-400 text-xs rounded-lg border border-[#27272a] hover:border-indigo-500/30 transition-all flex items-center justify-center gap-2"
                                    >
                                        <CornerDownRight size={14} />
                                        Draft reply using file context
                                    </button>
                                </>
                            )}
                        </div>
                    </div>
                )}

                {/* Tabs */}
                <div className="flex p-2 m-4 bg-[#18181B] rounded-lg border border-[#27272a]">
                    <button
                        onClick={() => setActiveTab('brief')}
                        className={`flex-1 py-2 text-sm font-medium rounded-md transition-all ${activeTab === 'brief' ? 'bg-[#27272a] text-white shadow-sm border border-zinc-700' : 'text-zinc-500 hover:text-zinc-300'}`}
                    >
                        Email Briefing
                    </button>
                    <button
                        onClick={() => setActiveTab('draft')}
                        className={`flex-1 py-2 text-sm font-medium rounded-md transition-all ${activeTab === 'draft' ? 'bg-[#27272a] text-white shadow-sm border border-zinc-700' : 'text-zinc-500 hover:text-zinc-300'}`}
                    >
                        Copilot
                    </button>
                </div>

                {/* Content Area */}
                <div className="px-6 pb-20">
                    {loading ? (
                        <div className="flex flex-col items-center justify-center py-20 space-y-4">
                            <div className="w-10 h-10 border-2 border-zinc-700 border-t-zinc-400 rounded-full animate-spin" />
                            <p className="text-zinc-500 text-xs animate-pulse">Analyzing context...</p>
                        </div>
                    ) : activeTab === 'brief' ? (
                        <div className="space-y-8">
                            {/* TL;DR Section */}
                            <div className="reveal-item">
                                <h3 className="text-xs font-bold text-zinc-500 uppercase tracking-wider mb-3">TL;DR Summary</h3>
                                <div className="bg-[#18181B] rounded-xl p-4 border border-[#27272a]">
                                    <ul className="space-y-3">
                                        {analysis?.summary?.map((point, i) => (
                                            <li key={i} className="flex gap-3 text-sm text-zinc-300 leading-relaxed">
                                                <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 mt-2 shrink-0" />
                                                {point}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            </div>

                            {/* Action Items Section */}
                            <div className="reveal-item">
                                <h3 className="text-xs font-bold text-zinc-500 uppercase tracking-wider mb-3">Suggested Actions</h3>
                                <div className="space-y-2">
                                    {analysis?.actionItems?.map((item, i) => (
                                        <div key={i} className="group flex items-start gap-3 p-3 rounded-lg bg-[#18181B] border border-[#27272a] hover:border-indigo-500/30 transition-colors">
                                            <div className="mt-0.5 p-1 rounded bg-[#27272a] text-zinc-400">
                                                <CheckSquare size={14} />
                                            </div>
                                            <p className="flex-1 text-sm text-zinc-300">{item}</p>
                                            <button
                                                onClick={() => handleCreateTask(item)}
                                                className="opacity-0 group-hover:opacity-100 px-3 py-1 bg-indigo-600 hover:bg-indigo-500 text-white text-xs rounded-md transition-all"
                                            >
                                                Add
                                            </button>
                                        </div>
                                    ))}
                                    {(!analysis?.actionItems || analysis.actionItems.length === 0) && (
                                        <p className="text-sm text-zinc-500 italic">No clear action items detected.</p>
                                    )}
                                </div>
                            </div>

                            <div className="reveal-item p-4 rounded-xl bg-gradient-to-br from-indigo-900/10 to-purple-900/10 border border-indigo-500/10">
                                <div className="flex gap-2 text-indigo-400 mb-2">
                                    <Sparkles size={16} />
                                    <span className="text-xs font-bold uppercase">AI Insight</span>
                                </div>
                                <p className="text-sm text-indigo-200/80">
                                    This email has {email.urgency.toLowerCase()} urgency.
                                    {email.urgency === 'High' ? " It requires immediate attention." : " You can probably deal with this later."}
                                </p>
                            </div>

                        </div>
                    ) : (
                        // Draft Mode
                        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                            <div className="grid grid-cols-3 gap-2">
                                <button onClick={() => handleDraft('formal')} className="p-2 bg-[#18181B] hover:bg-[#27272a] rounded-lg text-xs font-medium text-zinc-300 border border-[#27272a] flex flex-col items-center gap-1 transition-colors">
                                    <div className="p-1.5 bg-[#27272a] rounded-md"><MessageSquare size={14} /></div>
                                    Formal
                                </button>
                                <button onClick={() => handleDraft('casual')} className="p-2 bg-[#18181B] hover:bg-[#27272a] rounded-lg text-xs font-medium text-zinc-300 border border-[#27272a] flex flex-col items-center gap-1 transition-colors">
                                    <div className="p-1.5 bg-[#27272a] rounded-md"><MessageSquare size={14} /></div>
                                    Casual
                                </button>
                                <button onClick={() => handleDraft('meeting')} className="p-2 bg-[#18181B] hover:bg-[#27272a] rounded-lg text-xs font-medium text-zinc-300 border border-[#27272a] flex flex-col items-center gap-1 transition-colors">
                                    <div className="p-1.5 bg-[#27272a] rounded-md"><Calendar size={14} /></div>
                                    Meeting
                                </button>
                            </div>

                            {draftLoading ? (
                                <div className="h-48 rounded-xl bg-[#18181B] border border-[#27272a] animate-pulse flex items-center justify-center">
                                    <span className="text-zinc-500 text-sm">Drafting response...</span>
                                </div>
                            ) : (
                                <div className="relative">
                                    <textarea
                                        value={draft}
                                        onChange={(e) => setDraft(e.target.value)}
                                        placeholder="Select a style above or start typing..."
                                        className="w-full h-64 bg-[#09090B] border border-[#27272a] rounded-xl p-4 text-sm text-zinc-200 focus:outline-none focus:border-indigo-500/50 resize-none font-mono leading-relaxed"
                                    />
                                    <div className="absolute bottom-3 right-3 flex gap-2">
                                        <button className="p-2 text-zinc-500 hover:text-white hover:bg-[#18181B] rounded-lg transition-colors" title="Copy">
                                            <Copy size={16} />
                                        </button>
                                        <button className="p-2 text-zinc-500 hover:text-white hover:bg-[#18181B] rounded-lg transition-colors" title="Regenerate">
                                            <RotateCw size={16} />
                                        </button>
                                    </div>
                                </div>
                            )}

                            <div className="flex justify-end">
                                <button className="flex items-center gap-2 px-6 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg font-medium transition-all shadow-[0_0_15px_rgba(79,70,229,0.3)]">
                                    <Send size={16} />
                                    Send Reply
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default IntelligencePanel;
