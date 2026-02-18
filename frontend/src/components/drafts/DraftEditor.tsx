import React, { useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Copy, RefreshCw, ExternalLink, Check, AlertTriangle } from 'lucide-react';
import { EmailThreadV1 } from '@/types/dashboard';

interface DraftEditorProps {
    content: string;
    onUpdateContent: (text: string) => void;
    originalThread: EmailThreadV1 | null;
    isGenerating: boolean;
    onRegenerate: () => void;
    isLoading?: boolean;
}

export function DraftEditor({
    content,
    onUpdateContent,
    originalThread,
    isGenerating,
    onRegenerate,
    isLoading
}: DraftEditorProps) {
    const [copied, setCopied] = React.useState(false);
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    // Auto-resize textarea
    useEffect(() => {
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
            textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
        }
    }, [content]);

    const handleCopy = () => {
        navigator.clipboard.writeText(content);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    const recipient = originalThread ? originalThread.participants.find(p => p !== 'you@company.com') || 'Recipient' : 'Recipient';
    const subject = originalThread ? `Re: ${originalThread.subject}` : 'Subject';

    const placeholders = (content.match(/\[.*?\]/g) || []).length;

    return (
        <div className="flex flex-col h-full bg-paper relative">
            {isLoading && (
                <div className="absolute inset-0 z-10 bg-paper/50 backdrop-blur-sm flex items-center justify-center">
                    <div className="flex flex-col items-center gap-2">
                        <RefreshCw className="h-6 w-6 text-ai animate-spin" />
                        <p className="text-sm text-ai font-medium">Loading draft...</p>
                    </div>
                </div>
            )}
            {/* Toolbar */}
            <div className="px-10 py-6 border-b border-border-light bg-surface-card/30">
                <div className="grid gap-4 max-w-4xl mx-auto">
                    <div className="grid grid-cols-[80px_1fr] items-baseline gap-4">
                        <span className="text-sm font-medium text-ink-light text-right font-mono uppercase tracking-wide">To:</span>
                        <div className="flex items-center gap-2">
                            <Badge variant="secondary" className="font-mono font-medium text-ink bg-white border-border-light">
                                {recipient}
                            </Badge>
                        </div>
                    </div>
                    <div className="grid grid-cols-[80px_1fr] items-baseline gap-4">
                        <span className="text-sm font-medium text-ink-light text-right font-mono uppercase tracking-wide">Subject:</span>
                        <span className="text-base font-medium text-ink font-display tracking-wide">{subject}</span>
                    </div>
                </div>
            </div>

            {/* Editor Area */}
            <ScrollArea className="flex-1 bg-paper">
                <div className="px-10 py-10 max-w-4xl mx-auto min-h-[500px]">
                    {isGenerating ? (
                        <div className="space-y-4 animate-pulse max-w-2xl">
                            <div className="h-4 bg-muted/20 rounded w-3/4"></div>
                            <div className="h-4 bg-muted/20 rounded w-full"></div>
                            <div className="h-4 bg-muted/20 rounded w-5/6"></div>
                            <div className="h-4 bg-muted/20 rounded w-1/2"></div>
                        </div>
                    ) : content ? (
                        <Textarea
                            ref={textareaRef}
                            value={content}
                            onChange={(e) => onUpdateContent(e.target.value)}
                            className="min-h-[400px] border-none shadow-none focus-visible:ring-0 p-0 text-base leading-loose resize-none bg-transparent font-body text-ink"
                            placeholder="Draft will appear here..."
                            spellCheck={false}
                        />
                    ) : (
                        <div className="flex flex-col items-center justify-center h-64 text-muted-foreground border-2 border-dashed border-border-light rounded-2xl bg-surface-card/40 mx-auto max-w-2xl mt-12">
                            <p className="font-display text-lg text-ink/60">Ready to write?</p>
                            <p className="text-sm mt-1">Select an email thread to generate a draft.</p>
                        </div>
                    )}
                </div>
            </ScrollArea>

            {/* Action Bar */}
            <div className="border-t border-border-light bg-white/80 backdrop-blur-md p-4 sticky bottom-0 z-10">
                <div className="max-w-4xl mx-auto flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        {placeholders > 0 && (
                            <div className="flex items-center gap-2 text-warning text-xs font-semibold bg-warning/10 px-3 py-1.5 rounded-full border border-warning/20">
                                <AlertTriangle className="h-3.5 w-3.5" />
                                {placeholders} placeholder{placeholders !== 1 ? 's' : ''} detected
                            </div>
                        )}
                        <Button variant="ghost" size="sm" onClick={onRegenerate} disabled={!content || isGenerating} className="text-muted-foreground hover:text-ink">
                            <RefreshCw className={`h-4 w-4 mr-2 ${isGenerating ? 'animate-spin' : ''}`} />
                            Regenerate
                        </Button>
                    </div>

                    <div className="flex items-center gap-3">
                        <Button variant="outline" size="sm" onClick={handleCopy} disabled={!content} className="h-9">
                            {copied ? <Check className="h-4 w-4 mr-2" /> : <Copy className="h-4 w-4 mr-2" />}
                            {copied ? 'Copied' : 'Copy Text'}
                        </Button>
                        <Button variant="default" size="sm" className="bg-primary hover:bg-primary/90 text-white h-9 px-4 shadow-sm" disabled={!content}>
                            <ExternalLink className="h-4 w-4 mr-2" />
                            Open in Gmail
                        </Button>
                    </div>
                </div>
            </div>
        </div>
    );
}
