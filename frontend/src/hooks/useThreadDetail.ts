import { useQuery } from '@tanstack/react-query';
import { api, endpoints } from '@/lib/api';
import { mockThreads, mockThreadIntel, mockTasks, mockDraft } from '@/data/mockData';
import { EmailThreadV1, ThreadIntelV1, TaskDTOv1, DraftDTOv1 } from '@/types/dashboard';

const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK_DATA === 'true';

interface ThreadDetailData {
    thread: EmailThreadV1;
    intel: ThreadIntelV1 | null;
    tasks: TaskDTOv1[];
    draft: DraftDTOv1 | null;
}

export function useThreadDetail(threadId: string) {
    return useQuery({
        queryKey: ['thread', threadId],
        queryFn: async (): Promise<ThreadDetailData | null> => {
            if (!threadId) return null;

            if (USE_MOCK) {
                // Simulate network delay
                await new Promise(resolve => setTimeout(resolve, 600));

                const thread = mockThreads.find(t => t.thread_id === threadId);
                if (!thread) return null;

                const intel = mockThreadIntel[threadId] ?? null;
                const tasks = mockTasks.filter(t => t.thread_id === threadId);
                const draft = threadId === mockDraft.thread_id ? mockDraft : null;

                return { thread, intel, tasks, draft };
            }

            // Real API call (placeholder structure)
            const { data } = await api.get(`${endpoints.threads}/${threadId}`);
            return data;
        },
        enabled: !!threadId,
        staleTime: 1000 * 60 * 5, // 5 minutes
    });
}
