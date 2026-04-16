'use client';

import { useState, useCallback } from 'react';
import { useThreadIntel } from './useThreadIntel';
import { getApiUrl } from '@/lib/config';

/**
 * Provides context-aware AI interactions for the current thread.
 * Manages local state for AI chat and contextual suggestions.
 */
export function useThreadContext(threadId: string) {
    const { data: intel, isLoading } = useThreadIntel(threadId);
    const [messages, setMessages] = useState<Array<{ role: 'user' | 'assistant', content: string }>>([]);
    const [isTyping, setIsTyping] = useState(false);

    const sendMessage = useCallback(async (content: string) => {
        if (!content.trim()) return;

        // Add user message
        setMessages(prev => [...prev, { role: 'user', content }]);
        setIsTyping(true);

        // Simulate AI response based on thread context
        try {
            const apiRes = await fetch(getApiUrl('/api/ai/chat'), {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    thread_id: threadId,
                    query: content,
                    options: { use_attachments: true },
                    history: messages.map(m => ({ role: m.role === 'user' ? 'user' : 'model', parts: [m.content] }))
                })
            });

            if (!apiRes.ok) throw new Error('Failed to connect to AI');

            // Add an empty assistant message to stream into
            setMessages(prev => [...prev, { role: 'assistant', content: '' }]);
            setIsTyping(false);

            const reader = apiRes.body?.getReader();
            const decoder = new TextDecoder();

            if (reader) {
                let done = false;
                while (!done) {
                    const { value, done: readerDone } = await reader.read();
                    done = readerDone;
                    if (value) {
                        const chunkStr = decoder.decode(value, { stream: true });
                        const lines = chunkStr.split('\n');
                        for (const line of lines) {
                            if (line.startsWith('data: ')) {
                                try {
                                    const data = JSON.parse(line.slice(5));
                                    if (data.token) {
                                        setMessages(prev => {
                                            const newMsgs = [...prev];
                                            const last = newMsgs[newMsgs.length - 1];
                                            last.content += data.token;
                                            return newMsgs;
                                        });
                                    }
                                } catch (e) {
                                    // ignore parse errors for split chunks
                                }
                            }
                        }
                    }
                }
            }
        } catch (error) {
            console.error('AI Chat Error:', error);
            setMessages(prev => [...prev, { role: 'assistant', content: "Sorry, I'm having trouble connecting to the AI intelligence layer right now." }]);
            setIsTyping(false);
        }
    }, [messages, threadId]);

    const clearChat = useCallback(() => {
        setMessages([]);
    }, []);

    return {
        intel,
        isLoading,
        messages,
        isTyping,
        sendMessage,
        clearChat
    };
}
