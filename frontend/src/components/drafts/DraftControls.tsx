import React from 'react';
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Sparkles, Mail, Wand2 } from 'lucide-react';
import { mockThreads } from '@/data/mockData';
import { EmailThreadV1 } from '@/types/dashboard';

interface DraftControlsProps {
    selectedThreadId: string;
    onThreadChange: (threadId: string) => void;
    tone: string;
    onToneChange: (tone: string) => void;
    instructions: string;
    onInstructionsChange: (text: string) => void;
    isGenerating: boolean;
    onGenerate: () => void;
}

export function DraftControls({
    selectedThreadId,
    onThreadChange,
    tone,
    onToneChange,
    instructions,
    onInstructionsChange,
    isGenerating,
    onGenerate
}: DraftControlsProps) {
    return (
        <div className="flex flex-col gap-6 p-6 h-full border-r border-border-light bg-surface-card w-full md:w-[380px] shrink-0 overflow-y-auto">
            <div className="flex items-center gap-3 pb-4 border-b border-border-light">
                <div className="h-10 w-10 bg-ai/10 rounded-xl flex items-center justify-center text-ai">
                    <Wand2 className="h-5 w-5" />
                </div>
                <div>
                    <h2 className="font-display text-xl text-ink font-semibold">Draft Copilot</h2>
                    <p className="text-xs text-ink-light">AI-powered email replies</p>
                </div>
            </div>

            <div className="space-y-6">
                <div className="space-y-2">
                    <Label className="text-xs uppercase tracking-wider text-muted-foreground font-mono">Select Thread</Label>
                    <Select value={selectedThreadId} onValueChange={onThreadChange}>
                        <SelectTrigger className="w-full bg-paper border-border-light text-ink">
                            <SelectValue placeholder="Choose an email to reply to..." />
                        </SelectTrigger>
                        <SelectContent>
                            {mockThreads.map((thread: EmailThreadV1) => (
                                <SelectItem key={thread.thread_id} value={thread.thread_id}>
                                    <div className="flex flex-col gap-0.5 max-w-[300px]">
                                        <span className="truncate font-medium">{thread.subject}</span>
                                        <span className="truncate text-xs text-muted-foreground">
                                            {thread.participants[0]}
                                        </span>
                                    </div>
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </div>

                <div className="space-y-3">
                    <Label className="text-xs uppercase tracking-wider text-muted-foreground font-mono">Tone & Style</Label>
                    <RadioGroup value={tone} onValueChange={onToneChange} className="grid grid-cols-1 gap-2">
                        <label className={`flex items-center space-x-3 p-3 rounded-lg border cursor-pointer transition-all ${tone === 'brief' ? 'bg-paper border-primary/50 shadow-sm' : 'bg-transparent border-transparent hover:bg-paper-mid'}`}>
                            <RadioGroupItem value="brief" id="brief" />
                            <div className="flex flex-col">
                                <span className="text-sm font-medium text-ink">Brief & Direct</span>
                                <span className="text-xs text-muted-foreground">Short, to the point</span>
                            </div>
                        </label>
                        <label className={`flex items-center space-x-3 p-3 rounded-lg border cursor-pointer transition-all ${tone === 'normal' ? 'bg-paper border-primary/50 shadow-sm' : 'bg-transparent border-transparent hover:bg-paper-mid'}`}>
                            <RadioGroupItem value="normal" id="normal" />
                            <div className="flex flex-col">
                                <span className="text-sm font-medium text-ink">Professional</span>
                                <span className="text-xs text-muted-foreground">Standard business tone</span>
                            </div>
                        </label>
                        <label className={`flex items-center space-x-3 p-3 rounded-lg border cursor-pointer transition-all ${tone === 'formal' ? 'bg-paper border-primary/50 shadow-sm' : 'bg-transparent border-transparent hover:bg-paper-mid'}`}>
                            <RadioGroupItem value="formal" id="formal" />
                            <div className="flex flex-col">
                                <span className="text-sm font-medium text-ink">Formal & Polished</span>
                                <span className="text-xs text-muted-foreground">Respectful, detailed</span>
                            </div>
                        </label>
                    </RadioGroup>
                </div>

                <div className="space-y-2">
                    <Label className="text-xs uppercase tracking-wider text-muted-foreground font-mono">Instructions</Label>
                    <Textarea
                        placeholder="e.g. Mention that I'm OOO until Thursday..."
                        className="bg-paper min-h-[100px] text-sm resize-none border-border-light focus-visible:ring-ai"
                        value={instructions}
                        onChange={(e) => onInstructionsChange(e.target.value)}
                    />
                </div>

                <Button
                    className="w-full gap-2 bg-ai hover:bg-ai/90 text-white shadow-lg shadow-ai/20 transition-all font-medium py-6 rounded-xl"
                    onClick={onGenerate}
                    disabled={!selectedThreadId || isGenerating}
                >
                    {isGenerating ? (
                        <>
                            <Sparkles className="h-5 w-5 animate-spin" />
                            Writing Draft...
                        </>
                    ) : (
                        <>
                            <Sparkles className="h-5 w-5" />
                            Generate Draft
                        </>
                    )}
                </Button>
            </div>

            <div className="mt-auto pt-6 border-t border-border-light">
                <div className="bg-paper-mid/50 rounded-lg p-3 text-xs text-ink-light flex gap-2 border border-border-light">
                    <Mail className="h-4 w-4 shrink-0 text-muted-foreground" />
                    <p>Drafts are saved automatically to your database.</p>
                </div>
            </div>
        </div>
    );
}
