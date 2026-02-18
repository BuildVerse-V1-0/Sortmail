'use client';

import React, { useState, useEffect } from 'react';
import AppShell from '@/components/layout/AppShell';
import { DraftControls } from '@/components/drafts/DraftControls';
import { DraftEditor } from '@/components/drafts/DraftEditor';
import { useDrafts } from '@/hooks/useDrafts';
import { mockThreads } from '@/data/mockData';
import { EmailThreadV1 } from '@/types/dashboard';

export default function DraftsPage() {
    const [selectedThreadId, setSelectedThreadId] = useState<string>('');
    const [tone, setTone] = useState<string>('normal');
    const [customInstructions, setCustomInstructions] = useState('');
    const [generatedContent, setGeneratedContent] = useState('');
    const [isGenerating, setIsGenerating] = useState(false);

    // Fetch draft if a thread is selected
    const { data: activeDraft, isLoading } = useDrafts(selectedThreadId);

    // Effect to populate content when draft is loaded
    useEffect(() => {
        if (activeDraft) {
            setGeneratedContent(activeDraft.content);
            setTone(activeDraft.tone);
        } else {
            setGeneratedContent('');
        }
    }, [activeDraft]);

    const handleGenerate = async () => {
        if (!selectedThreadId) return;
        setIsGenerating(true);
        // Simulate API generation
        setTimeout(() => {
            const thread = mockThreads.find(t => t.thread_id === selectedThreadId);
            const newContent = `Hi ${thread?.participants[0] || 'there'},\n\nThis is a generated draft based on your instructions: "${customInstructions}"\n\nBest,\n[Your Name]`;
            setGeneratedContent(newContent);
            setIsGenerating(false);
        }, 1500);
    };

    const selectedThread = mockThreads.find((t: EmailThreadV1) => t.thread_id === selectedThreadId) || null;

    return (
        <AppShell title="Draft Copilot">
            <div className="flex flex-col lg:flex-row h-full">
                <DraftControls
                    selectedThreadId={selectedThreadId}
                    onThreadChange={setSelectedThreadId}
                    tone={tone}
                    onToneChange={setTone}
                    instructions={customInstructions}
                    onInstructionsChange={setCustomInstructions}
                    onGenerate={handleGenerate}
                    isGenerating={isGenerating}
                />
                <DraftEditor
                    content={generatedContent}
                    onUpdateContent={setGeneratedContent}
                    originalThread={selectedThread}
                    isGenerating={isGenerating}
                    onRegenerate={handleGenerate}
                    isLoading={isLoading}
                />
            </div>
        </AppShell>
    );
}
