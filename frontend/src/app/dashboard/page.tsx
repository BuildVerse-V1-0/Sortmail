
"use client";

import React, { useState, useRef, useLayoutEffect } from 'react';
import Sidebar from '@/components/dashboard/Sidebar';
import DashboardView from '@/components/dashboard/DashboardView';
import PriorityList from '@/components/dashboard/PriorityList';
import StatsView from '@/components/dashboard/StatsView';
import WaitingView from '@/components/dashboard/WaitingView';
import IntelligencePanel from '@/components/dashboard/IntelligencePanel';
import { generateBriefing } from '@/services/geminiService';
import { View, Email, Task, Urgency } from '@/types/dashboard';
import gsap from 'gsap';

// Mock Data
const MOCK_EMAILS: Email[] = [
    {
        id: '1',
        sender: 'Sarah Connor',
        avatar: 'https://picsum.photos/id/64/100/100',
        subject: 'Project Skynet: Q3 Timeline Update',
        preview: 'We need to discuss the new timeline for the neural network deployment...',
        body: 'Hi Alex,\n\nWe need to discuss the new timeline for the neural network deployment. The current pace is concerning, and we might miss the Q3 deadline if we don\'t allocate more GPU resources immediately.\n\nCan we meet this Thursday to go over the budget?\n\nBest,\nSarah',
        timestamp: '10:42 AM',
        urgency: Urgency.HIGH,
        isRead: false,
        hasAttachment: true,
        attachments: [
            { id: 'att-1', name: 'Q3_Projections.pdf', type: 'pdf', size: '2.4 MB' },
            { id: 'att-2', name: 'Budget_Realloc.xlsx', type: 'sheet', size: '1.1 MB' }
        ],
        aiTldr: 'Urgent meeting request regarding Q3 timeline risks and GPU budget allocation.'
    },
    {
        id: '2',
        sender: 'Dwayne Johnson',
        avatar: 'https://picsum.photos/id/91/100/100',
        subject: 'Gym equipment invoice #4022',
        preview: 'Please find attached the invoice for the new office gym equipment...',
        body: 'Hey Alex,\n\nAttached is the invoice. Let me know when this gets processed.\n\nThanks,\nDJ',
        timestamp: 'Yesterday',
        urgency: Urgency.LOW,
        isRead: true,
        hasAttachment: true,
        aiTldr: 'Invoice attached for gym equipment. Needs processing.'
    },
    {
        id: '3',
        sender: 'Emily Blunt',
        avatar: 'https://picsum.photos/id/129/100/100',
        subject: 'Marketing Strategy Review',
        preview: 'Here are the draft concepts for the holiday campaign...',
        body: 'Hi Team,\n\nHere are the draft concepts for the holiday campaign. I think option B is the strongest because it aligns with our new brand voice.\n\nPlease review and provide feedback by EOD Friday.\n\nEmily',
        timestamp: 'Yesterday',
        urgency: Urgency.MEDIUM,
        isRead: false,
        hasAttachment: true,
        attachments: [
            { id: 'att-3', name: 'Winter_Glow_Hero.png', type: 'img', size: '4.2 MB' }
        ],
        aiTldr: 'Feedback required on Holiday Campaign concepts (Option B recommended) by Friday.'
    },
    {
        id: '4',
        sender: 'Cloud Provider',
        avatar: 'https://picsum.photos/id/15/100/100',
        subject: 'Your instance usage alert',
        preview: 'Usage for instance i-098234 has exceeded 80% CPU for 2 hours.',
        body: 'Alert: High CPU usage detected on production server cluster. Please investigate.',
        timestamp: '10:05 AM',
        urgency: Urgency.HIGH,
        isRead: false,
        aiTldr: 'CRITICAL: Production server high CPU usage alert.'
    }
];

export default function DashboardPage() {
    const [currentView, setCurrentView] = useState<View>(View.DASHBOARD);
    const [emails, setEmails] = useState<Email[]>(MOCK_EMAILS);
    const [selectedEmail, setSelectedEmail] = useState<Email | null>(null);
    const [briefing, setBriefing] = useState<string>('');

    const contentRef = useRef<HTMLDivElement>(null);

    // Initial Briefing Generation
    useLayoutEffect(() => {
        if (!briefing) {
            generateBriefing(emails).then(setBriefing);
        }
    }, []);

    const handleViewChange = (view: View) => {
        if (view !== currentView) {
            // Fade out/slide out current view
            gsap.to(contentRef.current, {
                opacity: 0,
                x: -10,
                duration: 0.15,
                ease: "power1.out",
                onComplete: () => {
                    setCurrentView(view);
                    setSelectedEmail(null);
                    // Fade in/slide in new view
                    gsap.fromTo(contentRef.current,
                        { opacity: 0, x: 10 },
                        { opacity: 1, x: 0, duration: 0.2, ease: "power1.out" }
                    );
                }
            });
        }
    };

    const handleAddTask = (task: Task) => {
        console.log("Task added:", task);
        // Logic to add task would go here
    };

    const renderContent = () => {
        switch (currentView) {
            case View.DASHBOARD:
                return <DashboardView emails={emails} briefingText={briefing} />;
            case View.PRIORITY:
                return <PriorityList emails={emails} onOpenAction={setSelectedEmail} />;
            case View.STATS:
                return <StatsView />;
            case View.WAITING:
                return <WaitingView />;
            default:
                return null;
        }
    };

    return (
        <div className="flex w-full h-screen bg-[#09090B] text-zinc-100 overflow-hidden font-sans selection:bg-indigo-500/30">

            <Sidebar
                currentView={currentView}
                onChangeView={handleViewChange}
            />

            <main className="flex-1 relative flex flex-col bg-[#09090B] overflow-hidden">
                {/* Glass Header for Mobile/aesthetic */}
                <header className="h-16 border-b border-[#27272a] bg-[#09090B]/80 backdrop-blur-md flex items-center px-8 justify-between z-10 sticky top-0">
                    <div className="text-zinc-400 text-sm font-medium tracking-wide">
                        Workspace / <span className="text-white">{currentView}</span>
                    </div>
                    <div className="flex items-center gap-4">
                        {/* Status removed */}
                    </div>
                </header>

                {/* View Content Container */}
                <div ref={contentRef} className="flex-1 relative overflow-hidden">
                    {renderContent()}
                </div>

                {/* Slide-over Intelligence Panel (Action Engine) */}
                {selectedEmail && (
                    <IntelligencePanel
                        email={selectedEmail}
                        onClose={() => setSelectedEmail(null)}
                        onAddTask={handleAddTask}
                    />
                )}
            </main>

            {/* Subtle Background Glows */}
            <div className="fixed top-0 left-64 w-[600px] h-[600px] bg-indigo-600/5 rounded-full blur-[120px] pointer-events-none z-0" />
            <div className="fixed bottom-0 right-0 w-[500px] h-[500px] bg-purple-600/5 rounded-full blur-[120px] pointer-events-none z-0" />
        </div>
    );
};
